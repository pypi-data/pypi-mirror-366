# ranx-k: Korean-optimized ranx IR Evaluation Toolkit 🇰🇷

[![PyPI version](https://badge.fury.io/py/ranx-k.svg)](https://badge.fury.io/py/ranx-k)
[![Python version](https://img.shields.io/pypi/pyversions/ranx-k.svg)](https://pypi.org/project/ranx-k/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**ranx-k**는 한국어에 최적화된 정보 검색(IR) 평가 도구로, 기존 ranx 라이브러리를 확장하여 Kiwi 토크나이저와 한국어 임베딩을 지원합니다. RAG(Retrieval-Augmented Generation) 시스템의 성능을 정확하게 평가할 수 있습니다.

## 🚀 주요 특징

- **한국어 특화**: Kiwi 형태소 분석기를 활용한 정확한 토큰화
- **ranx 기반**: 검증된 IR 평가 메트릭 (Hit@K, NDCG@K, MRR 등) 지원
- **LangChain 호환**: LangChain 검색기 인터페이스 표준 지원
- **다양한 평가 방법**: ROUGE, 임베딩 유사도, 의미적 유사도 기반 평가
- **실용적 설계**: 프로토타입부터 프로덕션까지 단계별 평가 지원
- **높은 성능**: 기존 방법 대비 30~80% 한국어 평가 정확도 향상
- **이중언어 출력**: 국제적 접근성을 위한 영어-한국어 병기 출력 지원

## 📦 설치

```bash
pip install ranx-k
```

또는 개발 버전 설치:

```bash
pip install "ranx-k[dev]"
```

## 🔗 검색기 호환성

ranx-k는 **LangChain 검색기 인터페이스**를 지원합니다:

```python
# 검색기는 invoke() 메서드를 구현해야 합니다
class YourRetriever:
    def invoke(self, query: str) -> List[Document]:
        # Document 객체 리스트 반환 (page_content 속성 필요)
        pass

# LangChain Document 사용 예시
from langchain.schema import Document
doc = Document(page_content="텍스트 내용")
```

> **참고**: LangChain은 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [문서](docs/en/quickstart.md#langchain-license)를 참조하세요.

## 🔧 빠른 시작

### 기본 사용법

```python
from ranx_k.evaluation import simple_kiwi_rouge_evaluation

# 간단한 Kiwi ROUGE 평가
results = simple_kiwi_rouge_evaluation(
    retriever=your_retriever,
    questions=your_questions,
    reference_contexts=your_reference_contexts,
    k=5
)

print(f"ROUGE-1: {results['kiwi_rouge1@5']:.3f}")
print(f"ROUGE-2: {results['kiwi_rouge2@5']:.3f}")
print(f"ROUGE-L: {results['kiwi_rougeL@5']:.3f}")
```

### 향상된 평가 (Rouge Score + Kiwi)

```python
from ranx_k.evaluation import rouge_kiwi_enhanced_evaluation

# 검증된 rouge_score 라이브러리 + Kiwi 토크나이저
results = rouge_kiwi_enhanced_evaluation(
    retriever=your_retriever,
    questions=your_questions,
    reference_contexts=your_reference_contexts,
    k=5,
    tokenize_method='morphs',  # 'morphs' 또는 'nouns'
    use_stopwords=True
)
```

### 의미적 유사도 기반 ranx 평가

```python
from ranx_k.evaluation import evaluate_with_ranx_similarity

# 의미적 유사도를 ranx 형식으로 변환
results = evaluate_with_ranx_similarity(
    retriever=your_retriever,
    questions=your_questions,
    reference_contexts=your_reference_contexts,
    k=5,
    method='kiwi_rouge',  # 'embedding', 'kiwi_rouge'
    similarity_threshold=0.6
)

print(f"Hit@5: {results['hit_rate@5']:.3f}")
print(f"NDCG@5: {results['ndcg@5']:.3f}")
print(f"MRR: {results['mrr']:.3f}")
```

### 종합 평가

```python
from ranx_k.evaluation import comprehensive_evaluation_comparison

# 모든 평가 방법 비교
comparison = comprehensive_evaluation_comparison(
    retriever=your_retriever,
    questions=your_questions,
    reference_contexts=your_reference_contexts,
    k=5
)
```

## 📊 평가 방법

### 1. Kiwi ROUGE 평가
- **장점**: 빠른 속도, 직관적 해석
- **용도**: 프로토타이핑, 빠른 피드백

### 2. Enhanced ROUGE (Rouge Score + Kiwi)
- **장점**: 검증된 라이브러리, 안정성
- **용도**: 프로덕션 환경, 신뢰성 중요한 평가

### 3. 의미적 유사도 기반 ranx
- **장점**: 전통적 IR 메트릭, 의미적 유사도
- **용도**: 연구, 벤치마킹, 상세 분석

## 🎯 성능 개선 사례

```python
# 기존 방법 (영어 토크나이저)
basic_rouge1 = 0.234

# ranx-k (Kiwi 토크나이저)
ranxk_rouge1 = 0.421  # +79.9% 향상!
```

## 📈 점수 해석 가이드

| 점수 범위 | 평가 | 권장 조치 |
|-----------|------|-----------|
| 0.7 이상 | 🟢 매우 좋음 | 현재 설정 유지 |
| 0.5~0.7 | 🟡 양호 | 미세 조정 고려 |
| 0.3~0.5 | 🟠 보통 | 개선 필요 |
| 0.3 미만 | 🔴 낮음 | 시스템 재검토 |

## 📚 문서화

자세한 사용법과 예제는 [GitHub 문서](https://github.com/tsdata/rank-k/tree/main/docs)를 참조하세요.

## 🤝 기여하기

ranx-k는 오픈소스 프로젝트입니다. 기여를 환영합니다!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

### 라이선스 및 저작권

이 프로젝트는 다음 오픈소스 라이브러리들을 기반으로 개발되었습니다:

- **rouge_score**: Copyright (c) 2022 The rouge_score Authors (Apache License 2.0)
- **ranx**: Copyright (c) 2021 Elias Bassani (MIT License)  
- **kiwipiepy**: Copyright (c) 2021 bab2min (LGPL v3.0)
- **수정 및 확장**: Copyright (c) 2025 Pandas Studio (MIT License)

## 🙏 감사의 말

- **ranx**: 뛰어난 IR 평가 라이브러리를 제공해주신 [Elias Bassani](https://github.com/AmenRa)님
- **Kiwi**: 뛰어난 한국어 형태소 분석기를 제공해주신 [bab2min](https://github.com/bab2min)님
- **rouge_score**: Google Research팀의 ROUGE 구현

## 📞 지원

- 🐛 버그 리포트: [GitHub Issues](https://github.com/tsdata/rank-k/issues)
- 💬 질문 및 토론: [GitHub Issues](https://github.com/tsdata/rank-k/issues)
- 📧 이메일: ontofinance@gmail.com

---

**ranx-k와 함께 더 정확한 한국어 IR 평가를 경험해보세요!** 🚀🇰🇷