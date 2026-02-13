# QR 코드 → 모바일 턴바이턴 길안내 구현 계획서

> **프로젝트**: 다이소 매장 내 상품 위치 안내 서비스  
> **작성일**: 2026-02-13  
> **버전**: v1.0

---

## 1. 개요

키오스크에서 검색한 상품의 네비게이션 결과를 **QR 코드**를 통해 모바일로 전송하고,  
모바일에서 **턴바이턴(Turn-by-Turn) 화살표 안내**로 실제 상품 위치까지 단계별로 안내하는 기능을 구현합니다.

### 전체 사용자 흐름

```
[키오스크]                              [모바일]
   │                                      │
   ├─ 1. 음성/텍스트 검색                  │
   ├─ 2. 상품 선택                        │
   ├─ 3. 경로 계산 + QR 코드 생성          │
   │      ┌──────────┐                    │
   │      │ QR Code  │ ──── 스캔 ────→    │
   │      └──────────┘                    ├─ 4. 모바일 브라우저 접속
   │                                      ├─ 5. 지도 + 경로 표시
   │                                      ├─ 6. 턴바이턴 화살표 안내
   │                                      └─ 7. 목적지 도착!
```

---

## 2. 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
│                                                             │
│  ┌──────────────┐    ┌─────────────────────────────────┐    │
│  │ 키오스크 모드  │    │ 모바일 모드                      │    │
│  │              │    │                                 │    │
│  │ /kioskmode/  │    │ /mobile/navigate?session={id}   │    │
│  │  results/    │    │                                 │    │
│  │              │    │ ┌──────────────────────────┐    │    │
│  │ ┌──────────┐│    │ │ MapNavigation 컴포넌트    │    │    │
│  │ │QR Code   ││    │ │ (지도 + 경로 렌더링)      │    │    │
│  │ │Generator ││    │ └──────────────────────────┘    │    │
│  │ └──────────┘│    │ ┌──────────────────────────┐    │    │
│  │              │    │ │ TurnByTurn 컴포넌트       │    │    │
│  │              │    │ │ (단계별 화살표 안내)       │    │    │
│  └──────┬───────┘    │ └──────────────────────────┘    │    │
│         │            └─────────────┬───────────────────┘    │
└─────────┼──────────────────────────┼────────────────────────┘
          │                          │
          ▼                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│                                                             │
│  POST /api/navigation/route     ← 경로 계산                 │
│  POST /api/navigation/session   ← 세션 저장 (QR용)          │
│  GET  /api/navigation/session/{id} ← 세션 조회 (모바일용)    │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 상세 구현 계획

### 3.1 백엔드: 네비게이션 세션 API

**파일**: `backend/api.py`

키오스크에서 계산된 네비게이션 결과를 임시 저장하고, 모바일에서 조회할 수 있는 API입니다.

#### 데이터 모델

```python
class NavSessionCreate(BaseModel):
    product_id: int
    product_name: str
    floor: str
    shelf: str              # 예: "B1-B03"
    path: list[Point]       # 경로 좌표 배열
    
class NavSessionResponse(BaseModel):
    session_id: str
    product_name: str
    floor: str
    shelf: str
    path: list[Point]
    steps: list[dict]       # 턴바이턴 안내 단계
    created_at: str
```

#### API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| `POST` | `/api/navigation/session` | 세션 저장 → `session_id` 반환 |
| `GET` | `/api/navigation/session/{session_id}` | 세션 조회 → 경로 + 안내 데이터 반환 |

#### 세션 저장소

```python
# 인메모리 저장 (프로토타입용, TTL 30분)
nav_sessions: dict[str, dict] = {}

@app.post("/api/navigation/session")
async def create_nav_session(req: NavSessionCreate):
    session_id = str(uuid.uuid4())[:8]
    
    # 턴바이턴 단계 서버에서 생성
    steps = generate_turn_by_turn_steps(req.path)
    
    nav_sessions[session_id] = {
        "product_name": req.product_name,
        "floor": req.floor,
        "shelf": req.shelf,
        "path": [{"x": p.x, "y": p.y} for p in req.path],
        "steps": steps,
        "created_at": datetime.now().isoformat(),
    }
    return {"session_id": session_id}

@app.get("/api/navigation/session/{session_id}")
async def get_nav_session(session_id: str):
    session = nav_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session expired or not found")
    return session
```

---

### 3.2 턴바이턴 경로 분석 알고리즘

**파일**: `backend/navigation/turn_by_turn.py` (신규)

경로 좌표 배열(`path[]`)을 분석하여 방향 전환점을 감지하고, 단계별 안내문을 생성합니다.

#### 핵심 알고리즘

```
입력: path = [{x:50,y:90}, {x:50,y:70}, {x:50,y:50}, {x:70,y:50}, {x:70,y:20}]

분석 과정:
  1. 연속된 두 점 사이의 이동 방향 계산
     (50,90)→(50,70): 방향 = "위" (y 감소)
     (50,70)→(50,50): 방향 = "위" (y 감소) — 같은 방향, 병합
     (50,50)→(70,50): 방향 = "오른쪽" (x 증가) — 방향 변경! 턴 포인트
     (70,50)→(70,20): 방향 = "위" (y 감소) — 방향 변경! 턴 포인트

  2. 이전 방향과 새 방향으로 회전 유형 결정
     "위" → "오른쪽" = 우회전
     "오른쪽" → "위" = 좌회전

출력:
  Step 1: ⬆️ 직진하세요 (약 12m)
  Step 2: ➡️ 우회전하세요
  Step 3: ⬆️ 직진하세요 (약 9m)
  Step 4: 🎯 목적지에 도착했습니다!
```

#### 구현 코드

```python
# backend/navigation/turn_by_turn.py

import math

def get_direction(from_pt, to_pt):
    """두 점 사이의 이동 방향 계산"""
    dx = to_pt["x"] - from_pt["x"]
    dy = to_pt["y"] - from_pt["y"]
    
    if abs(dx) > abs(dy):
        return "right" if dx > 0 else "left"
    else:
        return "down" if dy > 0 else "up"

def get_turn_type(prev_dir, next_dir):
    """이전 방향과 다음 방향으로 회전 유형 결정"""
    turn_map = {
        ("up", "right"): "turn_right",
        ("up", "left"): "turn_left",
        ("down", "right"): "turn_left",
        ("down", "left"): "turn_right",
        ("left", "up"): "turn_right",
        ("left", "down"): "turn_left",
        ("right", "up"): "turn_left",
        ("right", "down"): "turn_right",
    }
    return turn_map.get((prev_dir, next_dir), "straight")

def calculate_distance(p1, p2):
    """두 점 사이 거리 (% 단위 → 대략 미터 변환)"""
    dx = p1["x"] - p2["x"]
    dy = p1["y"] - p2["y"]
    percent_dist = math.sqrt(dx*dx + dy*dy)
    return round(percent_dist * 0.3)  # 1% ≈ 0.3m (매장 크기 기반 추정)

DIRECTION_LABELS = {
    "up": "앞으로", "down": "뒤로",
    "left": "왼쪽으로", "right": "오른쪽으로"
}

TURN_LABELS = {
    "turn_right": {"text": "우회전하세요", "icon": "➡️"},
    "turn_left": {"text": "좌회전하세요", "icon": "⬅️"},
}

def generate_turn_by_turn_steps(path: list[dict]) -> list[dict]:
    """경로 좌표 배열을 턴바이턴 안내 단계로 변환"""
    if len(path) < 2:
        return [{"step": 1, "instruction": "목적지 근처입니다!", "icon": "🎯"}]
    
    steps = []
    step_num = 1
    current_dir = get_direction(path[0], path[1])
    segment_start_idx = 0
    
    for i in range(1, len(path) - 1):
        next_dir = get_direction(path[i], path[i + 1])
        
        if next_dir != current_dir:
            # 직진 구간 추가
            dist = calculate_distance(path[segment_start_idx], path[i])
            steps.append({
                "step": step_num,
                "instruction": f"직진하세요 (약 {max(dist, 1)}m)",
                "icon": "⬆️",
                "direction": current_dir,
                "point_index": segment_start_idx,
                "distance_m": max(dist, 1),
            })
            step_num += 1
            
            # 회전 안내 추가
            turn = get_turn_type(current_dir, next_dir)
            turn_info = TURN_LABELS.get(turn, {"text": "방향을 바꾸세요", "icon": "🔄"})
            steps.append({
                "step": step_num,
                "instruction": turn_info["text"],
                "icon": turn_info["icon"],
                "direction": next_dir,
                "point_index": i,
                "distance_m": 0,
            })
            step_num += 1
            
            current_dir = next_dir
            segment_start_idx = i
    
    # 마지막 직진 구간
    dist = calculate_distance(path[segment_start_idx], path[-1])
    if dist > 0:
        steps.append({
            "step": step_num,
            "instruction": f"직진하세요 (약 {max(dist, 1)}m)",
            "icon": "⬆️",
            "direction": current_dir,
            "point_index": segment_start_idx,
            "distance_m": max(dist, 1),
        })
        step_num += 1
    
    # 도착
    steps.append({
        "step": step_num,
        "instruction": "목적지에 도착했습니다! 🎉",
        "icon": "🎯",
        "direction": "arrived",
        "point_index": len(path) - 1,
        "distance_m": 0,
    })
    
    return steps
```

---

### 3.3 키오스크: QR 코드 생성

**파일**: `frontend/src/app/kioskmode/results/page.tsx`

기존 QR placeholder를 실제 QR 코드 이미지로 교체합니다.

#### 변경 사항

```diff
 // 기존 (placeholder)
-<div className="w-32 h-32 bg-white border border-gray-300 rounded-lg mx-auto 
-     flex items-center justify-center">
-    <span className="text-gray-400 text-xs">QR Code</span>
-</div>

 // 변경 (실제 QR 코드)
+{qrDataUrl ? (
+    <img src={qrDataUrl} alt="QR Code" className="w-32 h-32 mx-auto rounded-lg" />
+) : selectedProduct ? (
+    <div className="w-32 h-32 bg-white border border-gray-300 rounded-lg mx-auto 
+         flex items-center justify-center">
+        <Loader2 className="w-6 h-6 text-gray-400 animate-spin" />
+    </div>
+) : (
+    <div className="w-32 h-32 bg-white border border-gray-300 rounded-lg mx-auto 
+         flex items-center justify-center">
+        <span className="text-gray-400 text-xs">상품을 선택하세요</span>
+    </div>
+)}
```

#### QR 생성 로직

```typescript
import QRCode from 'qrcode';

// 상품 선택 + 경로 데이터 준비 시 세션 생성
useEffect(() => {
    if (selectedProduct && navPath.length > 0) {
        createNavSession();
    }
}, [selectedProduct, navPath]);

const createNavSession = async () => {
    try {
        const res = await fetch(`${API_BASE_URL}/api/navigation/session`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_id: selectedProduct.id,
                product_name: selectedProduct.name,
                floor: navFloor,
                shelf: selectedProduct.location || '',
                path: navPath,
            }),
        });
        const { session_id } = await res.json();
        
        // 모바일 URL 생성 (같은 네트워크 IP 사용)
        const host = window.location.hostname;
        const mobileUrl = `http://${host}:3000/mobile/navigate?session=${session_id}`;
        
        // QR 이미지 생성
        const dataUrl = await QRCode.toDataURL(mobileUrl, {
            width: 200,
            margin: 2,
            color: { dark: '#000000', light: '#FFFFFF' },
        });
        setQrDataUrl(dataUrl);
    } catch (e) {
        console.error('Failed to create nav session:', e);
    }
};
```

---

### 3.4 모바일: 턴바이턴 길안내 페이지

**파일**: `frontend/src/app/mobile/navigate/page.tsx` (신규)

QR 코드를 스캔하면 이 페이지로 이동합니다.

#### 화면 구성

```
┌──────────────────────────────┐
│  ← 어디다이소                │  ← 헤더
├──────────────────────────────┤
│                              │
│  ┌────────────────────────┐  │
│  │                        │  │
│  │   [지도 이미지]          │  │  ← MapNavigation 컴포넌트
│  │   + 경로 빨간점선        │  │     (현재 구간 강조 표시)
│  │   + 현재 위치 마커       │  │
│  │                        │  │
│  └────────────────────────┘  │
│                              │
│  ┌────────────────────────┐  │
│  │  Step 2 / 5            │  │  ← 현재 단계 표시
│  │                        │  │
│  │  ➡️  우회전하세요       │  │  ← 큰 화살표 + 안내문
│  │                        │  │
│  │  다음: ⬆️ 직진 (약 3m) │  │  ← 다음 단계 미리보기
│  │                        │  │
│  │  [◀ 이전]    [다음 ▶]  │  │  ← 네비게이션 버튼
│  └────────────────────────┘  │
│                              │
│  ┌────────────────────────┐  │
│  │ 🧴 규조토 욕실매트      │  │  ← 상품 정보
│  │ B1층 · B03 선반        │  │
│  │ 약 30초 소요            │  │
│  └────────────────────────┘  │
└──────────────────────────────┘
```

#### 핵심 컴포넌트 구조

```typescript
// 주요 State
const [session, setSession] = useState(null);       // 세션 데이터
const [currentStep, setCurrentStep] = useState(0);  // 현재 안내 단계
const [steps, setSteps] = useState([]);             // 턴바이턴 단계 목록

// 세션 데이터 로드
useEffect(() => {
    const sessionId = searchParams.get('session');
    if (sessionId) loadSession(sessionId);
}, []);

// 단계 이동
const goNext = () => setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
const goPrev = () => setCurrentStep(prev => Math.max(prev - 1, 0));
```

#### 지도 위 현재 구간 강조

```typescript
// MapNavigation 컴포넌트에 현재 구간 경로만 전달
const currentSegmentPath = useMemo(() => {
    if (!steps[currentStep]) return path;
    const startIdx = steps[currentStep].point_index;
    const endIdx = steps[currentStep + 1]?.point_index ?? path.length - 1;
    return path.slice(startIdx, endIdx + 1);
}, [currentStep, steps, path]);
```

---

## 4. 파일 변경 목록

| 구분 | 파일 | 작업 |
|------|------|------|
| 백엔드 | `backend/api.py` | 세션 API 2개 추가 |
| 백엔드 | `backend/navigation/turn_by_turn.py` | **신규** — 턴바이턴 알고리즘 |
| 프론트 | `frontend/src/app/kioskmode/results/page.tsx` | QR 코드 실제 생성 |
| 프론트 | `frontend/src/app/mobile/navigate/page.tsx` | **신규** — 모바일 길안내 |
| 프론트 | `frontend/src/app/mobile/navigate/layout.tsx` | **신규** — 모바일 레이아웃 |

---

## 5. 턴바이턴 안내 동작 예시

### 입력 데이터 (경로 좌표)

```json
{
    "path": [
        {"x": 50, "y": 90},
        {"x": 50, "y": 80},
        {"x": 50, "y": 70},
        {"x": 50, "y": 50},
        {"x": 65, "y": 50},
        {"x": 70, "y": 50},
        {"x": 70, "y": 40},
        {"x": 70, "y": 30},
        {"x": 70, "y": 20}
    ],
    "floor": "B1"
}
```

### 출력 (턴바이턴 단계)

| Step | 아이콘 | 안내문 | 거리 |
|------|--------|--------|------|
| 1 | ⬆️ | 직진하세요 | 약 12m |
| 2 | ➡️ | 우회전하세요 | - |
| 3 | ⬆️ | 직진하세요 | 약 6m |
| 4 | ⬅️ | 좌회전하세요 | - |
| 5 | ⬆️ | 직진하세요 | 약 9m |
| 6 | 🎯 | 목적지에 도착했습니다! 🎉 | - |

---

## 6. 매장 환경 구성

### 필요 장비

| 항목 | 수량 | 비용 | 비고 |
|------|------|------|------|
| 키오스크 (태블릿/PC) | 1대 | 기존 보유 | 프론트엔드 실행 |
| 백엔드 서버 | 1대 | 기존 보유 | 같은 PC 가능 |
| WiFi 공유기 | 1대 | 기존 매장 WiFi | 키오스크 + 모바일 연결 |
| **추가 장비** | **없음** | **0원** | 턴바이턴 방식은 추가 장비 불필요 |

### 네트워크 구성

```
[매장 WiFi 공유기]
        │
    ┌───┴───┐
    │       │
[키오스크]  [사용자 모바일]
(서버+프론트)  (QR 스캔 후 접속)
    │
    └─ http://{IP}:3000  (프론트엔드)
    └─ http://{IP}:8000  (백엔드 API)
```

> **중요**: 키오스크와 사용자의 모바일이 **같은 WiFi 네트워크**에 연결되어 있어야 합니다.

### 사전 설정 작업

1. **매장 지도 이미지** 준비 (이미 완료 — `map_b1.jpg`, `map_b2.jpg`)
2. **네비게이션 그리드** 생성 (이미 완료 — `b1_grid.json`, `b2_grid.json`)
3. **존(Zone) 데이터** 등록 (이미 완료 — Admin Map Editor)
4. **상품 DB** 위치 좌표 입력 (이미 완료 — `location_x`, `location_y`)
5. **서버 IP 확인** → `ipconfig`으로 IPv4 주소 확인

---

## 7. 검증 방법

### 테스트 시나리오

```
1. 키오스크에서 "물티슈" 검색
2. 검색 결과에서 상품 선택
3. 좌측 하단에 QR 코드가 생성되는지 확인
4. 모바일 카메라로 QR 코드 스캔
5. 모바일 브라우저에 지도 + 경로가 표시되는지 확인
6. "다음" 버튼으로 턴바이턴 안내가 단계별로 진행되는지 확인
7. 마지막 단계에서 "도착!" 표시 확인
```

### 예상 소요 시간

| 작업 | 예상 시간 |
|------|-----------|
| 백엔드 세션 API | 30분 |
| 턴바이턴 알고리즘 | 30분 |
| 키오스크 QR 생성 | 30분 |
| 모바일 길안내 페이지 | 1시간 |
| 테스트 및 디버깅 | 30분 |
| **합계** | **약 3시간** |
