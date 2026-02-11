# 실내 내비게이션 구현 계획

## 개요
`document/map.md`에 기술된 실내 내비게이션 시스템을 `poc/bjy/poc/data/poc_v6_mock_product_db.json`의 더미 상품 데이터를 사용하여 구현합니다.

## 데이터 소스
- **상품 데이터**: `poc/bjy/poc/data/poc_v6_mock_product_db.json`
  - 포함 정보: `id`, `name`, `location` (매대 ID), `floor` (B1, B2).
- **지도 이미지**: 기존 `map_b1.jpg`, `map_b2.jpg`.

## 단계별 구현 (Phased Implementation)

### 1단계: 데이터 통합 설정 (Phase 1)
1.  **데이터베이스 마이그레이션**:
    -   `products.db`의 기존 `products` 테이블 스키마 확인.
    -   매대 ID(예: "C01", "BA01")를 실제 지도 좌표(`location_x`, `location_y`)로 매핑할 수 있도록 스키마 생성/수정.
    -   `poc_v6_mock_product_db.json` 데이터를 `products.db`에 적재(Seed)하는 스크립트 작성.

### 2단계: 지도 데이터화 (Backend) (Phase 2)
1.  **그리드 시스템 (Grid System)**:
    -   그리드 크기 정의 (예: 10px = 1 노드).
    -   **장애물 감지**:
        -   옵션 A (고급): OpenCV를 사용하여 `map_b1.jpg`/`map_b2.jpg`를 이진화하고 벽(검은색 픽셀)을 자동 감지.
        -   옵션 B (수동): 이미지 처리가 너무 노이즈가 많을 경우 "이동 가능 구역" 또는 "장애물"을 정의하는 도구/스크립트 생성.
    -   *결정*: 명세서에 따라 OpenCV 처리를 우선 시도.

2.  **노드 그래프 (Node Graph)**:
    -   그리드를 A* 경로 탐색을 위한 그래프로 변환.

### 3단계: 경로 탐색 엔진 (Backend) (Phase 3)
1.  **A* 알고리즘**:
    -   Python으로 `find_path(start_node, end_node, grid)` 구현.
    -   휴리스틱(Heuristic): 맨해튼(Manhattan) 또는 유클리드(Euclidean) 거리 사용.
    -   대각선 이동 허용 여부 (일반적으로 허용하되 비용을 약간 높게 설정).
2.  **API 엔드포인트**:
    -   `POST /api/navigation/route`
    -   입력: `{ start: {x, y, floor}, target_product_id: string }`
    -   출력: `{ path: [{x, y}, ...], distance: number }`

### 4단계: 프론트엔드 시각화 (Frontend) (Phase 4)
1.  **캔버스 오버레이 (Canvas Overlay)**:
    -   지도 이미지 위에 오버레이되는 `MapNavigation` 컴포넌트 구현.
    -   API에서 받은 경로(Poly-line) 그리기.
    -   시작/종료 마커 추가.
    -   애니메이션: 이동 방향으로 흐르는 점선 애니메이션 효과.

## 실행 단계 (Execution Steps)
1.  [ ] **데이터 로딩**: JSON 임포트를 위한 `backend/database/seed_products_v6.py` 생성.
2.  [ ] **지도 처리**: 그리드 생성을 위한 `backend/navigation/map_processor.py` 생성.
3.  [ ] **경로 탐색**: `backend/navigation/pathfinder.py` 생성.
4.  [ ] **API**: `backend/api.py`에 경로 탐색 엔드포인트 추가.
5.  [ ] **UI**: `frontend/src/components/MapNavigation.tsx` 생성.
