# [설계서] 매장 내 실내 내비게이션 및 구역 관리 시스템

본 문서는 매장 안내 지도를 데이터화하여 카테고리별 구역을 설정하고, 장애물(벽, 매대)을 회피하는 최적 경로 안내 시스템의 기술적 사양을 다룹니다.

---

## 1. 기술 스택 (Tech Stack)

| 구분 | 기술 | 역할 |
| :--- | :--- | :--- |
| **Frontend** | **Next.js (App Router)** | 사용자 인터페이스, 지도 렌더링, 실시간 경로 시각화 |
| **Language** | **TypeScript** | 정적 타입을 통한 데이터 구조 안정성 확보 |
| **Backend** | **FastAPI (Python)** | 이미지 프로세싱, 경로 탐색 알고리즘 연산, API 제공 |
| **Library** | **Fabric.js** | HTML5 Canvas 기반의 인터랙티브 구역 설정 및 편집 |
| **Analysis** | **OpenCV / NetworkX** | 지도 이미지 이진화 처리 및 그래프 기반 최단 경로 계산 |
| **Database** | **MySQL** | 지도 메타데이터, 구역 좌표, 상품 위치 데이터 관리 |

---

## 2. 시스템 아키텍처 및 상세 프로세스

### 2.1. 지도 데이터화 (Map Digitization)
사용자가 업로드한 이미지를 시스템이 이해할 수 있는 좌표계로 변환합니다.
1. **이미지 이진화 (OpenCV):** 업로드된 평면도를 흑백으로 변환하여 벽(Black, 통과 불가)과 길(White, 통과 가능)을 구분합니다.
2. **그리드 맵 생성:** 지도를 일정 크기의 격자(Grid)로 분할하여 이동 가능 여부를 `0`과 `1`로 매핑한 행렬 데이터를 생성합니다.



### 2.2. 구역 설정 및 데이터 관리 (Spatial Mapping)
카테고리별 구역을 설정하고 DB에 저장합니다.
* **Polygon Mapping:** 관리자가 Next.js 환경에서 지도 위에 마우스 클릭으로 다각형 구역을 생성합니다. (Fabric.js 활용)
* **Data Structure:** 각 구역의 꼭짓점 좌표(`x, y`)와 카테고리 정보(예: 과자, 생필품 등)를 JSON 형태로 저장합니다.

### 2.3. 경로 탐색 엔진 (Pathfinding Engine)
벽과 매대를 통과하지 않는 최적의 길을 찾습니다.
* **A* (A-Star) 알고리즘:** 출발점부터 목적지까지의 추정 거리(Heuristic)를 계산하여 장애물을 피해가는 가장 빠른 경로를 도출합니다.
* **Graph Optimization:** 이동 가능한 통로 중앙을 따라 노드(Node)를 배치하여 자연스러운 보행 경로를 유도합니다.



---

## 3. 핵심 기능 인터페이스 (API & UI)

### 3.1. 경로 계산 API (FastAPI)
* **Endpoint:** `POST /api/v1/navigation/route`
* **Request:** `{ "start_pos": [x, y], "target_item": "item_id" }`
* **Response:** `{ "path": [[x1, y1], [x2, y2], ...], "distance": "15m" }`

### 3.2. 프론트엔드 시각화 (Next.js)
* **Canvas Layering:** 배경(지도 이미지) - 중간층(구역 폴리곤) - 상단층(경로 라인 및 애니메이션) 순으로 렌더링합니다.
* **Scale Calibration:** 이미지 원본 크기와 사용자 화면 크기 사이의 비율($Ratio$)을 계산하여 좌표를 정확히 매칭합니다.

---

## 4. 데이터베이스 엔티티 설계

```sql
-- 지도 정보
CREATE TABLE maps (
    id INT PRIMARY KEY AUTO_INCREMENT,
    image_url VARCHAR(255),
    pixel_width INT,
    pixel_height INT
);

-- 구역 정보 (JSON으로 좌표 저장)
CREATE TABLE zones (
    id INT PRIMARY KEY AUTO_INCREMENT,
    map_id INT,
    category_name VARCHAR(50),
    coordinates JSON -- 예: [[10,10], [50,10], [50,50], [10,50]]
);

-- 상품 위치 정보
CREATE TABLE items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    zone_id INT,
    name VARCHAR(100),
    location_x INT,
    location_y INT
);

5. 향후 확장성
실시간 위치 추적: Wi-Fi 지문(Fingerprinting)이나 BLE 비콘을 활용한 정밀 실내 측위 연동.

다층 지도 지원: 계단이나 엘리베이터 노드를 연결하여 층간 이동 경로 안내.

재고 연동: 상품 재고 유무에 따라 방문 우선순위를 조정하는 경로 최적화.