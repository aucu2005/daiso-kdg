# GitHub 업로드 가이드

현재 프로젝트(`daiso-category-search-dev-kdg`)를 GitHub에 업로드하는 단계별 방법입니다.

## 1. 사전 준비
*   **GitHub 계정**: [github.com](https://github.com)에서 계정이 필요합니다.
*   **Git 설치**: 컴퓨터에 Git이 설치되어 있어야 합니다.

## 2. GitHub 저장소(Repository) 생성
1.  GitHub 로그인 후, 오른쪽 상단의 `+` 아이콘을 클릭하고 **New repository**를 선택합니다.
2.  **Repository name**에 `daiso-store-navigation` (또는 원하는 이름)을 입력합니다.
3.  **Public** 또는 **Private**을 선택합니다.
4.  다른 옵션(README, .gitignore 추가 등)은 체크하지 말고 **Create repository** 버튼을 누릅니다.

## 3. 로컬 프로젝트 설정 및 업로드 (터미널에서 실행)

프로젝트 루트 폴더(`c:\Users\301\finalProject\daiso-category-search-dev-kdg`)에서 다음 명령어를 순서대로 실행하세요.

```bash
# 1. Git 저장소 초기화
git init

# 2. 모든 파일 추가 (이미 작성된 .gitignore가 불필요한 파일을 제외해줍니다)
git add .

# 3. 첫 번째 커밋 생성
git commit -m "Initial commit for Daiso store navigation"

# 4. 브랜치 이름을 main으로 설정 (기본이 master일 수 있음)
git branch -M main

# 5. GitHub 원격 저장소 연결 (URL 부분은 본인의 GitHub 주소로 변경하세요)
# 예시: git remote add origin https://github.com/사용자아이디/내저장소이름.git
git remote add origin <GitHub-Repository-URL>

# 6. 코드를 GitHub로 푸시
git push -u origin main
```

## 4. 주의사항 (중요!)
*   **환경 변수**: 현재 `.gitignore`에 `.env` 파일이 포함되어 있어 API 키 같은 비밀 정보는 안전합니다.
*   **데이터베이스**: `backend/database/products.db` 파일이 약 3.4MB입니다. 이 파일을 GitHub에 올리고 싶지 않다면 `.gitignore`에 추가하세요.
    *   추가 방법: `.gitignore` 파일 맨 아래에 `backend/database/products.db`를 입력합니다.
*   **업데이트**: 이후 코드가 변경되면 다음 명령어를 사용하세요.
    ```bash
    git add .
    git commit -m "변경 내용 설명"
    git push
    ```
