#!/usr/bin/env python3
"""
ranx-k 기본 토크나이저 사용 예제

이 예제는 KiwiTokenizer의 기본 사용법을 보여줍니다.
"""

from ranx_k.tokenizers import KiwiTokenizer

def main():
    print("🔤 ranx-k KiwiTokenizer 예제")
    print("=" * 50)
    
    # 1. 기본 형태소 분석 토크나이저
    print("\n1️⃣ 형태소 분석 토크나이저")
    morphs_tokenizer = KiwiTokenizer(method='morphs', use_stopwords=True)
    
    sample_texts = [
        "자연어처리는 인공지능의 핵심 기술입니다.",
        "RAG 시스템은 검색과 생성을 결합합니다.",
        "Kiwi 토크나이저는 한국어 분석에 특화되어 있습니다.",
        "ranx-k는 정보 검색 평가를 위한 도구입니다."
    ]
    
    for text in sample_texts:
        tokens = morphs_tokenizer.tokenize(text)
        print(f"입력: {text}")
        print(f"토큰: {tokens}")
        print(f"토큰 개수: {len(tokens)}")
        print("-" * 40)
    
    # 2. 명사 추출 토크나이저
    print("\n2️⃣ 명사 추출 토크나이저")
    nouns_tokenizer = KiwiTokenizer(method='nouns', use_stopwords=True)
    
    text = "머신러닝과 딥러닝 기술을 활용한 자연어처리 시스템의 성능 평가"
    morphs_tokens = morphs_tokenizer.tokenize(text)
    nouns_tokens = nouns_tokenizer.tokenize(text)
    
    print(f"입력: {text}")
    print(f"형태소 분석: {morphs_tokens}")
    print(f"명사 추출: {nouns_tokens}")
    
    # 3. 불용어 처리
    print("\n3️⃣ 불용어 커스터마이징")
    custom_tokenizer = KiwiTokenizer(method='morphs', use_stopwords=True)
    
    text = "이 시스템은 매우 효과적인 방법입니다."
    
    # 기본 불용어로 토큰화
    original_tokens = custom_tokenizer.tokenize(text)
    print(f"입력: {text}")
    print(f"기본 불용어: {original_tokens}")
    
    # 커스텀 불용어 추가
    custom_tokenizer.add_stopwords(['시스템', '방법'])
    custom_tokens = custom_tokenizer.tokenize(text)
    print(f"커스텀 불용어 추가 후: {custom_tokens}")
    
    # 현재 불용어 확인
    stopwords = custom_tokenizer.get_stopwords()
    print(f"전체 불용어 개수: {len(stopwords)}")
    print(f"일부 불용어: {list(stopwords)[:10]}")
    
    # 4. 비교 분석
    print("\n4️⃣ 토크나이저 비교")
    comparison_text = "자연어처리 기술의 발전으로 AI 시스템이 향상되고 있습니다."
    
    # 불용어 사용 vs 미사용
    with_stopwords = KiwiTokenizer(method='morphs', use_stopwords=True)
    without_stopwords = KiwiTokenizer(method='morphs', use_stopwords=False)
    
    tokens_with = with_stopwords.tokenize(comparison_text)
    tokens_without = without_stopwords.tokenize(comparison_text)
    
    print(f"입력: {comparison_text}")
    print(f"불용어 제거: {tokens_with} ({len(tokens_with)}개)")
    print(f"불용어 유지: {tokens_without} ({len(tokens_without)}개)")
    
    # 5. 성능 테스트
    print("\n5️⃣ 토큰화 성능 테스트")
    import time
    
    test_texts = [
        "한국어 자연어처리는 형태소 분석이 중요합니다.",
        "정보 검색 시스템의 성능 평가 방법론을 연구합니다.",
        "딥러닝 기반 언어 모델의 발전이 놀랍습니다."
    ] * 100  # 300개 문장
    
    start_time = time.time()
    total_tokens = 0
    
    for text in test_texts:
        tokens = morphs_tokenizer.tokenize(text)
        total_tokens += len(tokens)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"처리 문장 수: {len(test_texts)}")
    print(f"총 토큰 수: {total_tokens}")
    print(f"처리 시간: {processing_time:.3f}초")
    print(f"초당 문장 처리: {len(test_texts) / processing_time:.1f}개")
    print(f"초당 토큰 처리: {total_tokens / processing_time:.1f}개")
    
    print("\n✅ 기본 토크나이저 예제 완료!")

if __name__ == "__main__":
    main()