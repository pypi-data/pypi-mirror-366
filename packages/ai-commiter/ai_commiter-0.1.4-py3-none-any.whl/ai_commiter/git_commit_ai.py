#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import git
import argparse
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import re
from collections import defaultdict
from ai_commiter import __version__

# Language pack definitions with locale support
LANGUAGE_PACKS = {
    'ko': {
        'name': 'Korean (한국어)',
        'locale': 'ko-KR',
        'response_instruction': 'Please respond in Korean. The commit message title must be in English (imperative mood), but the detailed description must be written in Korean. 제목은 영어로, 상세 설명은 반드시 한국어로 작성해주세요.'
    },
    'ko-KR': {
        'name': 'Korean (한국어)',
        'locale': 'ko-KR', 
        'response_instruction': 'Please respond in Korean. The commit message title must be in English (imperative mood), but the detailed description must be written in Korean. 제목은 영어로, 상세 설명은 반드시 한국어로 작성해주세요.'
    },
    'en': {
        'name': 'English',
        'locale': 'en-US',
        'response_instruction': 'Please respond in English. Use imperative mood for the title and provide detailed description in English.'
    },
    'en-US': {
        'name': 'English (US)',
        'locale': 'en-US',
        'response_instruction': 'Please respond in English. Use imperative mood for the title and provide detailed description in English.'
    },
    'en-GB': {
        'name': 'English (UK)',
        'locale': 'en-GB',
        'response_instruction': 'Please respond in British English. Use imperative mood for the title and provide detailed description in British English.'
    },
    'ja': {
        'name': 'Japanese (日本語)',
        'locale': 'ja-JP',
        'response_instruction': 'Please respond in Japanese. The title should be in English (imperative mood), but the detailed description should be in Japanese. タイトルは英語で、詳細説明は日本語で記述してください。'
    },
    'ja-JP': {
        'name': 'Japanese (日本語)',
        'locale': 'ja-JP',
        'response_instruction': 'Please respond in Japanese. The title should be in English (imperative mood), but the detailed description should be in Japanese. タイトルは英語で、詳細説明は日本語で記述してください。'
    },
    'zh': {
        'name': 'Chinese Simplified (简体中文)',
        'locale': 'zh-CN',
        'response_instruction': 'Please respond in Simplified Chinese. The title should be in English (imperative mood), but the detailed description should be in Simplified Chinese. 标题用英语，详细说明请用简体中文。'
    },
    'zh-CN': {
        'name': 'Chinese Simplified (简体中文)',
        'locale': 'zh-CN',
        'response_instruction': 'Please respond in Simplified Chinese. The title should be in English (imperative mood), but the detailed description should be in Simplified Chinese. 标题用英语，详细说明请用简体中文。'
    },
    'zh-TW': {
        'name': 'Chinese Traditional (繁體中文)',
        'locale': 'zh-TW',
        'response_instruction': 'Please respond in Traditional Chinese. The title should be in English (imperative mood), but the detailed description should be in Traditional Chinese. 標題用英語，詳細說明請用繁體中文。'
    }
}

# Unified English prompt template
COMMIT_PROMPT_TEMPLATE = '''Analyze the following Git repository changes. Refer to the categorized information to write a concise and clear commit message.
After analyzing the changes, identify the core content and use only one type.
Please read the given {language_instruction} and create an appropriate Git commit message based on it.

The commit message consists of header and body.
Each component follows these rules:
1. header
- Written in the format 'type: content'
- Content is a brief summary of changes, written within 50 characters

2. body
- Detailed description of changes, written within 72 characters per line
- Describe what and why changed rather than how it was changed
- Explain changes across multiple lines as needed

Select only one type from the following (even if there are multiple changes, select only the most important change type):
feat: Add new feature
fix: Fix bug
docs: Change documentation
style: Change code formatting
refactor: Code refactoring
test: Add or modify test code
chore: Change build process or auxiliary tools and libraries

Change statistics:
- Total {total_files} files changed
- {added_lines} lines added, {removed_lines} lines deleted

{categorized_files}

Changes (diff):
{diff}

{language_instruction}

Output only the commit message:'''

def get_language_instruction(lang):
    """Get language-specific response instruction."""
    return LANGUAGE_PACKS.get(lang, LANGUAGE_PACKS['ko'])['response_instruction']

def get_git_diff(repo_path='.', staged=True):
    """
    Git 저장소에서 변경 내용을 가져옵니다.
    
    Args:
        repo_path (str): Git 저장소 경로
        staged (bool): 스테이지된 변경사항만 포함할지 여부
    
    Returns:
        str: Git diff 출력
    """
    try:
        repo = git.Repo(repo_path)
        if staged:
            # 스테이지된 변경사항
            diff = repo.git.diff('--staged')
        else:
            # 모든 변경사항
            diff = repo.git.diff()
        
        # 변경된 파일 목록
        if staged:
            changed_files = repo.git.diff('--staged', '--name-only').split('\n')
        else:
            changed_files = repo.git.diff('--name-only').split('\n')
        
        # 변경 내용이 없는 경우
        if not diff:
            return None, []
        
        return diff, [f for f in changed_files if f]
    except git.exc.InvalidGitRepositoryError:
        print(f"오류: '{repo_path}'는 유효한 Git 저장소가 아닙니다.")
        sys.exit(1)
    except Exception as e:
        print(f"Git diff 가져오기 오류: {str(e)}")
        sys.exit(1)

def categorize_file_changes(changed_files, diff):
    """
    변경된 파일들을 카테고리별로 분류합니다.
    
    Args:
        changed_files (list): 변경된 파일 목록
        diff (str): Git diff 내용
    
    Returns:
        dict: 카테고리별로 분류된 파일 변경 정보
    """
    categories = {
        'frontend': [],
        'backend': [],
        'config': [],
        'docs': [],
        'tests': [],
        'assets': [],
        'other': []
    }
    
    # 파일 확장자 및 경로 기반 분류
    file_patterns = {
        'frontend': ['.html', '.css', '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte', '.scss', '.sass', '.less'],
        'backend': ['.py', '.java', '.go', '.rs', '.cpp', '.c', '.php', '.rb', '.cs', '.kt', '.scala'],
        'config': ['.json', '.yaml', '.yml', '.toml', '.ini', '.conf', '.config', 'Dockerfile', 'docker-compose', '.env'],
        'docs': ['.md', '.rst', '.txt', '.doc', '.docx', '.pdf'],
        'tests': ['test_', '_test.', '.test.', 'spec_', '_spec.', '.spec.'],
        'assets': ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot']
    }
    
    # 변경 유형 분석 (추가, 수정, 삭제)
    change_types = defaultdict(list)
    
    for file_path in changed_files:
        categorized = False
        file_lower = file_path.lower()
        
        # 테스트 파일 우선 확인
        for test_pattern in file_patterns['tests']:
            if test_pattern in file_lower:
                categories['tests'].append(file_path)
                categorized = True
                break
        
        if not categorized:
            # 다른 카테고리 확인
            for category, patterns in file_patterns.items():
                if category == 'tests':  # 이미 확인했으므로 스킵
                    continue
                    
                for pattern in patterns:
                    if file_lower.endswith(pattern) or pattern in file_lower:
                        categories[category].append(file_path)
                        categorized = True
                        break
                
                if categorized:
                    break
        
        if not categorized:
            categories['other'].append(file_path)
    
    # diff에서 변경 유형 분석
    diff_lines = diff.split('\n')
    added_lines = len([line for line in diff_lines if line.startswith('+') and not line.startswith('+++')])
    removed_lines = len([line for line in diff_lines if line.startswith('-') and not line.startswith('---')])
    
    # 새 파일과 삭제된 파일 감지
    file_status = {}
    new_files = []
    deleted_files = []
    for line in diff_lines:
        if line.startswith('diff --git'):
            parts = line.split(' ')
            if len(parts) >= 3:
                file_path = parts[2][2:]  # remove 'a/'
                file_status[file_path] = 'modified'
        elif line.startswith('new file mode'):
            new_files.append(file_path)
            file_status[file_path] = 'added'
        elif line.startswith('deleted file mode'):
            deleted_files.append(file_path)
            file_status[file_path] = 'deleted'
    
    # 분류 정보 구성
    result = {
        'categories': {},
        'stats': {
            'total_files': len(changed_files),
            'added_lines': added_lines,
            'removed_lines': removed_lines,
            'new_files': new_files,
            'deleted_files': deleted_files
        }
    }
    
    # 각 카테고리에 파일이 있는 경우만 결과에 포함
    for category, files in categories.items():
        if files:
            result['categories'][category] = files
    
    return result

def get_recommended_model(files, diff):
    """
    변경사항 복잡도에 따라 모델 추천
    """
    
    # 기본 메트릭
    file_count = len(files)
    diff_lines = len(diff.split('\n'))
    
    # 복잡도 점수 계산
    complexity_score = 0
    score_details = []
    
    # 파일 수에 따른 점수
    if file_count > 10:
        complexity_score += 3
        score_details.append(f"파일 수 {file_count}개 (+3)")
    elif file_count > 5:
        complexity_score += 2
        score_details.append(f"파일 수 {file_count}개 (+2)")
    elif file_count > 1:
        complexity_score += 1
        score_details.append(f"파일 수 {file_count}개 (+1)")
    else:
        score_details.append(f"파일 수 {file_count}개 (+0)")
    
    # diff 크기에 따른 점수
    if diff_lines > 1000:
        complexity_score += 3
        score_details.append(f"diff {diff_lines}줄 (+3)")
    elif diff_lines > 500:
        complexity_score += 2
        score_details.append(f"diff {diff_lines}줄 (+2)")
    elif diff_lines > 100:
        complexity_score += 1
        score_details.append(f"diff {diff_lines}줄 (+1)")
    else:
        score_details.append(f"diff {diff_lines}줄 (+0)")

    # 점수에 따른 모델 선택 (3점 이상에서 GPT-4.1 사용)
    if complexity_score >= 4:
        selected_model = "gpt-4.1"
        reason = "복잡한 변경사항"
    else:
        selected_model = "gpt-3.5-turbo"
        reason = "간단한 변경사항"
    
    return selected_model, complexity_score, score_details, reason

def generate_commit_message(diff, files, prompt_template=None, openai_model="gpt-3.5-turbo", enable_categorization=True, lang='ko'):
    """
    변경 내용을 기반으로 커밋 메시지를 생성합니다.
    
    Args:
        diff (str): Git diff 내용
        files (list): 변경된 파일 목록
        prompt_template (str, optional): 커스텀 프롬프트 템플릿
        openai_model (str, optional): 사용할 OpenAI 모델
        enable_categorization (bool, optional): 파일 분류 기능 사용 여부
        lang (str, optional): 응답 언어 코드
    
    Returns:
        str: 생성된 커밋 메시지
    """
    # API 키 확인
    # AI_COMMITER_API_KEY를 우선 확인하고, 없으면 OPENAI_API_KEY 확인
    api_key = os.getenv("AI_COMMITER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key is not set.")
        print("Please set AI_COMMITER_API_KEY or OPENAI_API_KEY environment variable.")
        print("Example: export AI_COMMITER_API_KEY=your-api-key-here")
        sys.exit(1)
    
    # OPENAI_API_KEY 환경 변수가 없는 경우, 임시로 설정 (라이브러리가 확인하는 변수명)
    if not os.getenv("OPENAI_API_KEY") and api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    # 파일 변경 내용 분류 (여러 파일이 변경된 경우)
    change_summary = None
    if enable_categorization:
        change_summary = categorize_file_changes(files, diff)
    
    # 기본 프롬프트 템플릿 설정 (새로운 언어팩 시스템 사용)
    if prompt_template is None:
        prompt_template = COMMIT_PROMPT_TEMPLATE
    
    # 프롬프트 변수 준비
    prompt_vars = {
        "diff": diff,
        "language_instruction": get_language_instruction(lang)
    }
    
    # 카테고리 정보가 있는 경우 추가 변수 설정
    if change_summary:
        stats = change_summary['stats']
        # 카테고리별 파일 목록 영어로 포맷팅
        categorized_files_str = "\n".join([
            f"- {category.title()}: {', '.join(files)}" 
            for category, files in change_summary['categories'].items() if files
        ])
        
        prompt_vars.update({
            "total_files": stats['total_files'],
            "added_lines": stats['added_lines'],
            "removed_lines": stats['removed_lines'],
            "categorized_files": categorized_files_str if categorized_files_str else "No categorized files"
        })
        
        input_variables = ["diff", "total_files", "added_lines", "removed_lines", 
                          "categorized_files", "language_instruction"]
    else:
        # 분류 정보가 없는 경우 기본값 설정
        prompt_vars.update({
            "total_files": len(files),
            "added_lines": "Unknown",
            "removed_lines": "Unknown",
            "categorized_files": "Not categorized"
        })
        input_variables = ["diff", "total_files", "added_lines", "removed_lines", 
                          "categorized_files", "language_instruction"]
    
    # LangChain 설정 (새로운 RunnableSequence 방식)
    llm = ChatOpenAI(temperature=0.5, model_name=openai_model)
    chain_prompt = PromptTemplate(input_variables=input_variables, template=prompt_template)
    chain = chain_prompt | llm
    
    # 너무 큰 diff는 잘라내기 (토큰 한도 고려)
    if len(prompt_vars["diff"]) > 4000:
        prompt_vars["diff"] = prompt_vars["diff"][:4000] + "\n... (생략됨)"
    
    # 커밋 메시지 생성
    result = chain.invoke(prompt_vars)
    # AIMessage 객체에서 content 속성 추출
    commit_message = result.content if hasattr(result, 'content') else str(result)
    return commit_message.strip()

def make_commit(repo_path='.', message=None):
    """
    생성된 메시지로 커밋을 수행합니다.
    
    Args:
        repo_path (str): Git 저장소 경로
        message (str): 커밋 메시지
    """
    try:
        repo = git.Repo(repo_path)
        repo.git.commit('-m', message)
        print(f"✅ Successfully committed: '{message}'")
        return True
    except Exception as e:
        print(f"Commit error: {str(e)}")
        return False

def main():
    # .env 파일 로드
    load_dotenv()
    
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(description='AI-powered Git commit message generator with multi-language support')
    parser.add_argument('--version', action='version', version=f'ai-commiter {__version__}',
                        help='Show version information')
    parser.add_argument('--repo', default='.', help='Git repository path (default: current directory)')
    parser.add_argument('--all', action='store_false', dest='staged', 
                        help='Include all changes instead of staged changes only')
    parser.add_argument('--model', help='Manually specify OpenAI model to use (default: auto-selection)')
    parser.add_argument('--no-auto-model', action='store_true', help='Disable automatic model selection (use default gpt-3.5-turbo)')
    parser.add_argument('--commit', action='store_true', help='Automatically perform commit with generated message')
    parser.add_argument('--prompt', help='Path to custom prompt template file')
    parser.add_argument('--no-categorize', action='store_true', help='Disable file categorization feature')
    parser.add_argument('--lang', 
                        choices=['ko', 'ko-KR', 'en', 'en-US', 'en-GB', 'ja', 'ja-JP', 'zh', 'zh-CN', 'zh-TW'], 
                        default='ko',
                        help='Commit message language (ko/ko-KR: Korean, en/en-US/en-GB: English, ja/ja-JP: Japanese, zh/zh-CN: Chinese Simplified, zh-TW: Chinese Traditional)')
    
    args = parser.parse_args()
    
    # 커스텀 프롬프트 템플릿 로드
    custom_prompt = None
    if args.prompt:
        try:
            with open(args.prompt, 'r', encoding='utf-8') as f:
                custom_prompt = f.read()
        except Exception as e:
            print(f"Prompt file load error: {str(e)}")
            sys.exit(1)
    
    # Git diff 가져오기
    diff, changed_files = get_git_diff(args.repo, args.staged)
    
    if diff is None or not changed_files:
        print("No changes detected.")
        sys.exit(0)
    
    # 모델 선택 (기본: 자동 선택)
    if args.model:
        # 수동으로 모델 지정된 경우
        selected_model = args.model
        print(f"🎯 Manual selection: Using {selected_model} model")
    elif args.no_auto_model:
        # 자동 선택 비활성화
        selected_model = "gpt-3.5-turbo"
        print(f"🔄 Default model: Using {selected_model}")
    else:
        # 자동 모델 선택 (기본값)
        selected_model, score, details, reason = get_recommended_model(changed_files, diff)
        # 영어로 복잡도 이유 변환
        english_reason = "complex changes" if reason == "복잡한 변경사항" else "simple changes"
        print(f"🧠 Complexity analysis: {english_reason} (score: {score})")
        print(f"   • {', '.join(details)}")
        print(f"   → {selected_model} model selected")
    
    # 커밋 메시지 생성
    print("🤖 AI is generating commit message...")
    
    # 파일 분류 정보 출력 (여러 파일 변경 시)
    if len(changed_files) > 1 and not args.no_categorize:
        change_summary = categorize_file_changes(changed_files, diff)
        print(f"\n📊 Change statistics: {change_summary['stats']['total_files']} files, "
              f"+{change_summary['stats']['added_lines']}/-{change_summary['stats']['removed_lines']} lines")
        
        if change_summary['categories']:
            print("📁 Changes by category:")
            for category, files in change_summary['categories'].items():
                print(f"  - {category.title()}: {', '.join(files)}")
    
    commit_message = generate_commit_message(diff, changed_files, custom_prompt, selected_model, 
                                           enable_categorization=not args.no_categorize, lang=args.lang)
    
    print("\n📝 Generated commit message:")
    print("-" * 50)
    print(commit_message)
    print("-" * 50)
    
    # 자동 커밋 옵션이 활성화된 경우
    if args.commit:
        confirm = input("\nDo you want to commit with this message? (y/n): ")
        if confirm.lower() == 'y':
            make_commit(args.repo, commit_message)
    else:
        print("\nTo commit, run the following command:")
        print(f"git commit -m \"{commit_message}\"")

def cli():
    """패키지의 명령줄 진입점"""
    main()

if __name__ == "__main__":
    main()
