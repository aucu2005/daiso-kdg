# 카테고리 기반 실내 내비게이션 구현 가이드

맵 에디터에서 설정한 **구역(Zone)** 정보를 활용하여, 고객이 상품 검색 시 해당 구역으로 안내하는 내비게이션 기능을 구현하는 방법입니다.

## 1. 기본 원리

1.  **상품 검색**: 사용자가 상품(예: "새우깡")을 검색.
2.  **카테고리 매칭**: 검색 결과에서 상품의 카테고리(예: "식품")를 확인.
3.  **구역 조회**: 맵 에디터에서 생성한 구역 중 이름이 "식품"인 구역(Zone)을 찾음.
4.  **좌표 추출**: 해당 구역의 **중심점(Center Point)**을 계산.
5.  **경로 탐색**: 키오스크 위치(시작점) → 구역 중심점(도착점)으로 이어지는 경로 생성.
6.  **화면 표시**: 지도 위에 경로와 도착 마커를 그림.

---

## 2. 구현 단계 (Step-by-Step)

### 단계 1: 데이터 준비 (Backend)
이미 `/api/map/zones` API가 구현되어 있으므로, 프론트엔드에서 모든 구역 데이터를 미리 로드하거나 필요할 때 조회할 수 있습니다.

### 단계 2: 프론트엔드 - 구역 매칭 (Frontend)
`frontend/src/utils/mapUtils.ts` (신규 파일) 등을 생성하여 유틸리티 함수를 작성합니다.

```typescript
import { MapZone, Point } from '@/types/MapData'; // 타입 정의 필요

// 구역의 중심점 계산 함수
export function getZoneCenter(zone: MapZone): Point {
    if (Array.isArray(zone.rect)) {
        // 다각형(Polygon)인 경우: 모든 점의 평균 좌표 사용
        const points = zone.rect;
        const sum = points.reduce((acc, p) => ({ x: acc.x + p.x, y: acc.y + p.y }), { x: 0, y: 0 });
        return { x: sum.x / points.length, y: sum.y / points.length };
    } else {
        // 사각형(Rect)인 경우: 중심점 계산
        const r = zone.rect as any;
        const x = parseFloat(r.left) + parseFloat(r.width) / 2;
        const y = parseFloat(r.top) + parseFloat(r.height) / 2;
        return { x, y };
    }
}

// 카테고리 이름으로 구역 찾기
export function findZoneByCategory(zones: MapZone[], category: string): MapZone | undefined {
    // 1. 정확히 일치하는 이름 우선 검색
    const exact = zones.find(z => z.name === category);
    if (exact) return exact;

    // 2. 포함하는 이름 검색 (예: "문구/팬시" -> "문구")
    return zones.find(z => z.name.includes(category) || category.includes(z.name));
}
```

### 단계 3: 내비게이션 컴포넌트 (`MapNavigation.tsx`)
지도 위에 경로를 그리는 오버레이 컴포넌트를 만듭니다.

- **위치**: `frontend/src/components/MapNavigation.tsx`
- **기능**:
    -   `startPoint` (키오스크 위치, 고정값)와 `endPoint` (대상 구역 중심)를 받음.
    -   SVG `line` 또는 `path`로 연결선 그리기.
    -   도착 지점에 핀(Marker) 아이콘 표시.

```tsx
// 예시 코드
export default function MapNavigation({ zones, targetCategory }) {
    const kioskLocation = { x: 90, y: 90 }; // 키오스크 위치 (우측 하단 가정)
    
    // 타겟 구역 찾기
    const targetZone = findZoneByCategory(zones, targetCategory);
    if (!targetZone) return null;

    // 중심점 계산
    const center = getZoneCenter(targetZone);

    return (
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {/* 경로선 (점선) */}
            <line 
                x1={`${kioskLocation.x}%`} y1={`${kioskLocation.y}%`}
                x2={`${center.x}%`} y2={`${center.y}%`}
                stroke="#FF0000" strokeWidth="2" strokeDasharray="5,5"
                className="animate-dash" // CSS 애니메이션 추가 필요
            />
            
            {/* 도착 마커 */}
            <circle cx={`${center.x}%`} cy={`${center.y}%`} r="2" fill="red" />
            <text x={`${center.x}%`} y={`${center.y - 2}%`} fill="red" fontSize="0.8rem" textAnchor="middle" fontWeight="bold">
                {targetZone.name}
            </text>
            
            {/* 시작점(현위치) */}
            <circle cx={`${kioskLocation.x}%`} y={`${kioskLocation.y}%`} r="2" fill="blue" />
             <text x={`${kioskLocation.x}%`} y={`${kioskLocation.y + 4}%`} fill="blue" fontSize="0.8rem" textAnchor="middle" fontWeight="bold">
                현위치
            </text>
        </svg>
    );
}
```

### 단계 4: 검색 결과 페이지에 통합
검색 결과 페이지(예: `frontend/src/app/kioskmode/search/page.tsx` 또는 `results/page.tsx`)에서:

1.  `fetchMapZones()`로 전체 구역 정보를 로드합니다.
2.  검색된 상품의 `category_middle` (또는 `category_major`) 정보를 가져옵니다.
3.  `MapNavigation` 컴포넌트를 지도 이미지 위에 렌더링하고, `targetCategory`를 전달합니다.

---

## 3. 고급 기능 (Advanced)

### 장애물 회피 (A* Pathfinding)
단순 직선이 아니라, 벽을 피해 이동하려면 **노드 그래프(Node Graph)**가 필요합니다.
1.  **웨이포인트(Waypoint) 설정**: 맵 에디터에 '이동 가능 경로(Path Node)'를 찍는 모드를 추가합니다.
2.  **경로 탐색**: 시작점 -> 가장 가까운 노드 -> ... -> 도착점 주변 노드 -> 도착점 순서로 연결합니다.
3.  (현재 단계에서는 직선 연결로 시작하고, 복잡한 지형일 경우 꺾이는 지점을 하드코딩된 '경유지'로 추가하는 방식을 추천합니다.)
