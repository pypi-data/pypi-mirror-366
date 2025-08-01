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

def generate_commit_message(diff, files, prompt_template=None, openai_model="gpt-3.5-turbo", enable_categorization=True):
    """
    변경 내용을 기반으로 커밋 메시지를 생성합니다.
    
    Args:
        diff (str): Git diff 내용
        files (list): 변경된 파일 목록
        prompt_template (str, optional): 커스텀 프롬프트 템플릿
        openai_model (str, optional): 사용할 OpenAI 모델
        enable_categorization (bool, optional): 파일 분류 기능 사용 여부
    
    Returns:
        str: 생성된 커밋 메시지
    """
    # API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("오류: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)
    
    # 파일 변경 내용 분류 (여러 파일이 변경된 경우)
    change_summary = None
    if enable_categorization and len(files) > 1:
        change_summary = categorize_file_changes(files, diff)
    
    # 기본 프롬프트 템플릿 설정
    if prompt_template is None:
        if change_summary and len(files) > 1:
            # 여러 파일 변경 시 카테고리별 분류 정보를 포함한 프롬프트
            prompt_template = """
다음은 Git 저장소의 변경 내용입니다. 여러 파일이 변경되었으므로 카테고리별 분류 정보를 참고하여 간결하고 명확한 커밋 메시지를 작성해 주세요.

커밋 메시지는 다음과 같은 형식으로 작성해 주세요:
- 첫 줄: 변경의 요약 (타입: 내용) - 영어로 작성, 앞에 - 기호 없이 작성
- 두 번째 줄: 비움
- 세 번째 줄 이후: 필요한 경우 변경 내용 상세 설명 (선택 사항)

타입은 다음 중 하나를 사용하세요:
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 변경
style: 코드 형식 변경
refactor: 코드 리팩토링
test: 테스트 코드 추가 또는 수정
chore: 빌드 프로세스 또는 보조 도구 및 라이브러리 변경

변경 통계:
- 총 파일 수: {total_files}개
- 추가된 라인: {added_lines}줄
- 삭제된 라인: {removed_lines}줄
{new_files_info}{deleted_files_info}
카테고리별 변경된 파일:
{categorized_files}

변경 내용 (diff):
{diff}

커밋 메시지만 출력해주세요:
"""
        else:
            # 단일 파일 또는 분류 비활성화 시 기본 프롬프트
            prompt_template = """
다음은 Git 저장소의 변경 내용입니다. 이 변경 내용을 바탕으로 간결하고 명확한 커밋 메시지를 작성해 주세요.
커밋 메시지는 다음과 같은 형식으로 작성해 주세요:
- 첫 줄: 변경의 요약 (타입: 내용) - 영어로 작성, 앞에 - 기호 없이 작성
- 두 번째 줄: 비움
- 세 번째 줄 이후: 필요한 경우 변경 내용 상세 설명 (선택 사항)

타입은 다음 중 하나를 사용하세요:
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 변경
style: 코드 형식 변경 (코드 작동에 영향을 주지 않는 변경)
refactor: 코드 리팩토링
test: 테스트 코드 추가 또는 수정
chore: 빌드 프로세스 또는 보조 도구 및 라이브러리 변경

변경된 파일:
{files}

변경 내용 (diff):
{diff}

커밋 메시지만 출력해주세요:
"""
    
    # 프롬프트 변수 준비
    prompt_vars = {"diff": diff, "files": "\n".join(files)}
    
    # 카테고리 정보가 있는 경우 추가 변수 설정
    if change_summary:
        stats = change_summary['stats']
        prompt_vars.update({
            "total_files": stats['total_files'],
            "added_lines": stats['added_lines'],
            "removed_lines": stats['removed_lines'],
            "new_files_info": f"\n- 새 파일: {len(stats['new_files'])}개" if stats['new_files'] else "",
            "deleted_files_info": f"\n- 삭제된 파일: {len(stats['deleted_files'])}개" if stats['deleted_files'] else "",
            "categorized_files": "\n".join([f"- {category.title()}: {', '.join(files)}" 
                                           for category, files in change_summary['categories'].items()])
        })
        
        # 카테고리별 프롬프트용 변수명 설정
        input_variables = ["diff", "total_files", "added_lines", "removed_lines", 
                          "new_files_info", "deleted_files_info", "categorized_files"]
    else:
        input_variables = ["diff", "files"]
    
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
        print(f"✅ 성공적으로 커밋했습니다: '{message}'")
        return True
    except Exception as e:
        print(f"커밋 오류: {str(e)}")
        return False

def main():
    # .env 파일 로드
    load_dotenv()
    
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(description='AI를 활용한 Git 커밋 메시지 생성기')
    parser.add_argument('--repo', default='.', help='Git 저장소 경로 (기본값: 현재 디렉토리)')
    parser.add_argument('--all', action='store_false', dest='staged', 
                        help='스테이지된 변경사항 대신 모든 변경사항 포함')
    parser.add_argument('--model', default='gpt-3.5-turbo', help='사용할 OpenAI 모델')
    parser.add_argument('--commit', action='store_true', help='자동으로 커밋 수행')
    parser.add_argument('--prompt', help='커스텀 프롬프트 템플릿 파일 경로')
    parser.add_argument('--no-categorize', action='store_true', help='파일 분류 기능 비활성화')
    
    args = parser.parse_args()
    
    # 커스텀 프롬프트 템플릿 로드
    custom_prompt = None
    if args.prompt:
        try:
            with open(args.prompt, 'r', encoding='utf-8') as f:
                custom_prompt = f.read()
        except Exception as e:
            print(f"프롬프트 파일 로드 오류: {str(e)}")
            sys.exit(1)
    
    # Git diff 가져오기
    diff, changed_files = get_git_diff(args.repo, args.staged)
    
    if diff is None or not changed_files:
        print("변경된 내용이 없습니다.")
        sys.exit(0)
    
    # 커밋 메시지 생성
    print("🤖 AI가 커밋 메시지를 생성 중입니다...")
    
    # 파일 분류 정보 출력 (여러 파일 변경 시)
    if len(changed_files) > 1 and not args.no_categorize:
        change_summary = categorize_file_changes(changed_files, diff)
        print(f"\n📊 변경 통계: {change_summary['stats']['total_files']}개 파일, "
              f"+{change_summary['stats']['added_lines']}/-{change_summary['stats']['removed_lines']} 라인")
        
        if change_summary['categories']:
            print("📁 카테고리별 변경:")
            for category, files in change_summary['categories'].items():
                print(f"  - {category.title()}: {', '.join(files)}")
    
    commit_message = generate_commit_message(diff, changed_files, custom_prompt, args.model, 
                                           enable_categorization=not args.no_categorize)
    
    print("\n📝 생성된 커밋 메시지:")
    print("-" * 50)
    print(commit_message)
    print("-" * 50)
    
    # 자동 커밋 옵션이 활성화된 경우
    if args.commit:
        confirm = input("\n이 메시지로 커밋하시겠습니까? (y/n): ")
        if confirm.lower() == 'y':
            make_commit(args.repo, commit_message)
    else:
        print("\n커밋하려면 다음 명령을 실행하세요:")
        print(f"git commit -m \"{commit_message}\"")

def cli():
    """패키지의 명령줄 진입점"""
    main()

if __name__ == "__main__":
    main()
