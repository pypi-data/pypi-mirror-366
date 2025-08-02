# KRenamer - Korean Advanced File Renaming Tool

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

**KRenamer**는 Python tkinter로 개발된 한국어 고급 파일 이름 변경 도구입니다. 직관적인 한글 GUI와 강력한 조건부 필터링 기능으로 대량의 파일을 효율적으로 관리할 수 있습니다.

## ✨ 주요 기능

### 🎯 다양한 이름 변경 방식
- **접두사/접미사 추가**: 파일명 앞뒤에 텍스트 추가
- **순차 번호 매기기**: 파일들을 일련번호로 정리
- **찾기/바꾸기**: 특정 텍스트를 다른 텍스트로 치환
- **정규식 패턴**: 복잡한 패턴 매칭과 치환

### 🔍 고급 조건부 필터링
- **파일 크기 조건**: 특정 크기 이상/이하 파일만 대상
- **수정 날짜 조건**: 날짜 기준으로 파일 필터링
- **확장자 제한**: 특정 파일 형식만 처리

### 🛠️ 일괄 변환 기능
- **대소문자 변환**: 전체 대문자, 소문자, 첫글자 대문자
- **특수문자 처리**: 안전하지 않은 문자 제거
- **공백 처리**: 공백을 언더스코어로 변환
- **중복 처리**: 동일한 파일명 발생 시 자동 번호 부여

### 🖥️ 사용자 친화적 인터페이스
- **드래그 앤 드롭**: 파일을 끌어다 놓기만 하면 추가
- **실시간 미리보기**: 변경 결과를 즉시 확인
- **반응형 레이아웃**: 창 크기에 따라 자동 조정
- **직관적인 탭 구성**: 기능별로 체계적 구성

## 🚀 빠른 시작

### 필요 조건
- Python 3.8 이상
- tkinter (Python 표준 라이브러리)
- tkinterdnd2 (드래그 앤 드롭 기능)

### 설치 및 실행

1. **저장소 클론**
   ```bash
   git clone https://github.com/geniuskey/renamer.git
   cd renamer
   ```

2. **의존성 설치**
   ```bash
   pip install tkinterdnd2
   ```

3. **프로그램 실행**
   ```bash
   cd src/krenamer
   python main.py
   ```

### 개발자 설치 (권장)

개발 의존성을 포함한 완전한 설치:

```bash
# 개발 의존성 포함 설치
pip install -e .[dev]

# 또는 개별 설치
pip install tkinterdnd2 pyinstaller build twine mkdocs mkdocs-material
```

## 📋 사용 방법

### 1. 파일 추가
- **드래그 앤 드롭**: 파일을 파일 목록 영역에 끌어다 놓기
- **파일 추가 버튼**: 대화상자에서 파일 선택

### 2. 이름 변경 설정

#### 기본 변경
- **접두사**: 모든 파일명 앞에 텍스트 추가
  ```
  photo.jpg → vacation_photo.jpg
  ```
- **접미사**: 모든 파일명 뒤에 텍스트 추가
  ```
  photo.jpg → photo_edited.jpg
  ```
- **순번**: 파일들을 순차 번호로 정리
  ```
  photo.jpg → 001_photo.jpg
  video.mp4 → 002_video.mp4
  ```
- **찾기/바꾸기**: 특정 문자열을 다른 문자열로 치환
  ```
  IMG_20240315.jpg → Photo_20240315.jpg
  ```

#### 패턴 기반
- **정규식 사용**: 복잡한 패턴 매칭
  ```
  정규식: (\d{4})(\d{2})(\d{2})
  치환: \1-\2-\3
  결과: 20240315 → 2024-03-15
  ```

#### 조건부 변경
- **파일 크기**: 1MB 이상 파일만 대상
- **수정 날짜**: 2024년 이후 수정된 파일만
- **확장자**: .jpg, .png 파일만 처리

#### 일괄 작업
- **대소문자**: 모든 파일명을 소문자로 변환
- **특수문자 제거**: 안전하지 않은 문자 제거
- **공백 변환**: 공백을 언더스코어(_)로 변환

### 3. 미리보기 및 실행
- **실시간 미리보기**: 설정 변경 시 즉시 결과 확인
- **조건 확인**: 어떤 파일이 변경되는지 미리 보기
- **안전한 실행**: 확인 후 일괄 변경 실행

## 🏗️ 프로젝트 구조

```
src/krenamer/
├── __init__.py          # 패키지 초기화
├── main.py             # 프로그램 진입점
├── gui.py              # GUI 인터페이스
└── core.py             # 파일 처리 엔진
```

### 주요 모듈

- **`main.py`**: 애플리케이션 시작점, 오류 처리
- **`gui.py`**: tkinter 기반 사용자 인터페이스
- **`core.py`**: 파일 이름 변경 로직, 조건 처리
- **`__init__.py`**: 패키지 정보

## 🚀 빌드 및 배포

KRenamer는 `make.bat` 스크립트를 통해 다양한 빌드 작업을 지원합니다.

### 📦 실행 파일 빌드

```bash
# 단일 실행 파일 생성 (.exe)
make exe

# 결과: dist/KRenamer.exe (약 15-25MB)
```

### 🎁 패키지 빌드

```bash
# Wheel 패키지 빌드
make wheel

# 소스 배포 빌드
make sdist

# 모든 패키지 빌드 (wheel + sdist)
make build
```

### 📚 문서 빌드

```bash
# 문서 빌드
make docs

# 문서 로컬 서버 (http://localhost:8000)
make serve
```

### 🚀 배포

```bash
# TestPyPI에 업로드 (테스트용)
make publish-test

# PyPI에 업로드 (프로덕션)
make publish
```

### 🧹 정리

```bash
# 빌드 아티팩트 정리
make clean
```

### 전체 명령어 목록

```bash
make help  # 모든 명령어 보기
```

## 🔧 기술 사양

### 개발 환경
- **언어**: Python 3.8+
- **GUI 프레임워크**: tkinter
- **추가 라이브러리**: tkinterdnd2

### 지원 플랫폼
- **주요 지원**: Windows 10/11
- **부분 지원**: macOS, Linux (드래그 앤 드롭 기능 제한)

### 성능
- **처리 용량**: 수천 개 파일 동시 처리
- **메모리 사용량**: 경량 (< 50MB)
- **처리 속도**: 즉시 미리보기, 빠른 일괄 처리

## 🛡️ 안전 기능

- **미리보기 필수**: 실행 전 반드시 결과 확인
- **중복 방지**: 동일 파일명 자동 처리
- **오류 처리**: 파일 접근 오류 시 안전한 처리
- **되돌리기 불가 경고**: 실행 전 확인 메시지

## 🐛 문제 해결

### 일반적인 문제

1. **tkinterdnd2 설치 오류**
   ```bash
   pip install --upgrade tkinterdnd2
   ```

2. **드래그 앤 드롭이 작동하지 않음**
   - tkinterdnd2가 설치되어 있는지 확인
   - "파일 추가" 버튼을 대안으로 사용

3. **한글 파일명 처리 문제**
   - Windows에서는 자동으로 처리됨
   - 다른 OS에서는 인코딩 확인 필요

4. **모듈 import 오류**
   ```bash
   # src/krenamer 폴더에서 실행해야 함
   cd src/krenamer
   python main.py
   ```

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 지원

- **GitHub Issues**: [이슈 제보](https://github.com/geniuskey/krenamer/issues)
- **문서**: [프로젝트 문서](https://geniuskey.github.io/krenamer)

---

⭐ 이 프로젝트가 유용하다면 스타를 눌러주세요!