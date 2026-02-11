# 다이소 프론트엔드 구현 계획서

## 개요

다이소 "어디다있소" 키오스크 및 모바일 프론트엔드를 `front_v1.pen` UI 디자인과 `implementation_plan.md` 스펙에 기반하여 구현합니다. Next.js 14 (App Router), TailwindCSS, TypeScript를 사용합니다.

---

## 사용자 검토 필요 사항

> [!IMPORTANT]
> **기본 프로젝트 위치**: `frontend/bjy/` 폴더에 Next.js 14 스캐폴드가 이미 존재합니다.

> [!WARNING]
> **의존성 설치 필요**: zustand, lucide-react, framer-motion, qrcode 등 추가 패키지 설치가 필요합니다.

---

## 변경 사항

### Phase 1: 프로젝트 셋업 및 디자인 시스템

#### [수정] [package.json](file:///c:/Users/301/finalProject/daiso-category-search-merged-branch-by-bjy/frontend/bjy/package.json)
- 의존성 추가: `zustand`, `lucide-react`, `framer-motion`, `qrcode`, `clsx`, `tailwind-merge`

#### [신규] [tailwind.config.ts](file:///c:/Users/301/finalProject/daiso-category-search-merged-branch-by-bjy/frontend/bjy/tailwind.config.ts)
- 다이소 컬러 팔레트 설정 (`#E60012` 레드, 중립 톤)
- SUITE, Pretendard 폰트 패밀리 추가
- 커스텀 컴포넌트 크기 (80px 헤더, 60px 네비게이션)

#### [수정] [globals.css](file:///c:/Users/301/finalProject/daiso-category-search-merged-branch-by-bjy/frontend/bjy/src/app/globals.css)
- CSS 변수 정의: `--daiso-red`, `--daiso-gray` 등
- SUITE, Pretendard 폰트 임포트
- 다이소 브랜딩 기본 컴포넌트 스타일

---

### Phase 2: 공통 컴포넌트

#### [신규] [Header.tsx](file:///c:/Users/301/finalProject/daiso-category-search-merged-branch-by-bjy/frontend/bjy/src/components/shared/Header.tsx)
- 로고 + "어디다있소" 브랜딩 (40x40px 로고, 24px 텍스트)
- 시간 표시 및 WiFi 아이콘
- 높이 80px, 좌우 패딩 32px

#### [신규] [BottomNav.tsx](file:///c:/Users/301/finalProject/daiso-category-search-merged-branch-by-bjy/frontend/bjy/src/components/shared/BottomNav.tsx)
- 3개 네비 아이템: 검색, 매장지도, My/장바구니
- Lucide 아이콘, 높이 60px
- 활성 상태 레드 컬러

#### [신규] [Button.tsx](file:///c:/Users/301/finalProject/daiso-category-search-merged-branch-by-bjy/frontend/bjy/src/components/shared/Button.tsx)
- Primary (레드 채움), Secondary (테두리) 변형
- 높이 56px, 라운드 코너

#### [신규] [CategoryButton.tsx](file:///c:/Users/301/finalProject/daiso-category-search-merged-branch-by-bjy/frontend/bjy/src/components/shared/CategoryButton.tsx)
- 높이 44px 카테고리 필 버튼 (아이콘 포함)
- 활성/비활성 상태

---

### Phase 3: 키오스크 화면 (1280x800px)

#### [신규] [page.tsx - 음성 홈](file:///c:/Users/301/finalProject/daiso-category-search-merged-branch-by-bjy/frontend/bjy/src/app/kioskmode/page.tsx)
- 헤더 + 음성 검색 섹션 (80px 마이크 버튼, 700px 입력창)
- 캐러셀 섹션 (1100x300px 카드)
- 카테고리 바로가기 그리드 (4개: 홈, 카테고리, 매장지도, 고객센터)

#### [신규] [VoiceInput/page.tsx](file:///c:/Users/301/finalProject/daiso-category-search-merged-branch-by-bjy/frontend/bjy/src/app/kioskmode/voice/page.tsx)
- "듣고 있습니다..." 텍스트 (48px)
- 애니메이션 파형 바 (13개)
- 사용자 입력 표시 및 취소/확인 버튼

#### [신규] [SearchResults/page.tsx](file:///c:/Users/301/finalProject/daiso-category-search-merged-branch-by-bjy/frontend/bjy/src/app/kioskmode/results/page.tsx)
- 왼쪽 패널 (320px): 상품 카드 목록 + QR 코드
- 오른쪽 패널: B1/B2 층 지도 + 구역 마커
- 경로 시각화 및 현재 위치 표시

#### [신규] [CategoryMap/page.tsx](file:///c:/Users/301/finalProject/daiso-category-search-merged-branch-by-bjy/frontend/bjy/src/app/kioskmode/map/page.tsx)
- B1, B2 층 카드 나란히 배치
- 카테고리 사이드바 (140px) - 9개 카테고리
- 색상 코드별 구역 영역

#### [신규] [NotFound/page.tsx](file:///c:/Users/301/finalProject/daiso-category-search-merged-branch-by-bjy/frontend/bjy/src/app/kioskmode/not-found/page.tsx)
- 빈 상태 일러스트레이션
- 재검색 안내

---

### Phase 4: 모바일 화면 (390x844px)

#### [신규] [Mobile Layout](file:///c:/Users/301/finalProject/daiso-category-search-merged-branch-by-bjy/frontend/bjy/src/app/mobile/layout.tsx)
- 모바일 전용 뷰포트 및 스타일링

#### [신규] [MapNavigation/page.tsx](file:///c:/Users/301/finalProject/daiso-category-search-merged-branch-by-bjy/frontend/bjy/src/app/mobile/page.tsx)
- 헤더 (뒤로가기 버튼 + 로고)
- 지도 영역 (층 시각화)
- 바텀 시트 (200px) - 상품 정보 + 지도/AR 버튼

---

### Phase 5: 상태 관리 및 서비스

#### [신규] [searchStore.ts](file:///c:/Users/301/finalProject/daiso-category-search-merged-branch-by-bjy/frontend/bjy/src/store/searchStore.ts)
- Zustand 스토어: 검색 쿼리, 결과, 선택된 상품

#### [신규] [api.ts](file:///c:/Users/301/finalProject/daiso-category-search-merged-branch-by-bjy/frontend/bjy/src/lib/api.ts)
- API 클라이언트 (검색 엔드포인트)
- 백엔드 포트 8000 연동

---

## 구현 우선순위

| 우선순위 | 화면 | 복잡도 |
|---------|------|--------|
| 1 | 음성 홈 | 중간 |
| 2 | 검색 결과 | 높음 |
| 3 | 카테고리 지도 | 중간 |
| 4 | 모바일 지도 | 중간 |
| 5 | 음성 입력 | 낮음 |
| 6 | 결과 없음 | 낮음 |

---

## 검증 계획

### 개발 서버 테스트
```bash
cd frontend/bjy
npm install
npm run dev
# http://localhost:3000/kioskmode 접속
```

### 수동 검증 체크리스트

| 화면 | 테스트 항목 |
|-----|------------|
| 음성 홈 | 1. `/kioskmode` 이동 2. 1280x800 레이아웃 확인 3. 마이크 버튼 레드 컬러 확인 4. 카테고리 아이콘 클릭 |
| 검색 결과 | 1. `/kioskmode/results?q=샴푸` 이동 2. 왼쪽 패널 상품 표시 확인 3. B1/B2 지도 표시 확인 |
| 카테고리 지도 | 1. `/kioskmode/map` 이동 2. 카테고리 버튼 클릭 3. 구역 하이라이트 확인 |
| 모바일 | 1. `/mobile` 휴대폰 또는 브라우저 리사이즈로 확인 2. 390px 너비 확인 3. 바텀 시트 버튼 테스트 |

### 브라우저 테스트
- Chrome DevTools 디바이스 툴바 사용
- 키오스크: 1280x800 해상도 설정
- 모바일: iPhone 14 Pro (390x844) 설정

---

## 디자인 스펙 참조

| 요소 | 스펙 |
|-----|------|
| 주요 색상 | `#E60012` (다이소 레드) |
| 폰트 | SUITE (제목), Pretendard (본문) |
| 헤더 높이 | 80px (키오스크), 56px (모바일) |
| 하단 네비 | 60px |
| 코너 라운드 | 8px (버튼), 12px (카드), 24px (모달) |
| 그림자 | `0 4px 8px rgba(0,0,0,0.1)` |
