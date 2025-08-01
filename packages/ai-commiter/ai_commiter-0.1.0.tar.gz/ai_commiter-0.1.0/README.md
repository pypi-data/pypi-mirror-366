# AI-Commiter

인공지능을 활용하여 Git 커밋 메시지를 자동으로 생성하는 도구입니다. 파일 변경 내역을 분석하고 OpenAI API를 통해 명확하고 구조화된 커밋 메시지를 생성합니다.

[![PyPI version](https://badge.fury.io/py/ai-commiter.svg)](https://badge.fury.io/py/ai-commiter)

## 주요 기능

- **자동 커밋 메시지 생성**: Git diff를 분석하여 의미 있는 커밋 메시지 생성
- **Conventional Commits 지원**: 표준화된 커밋 메시지 형식 사용
- **파일 분류 및 요약**: 여러 파일 변경 시 카테고리별로 분류하여 요약 정보 제공
- **커스텀 프롬프트**: 사용자 정의 프롬프트 템플릿 지원
- **자동 커밋**: 생성된 메시지로 자동 커밋 옵션
- **다양한 모델 지원**: OpenAI의 다양한 GPT 모델 선택 가능

## 설치 방법

### PyPI 패키지로 설치 (권장)

```bash
# PyPI에서 패키지 설치
pip install ai-commiter

# OpenAI API 키 설정
export OPENAI_API_KEY=your-api-key-here
# Windows에서는 
# set OPENAI_API_KEY=your-api-key-here
```

### 저장소에서 직접 설치

```bash
# 저장소 클론
git clone https://github.com/your-username/ai-commiter.git
cd ai-commiter

# 패키지로 설치
pip install -e .

# OpenAI API 키 설정
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## 사용 방법

### 기본 사용법

```bash
# 스테이지된 변경 사항에 대한 커밋 메시지 생성
ai-commit

# 생성된 메시지로 바로 커밋
ai-commit --commit

# 패키지 설치 없이 직접 실행할 경우
python -m ai_commiter.git_commit_ai
```

### 추가 옵션

```bash
# 특정 저장소 경로 지정
ai-commit --repo /path/to/repo --model gpt-4 --commit

# 파일 분류 기능 비활성화
ai-commit --no-categorize

# 스테이지되지 않은 모든 변경 사항 포함
ai-commit --all

# 다른 OpenAI 모델 사용
ai-commit --model gpt-4

# 커스텀 프롬프트 템플릿 사용
ai-commit --prompt my_custom_prompt.txt
```

## 커스텀 프롬프트 템플릿

커스텀 프롬프트 템플릿 파일을 만들어 AI가 생성하는 커밋 메시지의 스타일과 형식을 조정할 수 있습니다. 템플릿에는 `{diff}`와 `{files}` 변수를 사용할 수 있습니다.

예시 템플릿:

```
다음 변경 사항을 분석하여 한국어로 커밋 메시지만 출력해주세요:
커밋 메시지 형식: [타입] 내용
```

## 요구 사항

- Python 3.7 이상
- Git
- OpenAI API 키

## 라이센스

MIT
