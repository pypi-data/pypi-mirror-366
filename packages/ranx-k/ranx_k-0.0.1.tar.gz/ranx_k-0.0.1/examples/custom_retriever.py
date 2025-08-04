#!/usr/bin/env python3
"""
ranx-k 커스텀 검색기 구현 예제

이 예제는 ranx-k와 호환되는 커스텀 검색기를 구현하는 방법을 보여줍니다.
"""

import numpy as np
from typing import List, Any
from ranx_k.tokenizers import KiwiTokenizer
from ranx_k.evaluation import simple_kiwi_rouge_evaluation

class Document:
    """문서 클래스"""
    def __init__(self, content: str, metadata: dict = None):
        self.page_content = content
        self.metadata = metadata or {}

class SimpleVectorRetriever:
    """간단한 벡터 기반 검색기"""
    
    def __init__(self, documents: List[str]):
        self.documents = [Document(doc) for doc in documents]
        self.tokenizer = KiwiTokenizer(method='morphs', use_stopwords=True)
        self.vocab = self._build_vocabulary()
        self.doc_vectors = self._vectorize_documents()
    
    def _build_vocabulary(self):
        """전체 문서에서 어휘 사전 구축"""
        vocab = set()
        for doc in self.documents:
            tokens = self.tokenizer.tokenize(doc.page_content)
            vocab.update(tokens)
        return {word: i for i, word in enumerate(sorted(vocab))}
    
    def _vectorize_documents(self):
        """문서들을 벡터로 변환"""
        vectors = []
        for doc in self.documents:
            vector = self._text_to_vector(doc.page_content)
            vectors.append(vector)
        return np.array(vectors)
    
    def _text_to_vector(self, text: str):
        """텍스트를 TF 벡터로 변환"""
        tokens = self.tokenizer.tokenize(text)
        vector = np.zeros(len(self.vocab))
        
        for token in tokens:
            if token in self.vocab:
                vector[self.vocab[token]] += 1
        
        # L2 정규화
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def invoke(self, query: str, top_k: int = 10) -> List[Document]:
        """쿼리에 대해 관련 문서들을 검색"""
        query_vector = self._text_to_vector(query)
        
        # 코사인 유사도 계산
        similarities = np.dot(self.doc_vectors, query_vector)
        
        # 상위 k개 문서 선택
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [self.documents[i] for i in top_indices if similarities[i] > 0]

class KeywordRetriever:
    """키워드 기반 검색기"""
    
    def __init__(self, documents: List[str]):
        self.documents = [Document(doc) for doc in documents]
        self.tokenizer = KiwiTokenizer(method='morphs', use_stopwords=True)
    
    def invoke(self, query: str, top_k: int = 10) -> List[Document]:
        """키워드 매칭 기반 검색"""
        query_tokens = set(self.tokenizer.tokenize(query))
        
        scored_docs = []
        for doc in self.documents:
            doc_tokens = set(self.tokenizer.tokenize(doc.page_content))
            
            # 교집합 기반 점수 계산
            overlap = len(query_tokens & doc_tokens)
            if overlap > 0:
                # Jaccard 유사도
                union = len(query_tokens | doc_tokens)
                score = overlap / union
                scored_docs.append((score, doc))
        
        # 점수 순으로 정렬
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        return [doc for score, doc in scored_docs[:top_k]]

class HybridRetriever:
    """벡터 + 키워드 하이브리드 검색기"""
    
    def __init__(self, documents: List[str], vector_weight: float = 0.7):
        self.vector_retriever = SimpleVectorRetriever(documents)
        self.keyword_retriever = KeywordRetriever(documents)
        self.vector_weight = vector_weight
        self.keyword_weight = 1.0 - vector_weight
    
    def invoke(self, query: str, top_k: int = 10) -> List[Document]:
        """하이브리드 검색 수행"""
        # 각 검색기에서 결과 가져오기
        vector_results = self.vector_retriever.invoke(query, top_k * 2)
        keyword_results = self.keyword_retriever.invoke(query, top_k * 2)
        
        # 문서별 점수 집계
        doc_scores = {}
        
        # 벡터 검색 점수
        for i, doc in enumerate(vector_results):
            score = (len(vector_results) - i) / len(vector_results)  # 순위 기반 점수
            doc_scores[doc.page_content] = doc_scores.get(doc.page_content, 0) + \
                                         score * self.vector_weight
        
        # 키워드 검색 점수
        for i, doc in enumerate(keyword_results):
            score = (len(keyword_results) - i) / len(keyword_results)
            doc_scores[doc.page_content] = doc_scores.get(doc.page_content, 0) + \
                                         score * self.keyword_weight
        
        # 점수 순으로 정렬
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Document 객체 반환
        result_docs = []
        doc_map = {doc.page_content: doc for doc in 
                  self.vector_retriever.documents}
        
        for content, score in sorted_docs[:top_k]:
            if content in doc_map:
                result_docs.append(doc_map[content])
        
        return result_docs

def main():
    print("🔍 ranx-k 커스텀 검색기 예제")
    print("=" * 50)
    
    # 샘플 문서 컬렉션
    documents = [
        "자연어처리는 컴퓨터가 인간의 언어를 이해하고 처리하는 인공지능 기술입니다.",
        "RAG 시스템은 검색 증강 생성 기술로 정보 검색과 텍스트 생성을 결합합니다.",
        "한국어 토큰화는 교착어적 특성 때문에 형태소 분석이 중요합니다.",
        "정보 검색 시스템의 성능은 정밀도와 재현율로 평가됩니다.",
        "Kiwi는 한국어 형태소 분석에 특화된 오픈소스 라이브러리입니다.",
        "머신러닝 모델 훈련에는 대량의 라벨링된 데이터가 필요합니다.",
        "딥러닝 기반 언어 모델은 트랜스포머 아키텍처를 사용합니다.",
        "검색 엔진 최적화는 웹사이트 가시성을 향상시키는 기법입니다.",
        "텍스트 마이닝은 비구조화된 텍스트에서 유용한 정보를 추출합니다.",
        "추천 시스템은 사용자 선호도를 학습하여 개인화된 콘텐츠를 제공합니다.",
        "컴퓨터 비전 기술은 이미지와 영상을 분석하고 이해합니다.",
        "데이터 전처리는 머신러닝 파이프라인에서 중요한 단계입니다."
    ]
    
    print(f"📚 문서 컬렉션: {len(documents)}개 문서")
    
    # 다양한 검색기 초기화
    vector_retriever = SimpleVectorRetriever(documents)
    keyword_retriever = KeywordRetriever(documents)
    hybrid_retriever = HybridRetriever(documents, vector_weight=0.6)
    
    # 테스트 쿼리
    test_queries = [
        "자연어처리 기술은 무엇인가요?",
        "RAG 시스템의 특징을 알려주세요",
        "한국어 토큰화 방법은?",
        "머신러닝 모델 훈련 과정은?"
    ]
    
    print(f"🔍 테스트 쿼리: {len(test_queries)}개")
    
    # 1. 각 검색기별 결과 비교
    print("\n1️⃣ 검색기별 결과 비교")
    print("-" * 50)
    
    for i, query in enumerate(test_queries[:2]):  # 처음 2개만
        print(f"\n쿼리 {i+1}: {query}")
        print("=" * 40)
        
        # 벡터 검색
        vector_results = vector_retriever.invoke(query, 3)
        print(f"\n🔢 벡터 검색 ({len(vector_results)}개):")
        for j, doc in enumerate(vector_results, 1):
            print(f"  {j}. {doc.page_content[:50]}...")
        
        # 키워드 검색
        keyword_results = keyword_retriever.invoke(query, 3)
        print(f"\n🔤 키워드 검색 ({len(keyword_results)}개):")
        for j, doc in enumerate(keyword_results, 1):
            print(f"  {j}. {doc.page_content[:50]}...")
        
        # 하이브리드 검색
        hybrid_results = hybrid_retriever.invoke(query, 3)
        print(f"\n🔀 하이브리드 검색 ({len(hybrid_results)}개):")
        for j, doc in enumerate(hybrid_results, 1):
            print(f"  {j}. {doc.page_content[:50]}...")
    
    # 2. 성능 평가
    print("\n2️⃣ 검색기 성능 평가")
    print("-" * 30)
    
    # 평가 데이터 준비
    eval_questions = [
        "자연어처리 기술이란?",
        "RAG 시스템 설명",
        "한국어 토큰화 특징",
        "정보 검색 평가 방법"
    ]
    
    eval_references = [
        ["자연어처리는 컴퓨터가 인간의 언어를 이해하고 처리하는 인공지능 기술입니다."],
        ["RAG 시스템은 검색 증강 생성 기술로 정보 검색과 텍스트 생성을 결합합니다."],
        ["한국어 토큰화는 교착어적 특성 때문에 형태소 분석이 중요합니다."],
        ["정보 검색 시스템의 성능은 정밀도와 재현율로 평가됩니다."]
    ]
    
    retrievers = [
        ("벡터 검색기", vector_retriever),
        ("키워드 검색기", keyword_retriever),  
        ("하이브리드 검색기", hybrid_retriever)
    ]
    
    print(f"{'검색기':<15} {'ROUGE-1':<10} {'ROUGE-2':<10} {'ROUGE-L':<10}")
    print("-" * 50)
    
    for name, retriever in retrievers:
        try:
            results = simple_kiwi_rouge_evaluation(
                retriever=retriever,
                questions=eval_questions,
                reference_contexts=eval_references,
                k=3
            )
            
            rouge1 = results.get('kiwi_rouge1@3', 0.0)
            rouge2 = results.get('kiwi_rouge2@3', 0.0)
            rougeL = results.get('kiwi_rougeL@3', 0.0)
            
            print(f"{name:<15} {rouge1:<10.3f} {rouge2:<10.3f} {rougeL:<10.3f}")
            
        except Exception as e:
            print(f"{name:<15} 오류: {str(e)}")
    
    # 3. 성능 분석
    print("\n3️⃣ 성능 특성 분석")
    print("-" * 25)
    
    analysis_query = "머신러닝과 딥러닝의 차이점은?"
    
    print(f"분석 쿼리: {analysis_query}")
    print("\n각 검색기의 특성:")
    
    # 벡터 검색기 분석
    vector_results = vector_retriever.invoke(analysis_query, 5)
    print(f"\n🔢 벡터 검색기:")
    print(f"  - 의미적 유사도 기반")
    print(f"  - 검색 결과: {len(vector_results)}개")
    print(f"  - 장점: 동의어, 유사 개념 검색 가능")
    
    # 키워드 검색기 분석
    keyword_results = keyword_retriever.invoke(analysis_query, 5)
    print(f"\n🔤 키워드 검색기:")
    print(f"  - 정확한 키워드 매칭")
    print(f"  - 검색 결과: {len(keyword_results)}개")
    print(f"  - 장점: 빠른 속도, 정확한 매칭")
    
    # 하이브리드 검색기 분석
    hybrid_results = hybrid_retriever.invoke(analysis_query, 5)
    print(f"\n🔀 하이브리드 검색기:")
    print(f"  - 벡터 + 키워드 결합")
    print(f"  - 검색 결과: {len(hybrid_results)}개")
    print(f"  - 장점: 두 방식의 장점 결합")
    
    print("\n✅ 커스텀 검색기 예제 완료!")
    print("\n💡 구현 가이드:")
    print("1. invoke(query) 메서드만 구현하면 ranx-k와 호환")
    print("2. Document 객체의 page_content 속성 필요")
    print("3. 다양한 검색 알고리즘 조합 가능")

if __name__ == "__main__":
    main()