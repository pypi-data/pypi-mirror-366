"""
Similarity-based ranx evaluation for Korean RAG systems.

This module provides ranx-compatible evaluation using semantic similarity
instead of traditional document ID matching. It supports multiple similarity
calculation methods including embedding similarity and Kiwi-based ROUGE.

Based on ranx library concepts: Copyright (c) 2021 Elias Bassani (MIT License)
Extended for semantic similarity evaluation in Korean RAG systems.
"""

import numpy as np
from tqdm import tqdm
from typing import List, Dict, Tuple, Any
import re

try:
    from ranx import Qrels, Run, evaluate
    RANX_AVAILABLE = True
except ImportError:
    RANX_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False

try:
    from rouge_score import rouge_scorer
    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False

try:
    from kiwipiepy import Kiwi
    KIWI_AVAILABLE = True
except ImportError:
    KIWI_AVAILABLE = False

try:
    import openai
    from .openai_similarity import OpenAISimilarityCalculator
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def evaluate_with_ranx_similarity(retriever, questions: List[str], 
                                 reference_contexts: List[List[str]], 
                                 k: int = 5,
                                 method: str = 'embedding', 
                                 similarity_threshold: float = 0.7,
                                 embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                                 use_graded_relevance: bool = False,
                                 evaluation_mode: str = 'reference_based') -> Dict[str, float]:
    """
    Evaluate RAG system using ranx with semantic similarity matching.
    
    This function converts semantic similarity scores into ranx-compatible
    relevance judgments, enabling the use of traditional IR metrics while
    accounting for semantic relatedness rather than exact document ID matching.
    
    Args:
        retriever: RAG retriever object with invoke() method.
        questions: List of questions to evaluate.
        reference_contexts: List of reference document lists for each question.
        k: Number of top retrieved documents to evaluate.
        method: Similarity calculation method ('embedding', 'rouge', 'kiwi_rouge', 'openai').
        similarity_threshold: Minimum similarity score to consider relevant (0.0-1.0).
        embedding_model: Sentence transformer model name for embedding method.
        use_graded_relevance: If True, use similarity scores as relevance grades. 
                             If False, use binary relevance (0 or 1).
        evaluation_mode: 'reference_based' evaluates against all reference documents,
                        'retrieval_based' evaluates only retrieved documents.
        
    Returns:
        Dictionary containing ranx evaluation metrics:
        - hit_rate@k: Hit rate at k
        - ndcg@k: Normalized Discounted Cumulative Gain at k
        - map@k: Mean Average Precision at k  
        - mrr: Mean Reciprocal Rank
        
    Examples:
        Basic usage with default embedding model:
        >>> from ranx_k.evaluation import evaluate_with_ranx_similarity
        >>> results = evaluate_with_ranx_similarity(
        ...     retriever=my_retriever,
        ...     questions=["RAG 시스템이란?"],
        ...     reference_contexts=[["RAG는 검색 증강 생성..."]], 
        ...     k=5,
        ...     method='embedding',
        ...     similarity_threshold=0.6
        ... )
        >>> print(f"Hit@5: {results['hit_rate@5']:.3f}")
        
        Using different embedding models:
        >>> # More accurate multilingual model
        >>> results = evaluate_with_ranx_similarity(
        ...     retriever=my_retriever,
        ...     questions=questions,
        ...     reference_contexts=references,
        ...     method='embedding',
        ...     similarity_threshold=0.7,
        ...     embedding_model="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        ... )
        
        >>> # Latest BGE-M3 model
        >>> results = evaluate_with_ranx_similarity(
        ...     retriever=my_retriever,
        ...     questions=questions,
        ...     reference_contexts=references,
        ...     method='embedding',
        ...     embedding_model="BAAI/bge-m3"
        ... )
        
        Reference-based evaluation (properly calculates recall):
        >>> results = evaluate_with_ranx_similarity(
        ...     retriever=my_retriever,
        ...     questions=questions,
        ...     reference_contexts=references,
        ...     method='kiwi_rouge',
        ...     similarity_threshold=0.3,
        ...     evaluation_mode='reference_based'  # Evaluates against all reference docs
        ... )
        
        Using graded relevance instead of binary:
        >>> results = evaluate_with_ranx_similarity(
        ...     retriever=my_retriever,
        ...     questions=questions,
        ...     reference_contexts=references,
        ...     method='embedding',
        ...     use_graded_relevance=True,  # Uses similarity scores as relevance grades
        ...     evaluation_mode='reference_based'
        ... )
        
        Using Korean-optimized Kiwi ROUGE:
        >>> results = evaluate_with_ranx_similarity(
        ...     retriever=my_retriever,
        ...     questions=questions,
        ...     reference_contexts=references,
        ...     method='kiwi_rouge',
        ...     similarity_threshold=0.3  # Lower threshold for Kiwi ROUGE
        ... )
        
        Using OpenAI Embeddings:
        >>> results = evaluate_with_ranx_similarity(
        ...     retriever=my_retriever,
        ...     questions=questions,
        ...     reference_contexts=references,
        ...     method='openai',
        ...     similarity_threshold=0.7,
        ...     embedding_model="text-embedding-3-small"  # OpenAI model name
        ... )
        
    Raises:
        ImportError: If required dependencies are not installed.
    """
    if not RANX_AVAILABLE:
        raise ImportError(
            "ranx is required for this evaluation. Install with: pip install ranx"
        )
    
    print(f"🔍 Starting similarity-based ranx evaluation | 유사도 기반 ranx 평가 시작")
    print(f"   Method | 방법: {method}, Threshold | 임계값: {similarity_threshold}, Mode | 모드: {evaluation_mode}")
    
    # Initialize similarity calculator based on method
    if method == 'embedding':
        if not EMBEDDING_AVAILABLE:
            raise ImportError(
                "sentence-transformers and scikit-learn required for embedding method. "
                "Install with: pip install sentence-transformers scikit-learn"
            )
        similarity_calculator = EmbeddingSimilarityCalculator(model_name=embedding_model)
    elif method == 'rouge':
        if not ROUGE_AVAILABLE:
            raise ImportError(
                "rouge_score required for rouge method. Install with: pip install rouge-score"
            )
        similarity_calculator = RougeSimilarityCalculator()
    elif method == 'kiwi_rouge':
        if not KIWI_AVAILABLE:
            raise ImportError(
                "kiwipiepy required for kiwi_rouge method. Install with: pip install kiwipiepy"
            )
        similarity_calculator = KiwiRougeSimilarityCalculator()
    elif method == 'openai':
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai required for openai method. Install with: pip install openai"
            )
        similarity_calculator = OpenAISimilarityCalculator(model_name=embedding_model)
    else:
        raise ValueError(f"Unsupported similarity method: {method}")
    
    qrels_dict = {}
    run_dict = {}
    
    # Track total retrieved documents
    total_retrieved_docs = 0
    
    for i, (question, ref_docs) in tqdm(enumerate(zip(questions, reference_contexts)), 
                                       desc="ranx similarity evaluation | ranx 유사도 평가",
                                       total=len(questions)):
        query_id = f"q_{i+1}"
        
        # Retrieve documents
        retrieved_docs = retriever.invoke(question)[:k]
        retrieved_texts = [doc.page_content for doc in retrieved_docs]
        total_retrieved_docs += len(retrieved_docs)
        
        # Extract reference texts
        ref_texts = []
        for ref_doc in ref_docs:
            ref_text = ref_doc.page_content if hasattr(ref_doc, 'page_content') else ref_doc
            ref_texts.append(ref_text)
        
        # Calculate similarity matrix (reference docs x retrieved docs)
        similarity_matrix = similarity_calculator.calculate_similarity_matrix(
            ref_texts, retrieved_texts
        )
        
        # Build qrels and run based on evaluation mode
        qrels_dict[query_id] = {}
        run_dict[query_id] = {}
        
        if evaluation_mode == 'reference_based':
            # Reference-based evaluation: Include all reference documents in qrels
            # This properly evaluates recall
            
            # First, add all reference documents to qrels
            for ref_idx, ref_text in enumerate(ref_texts):
                ref_doc_id = f"ref_{ref_idx}"
                if use_graded_relevance:
                    qrels_dict[query_id][ref_doc_id] = 1.0  # All reference docs have relevance 1.0
                else:
                    qrels_dict[query_id][ref_doc_id] = 1.0
            
            # Then, check which reference documents were retrieved
            for ref_idx, ref_text in enumerate(ref_texts):
                ref_doc_id = f"ref_{ref_idx}"
                
                # Find best matching retrieved document for this reference
                if similarity_matrix.shape[1] > 0:
                    similarities = similarity_matrix[ref_idx, :]
                    best_match_idx = np.argmax(similarities)
                    best_similarity = similarities[best_match_idx]
                    
                    # Add to run if similarity is above threshold
                    if best_similarity >= similarity_threshold:
                        run_dict[query_id][ref_doc_id] = float(best_similarity)
                        
            # Also add non-reference retrieved documents with low scores
            for j, ret_text in enumerate(retrieved_texts):
                # Check if this retrieved doc matches any reference
                if similarity_matrix.shape[0] > 0:
                    max_sim_to_any_ref = np.max(similarity_matrix[:, j])
                    if max_sim_to_any_ref < similarity_threshold:
                        # This is a non-relevant retrieved document
                        non_ref_id = f"non_ref_{j}"
                        run_dict[query_id][non_ref_id] = 0.0
                        
        else:
            # Retrieval-based evaluation: Original behavior
            for j, ret_text in enumerate(retrieved_texts):
                doc_id = f"doc_{j}"
                
                # Find maximum similarity with any reference document
                max_similarity = np.max(similarity_matrix[:, j]) if similarity_matrix.shape[0] > 0 else 0
                
                # Add to run (all retrieved documents with their similarity scores)
                run_dict[query_id][doc_id] = float(max_similarity)
                
                # Add to qrels based on relevance
                if use_graded_relevance:
                    # Use actual similarity score as relevance grade
                    if max_similarity >= similarity_threshold:
                        qrels_dict[query_id][doc_id] = float(max_similarity)
                else:
                    # Binary relevance
                    if max_similarity >= similarity_threshold:
                        qrels_dict[query_id][doc_id] = 1.0
        
        # Debug info for first few queries
        if i < 3:
            print(f"\n🔍 Question | 질문 {i+1}: {question[:50]}...")
            print(f"📊 Reference docs | 참조 문서: {len(ref_texts)}, Retrieved docs | 검색 문서: {len(retrieved_texts)}")
            print(f"📊 Similarity matrix shape | 유사도 매트릭스 shape: {similarity_matrix.shape}")
            if similarity_matrix.size > 0:
                print(f"📈 Max similarity | 최대 유사도: {np.max(similarity_matrix):.3f}")
            print(f"📋 Qrels items | qrels 항목 수: {len(qrels_dict[query_id])}")
            print(f"📋 Run items | run 항목 수: {len(run_dict[query_id])}")
            if evaluation_mode == 'reference_based':
                retrieved_count = len([doc for doc in run_dict[query_id] if doc.startswith('ref_')])
                print(f"📋 Retrieved reference docs | 검색된 참조 문서: {retrieved_count}/{len(ref_texts)}")
            print("-" * 50)
    
    # Evaluate using ranx
    try:
        qrels = Qrels(qrels_dict)
        run = Run(run_dict)
        
        # Calculate IR metrics
        metrics = [f"hit_rate@{k}", f"ndcg@{k}", f"map@{k}", "mrr"]
        results = evaluate(qrels, run, metrics)
        
        print(f"\n📊 Similarity-based ranx evaluation results | 유사도 기반 ranx 평가 결과 ({method}):")
        for metric, score in results.items():
            print(f"  {metric}: {score:.3f}")
        
        # Additional analysis information
        total_relevant_docs = sum(len(qrels) for qrels in qrels_dict.values())
        total_queries = len(qrels_dict)
        avg_relevant_per_query = total_relevant_docs / total_queries if total_queries > 0 else 0
        
        print(f"\n📈 Analysis information | 분석 정보:")
        print(f"  Total queries | 총 질문 수: {total_queries}")
        print(f"  Total retrieved docs | 총 검색 문서 수: {total_retrieved_docs}")
        print(f"  Avg docs per query | 질문당 평균 검색 문서: {total_retrieved_docs/total_queries:.1f}")
        print(f"  Total relevant docs | 관련 문서 총 개수: {total_relevant_docs}")
        print(f"  Avg relevant per query | 질문당 평균 관련 문서: {avg_relevant_per_query:.1f}")
        print(f"  Threshold used | 사용된 임계값: {similarity_threshold}")
        
        if evaluation_mode == 'reference_based':
            total_retrieved = sum(len([doc for doc in run[query_id] if doc.startswith('ref_')]) 
                                for query_id in run_dict)
            total_reference = sum(len(ref_docs) for ref_docs in reference_contexts)
            overall_recall = total_retrieved / total_reference if total_reference > 0 else 0
            print(f"  Overall recall | 전체 재현율: {overall_recall:.3f} ({total_retrieved}/{total_reference})")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during ranx evaluation | ranx 평가 중 오류: {e}")
        print("💡 qrels or run may be empty. Try lowering the threshold | qrels나 run이 비어있을 가능성이 있습니다. 임계값을 낮춰보세요.")
        return {}


class EmbeddingSimilarityCalculator:
    """Embedding-based similarity calculator using sentence transformers."""
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize embedding similarity calculator.
        
        Args:
            model_name: Name of the sentence transformer model to use.
        """
        self.model = SentenceTransformer(model_name)
    
    def calculate_similarity_matrix(self, ref_texts: List[str], 
                                   ret_texts: List[str]) -> np.ndarray:
        """
        Calculate cosine similarity matrix between reference and retrieved texts.
        
        Args:
            ref_texts: List of reference text strings.
            ret_texts: List of retrieved text strings.
            
        Returns:
            2D numpy array with shape (len(ref_texts), len(ret_texts)).
        """
        if not ref_texts or not ret_texts:
            return np.array([[]])
        
        ref_embeddings = self.model.encode(ref_texts)
        ret_embeddings = self.model.encode(ret_texts)
        
        return cosine_similarity(ref_embeddings, ret_embeddings)


class RougeSimilarityCalculator:
    """ROUGE-based similarity calculator using rouge_score library."""
    
    def __init__(self):
        """Initialize ROUGE similarity calculator."""
        self.scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'])
    
    def calculate_similarity_matrix(self, ref_texts: List[str], 
                                   ret_texts: List[str]) -> np.ndarray:
        """
        Calculate ROUGE-L F1 similarity matrix.
        
        Args:
            ref_texts: List of reference text strings.
            ret_texts: List of retrieved text strings.
            
        Returns:
            2D numpy array with ROUGE-L F1 scores.
        """
        if not ref_texts or not ret_texts:
            return np.array([[]])
        
        similarity_matrix = np.zeros((len(ref_texts), len(ret_texts)))
        
        for i, ref_text in enumerate(ref_texts):
            for j, ret_text in enumerate(ret_texts):
                scores = self.scorer.score(ref_text, ret_text)
                # Use ROUGE-L F1 score as similarity measure
                similarity_matrix[i, j] = scores['rougeL'].fmeasure
        
        return similarity_matrix


class KiwiRougeSimilarityCalculator:
    """Kiwi + ROUGE similarity calculator for Korean text."""
    
    def __init__(self):
        """Initialize Kiwi ROUGE similarity calculator."""
        self.kiwi = Kiwi()
        self.korean_stopwords = {
            '은', '는', '이', '가', '을', '를', '에', '의', '로', '도', '만', 
            '하다', '되다', '있다', '것', '들', '등', '및', '또는', '그리고'
        }
    
    def tokenize_with_kiwi(self, text: str) -> List[str]:
        """
        Tokenize Korean text using Kiwi morphological analyzer.
        
        Args:
            text: Text to tokenize.
            
        Returns:
            List of meaningful Korean morphemes.
        """
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        try:
            analyzed = self.kiwi.analyze(text)
            tokens = []
            for token, pos, _, _ in analyzed[0][0]:
                if (pos.startswith(('N', 'V', 'M')) and 
                    len(token) > 1 and 
                    token.lower() not in self.korean_stopwords):
                    tokens.append(token.lower())
            return tokens
        except:
            return [t.lower() for t in text.split() 
                   if len(t) > 1 and t.lower() not in self.korean_stopwords]
    
    def calculate_rouge_score(self, ref_tokens: List[str], ret_tokens: List[str]) -> float:
        """
        Calculate ROUGE-L F1 score between token lists.
        
        Args:
            ref_tokens: Reference document tokens.
            ret_tokens: Retrieved document tokens.
            
        Returns:
            ROUGE-L F1 score.
        """
        if not ref_tokens or not ret_tokens:
            return 0.0
        
        # Calculate Longest Common Subsequence
        def lcs_length(a: List[str], b: List[str]) -> int:
            """Calculate LCS length using dynamic programming."""
            m, n = len(a), len(b)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if a[i-1] == b[j-1]:
                        dp[i][j] = dp[i-1][j-1] + 1
                    else:
                        dp[i][j] = max(dp[i-1][j], dp[i][j-1])
            return dp[m][n]
        
        lcs = lcs_length(ref_tokens, ret_tokens)
        
        # Calculate F1 score
        precision = lcs / len(ret_tokens) if ret_tokens else 0
        recall = lcs / len(ref_tokens) if ref_tokens else 0
        
        if precision + recall == 0:
            return 0.0
        
        f1 = 2 * (precision * recall) / (precision + recall)
        return f1
    
    def calculate_similarity_matrix(self, ref_texts: List[str], 
                                   ret_texts: List[str]) -> np.ndarray:
        """
        Calculate Kiwi ROUGE similarity matrix.
        
        Args:
            ref_texts: List of reference text strings.
            ret_texts: List of retrieved text strings.
            
        Returns:
            2D numpy array with Kiwi ROUGE-L F1 scores.
        """
        if not ref_texts or not ret_texts:
            return np.array([[]])
        
        similarity_matrix = np.zeros((len(ref_texts), len(ret_texts)))
        
        for i, ref_text in enumerate(ref_texts):
            ref_tokens = self.tokenize_with_kiwi(ref_text)
            
            for j, ret_text in enumerate(ret_texts):
                ret_tokens = self.tokenize_with_kiwi(ret_text)
                similarity_matrix[i, j] = self.calculate_rouge_score(ref_tokens, ret_tokens)
        
        return similarity_matrix


def compare_ranx_methods(retriever, questions: List[str], 
                        reference_contexts: List[List[str]], 
                        k: int = 5) -> Dict[str, Dict[str, float]]:
    """
    Compare different similarity methods for ranx evaluation.
    
    This function evaluates the same RAG system using different similarity
    calculation methods and provides a comprehensive comparison.
    
    Args:
        retriever: RAG retriever object.
        questions: List of questions to evaluate.
        reference_contexts: List of reference document lists.
        k: Number of top documents to evaluate.
        
    Returns:
        Dictionary containing comparison results for each method.
        
    Example:
        >>> from krag.evaluation.similarity_ranx import compare_ranx_methods
        >>> comparison = compare_ranx_methods(
        ...     retriever=my_retriever,
        ...     questions=questions,
        ...     reference_contexts=references,
        ...     k=5
        ... )
        >>> print("Method comparison completed!")
    """
    print("🔍 ranx Similarity Method Comparison Evaluation | ranx 유사도 방법 비교 평가")
    print("="*60)
    
    methods = {
        'embedding': '임베딩 유사도',
        'rouge': '기본 ROUGE',
        'kiwi_rouge': 'Kiwi ROUGE'
    }
    
    all_results = {}
    
    for method_key, method_name in methods.items():
        print(f"\n🚀 Evaluating {method_name} | {method_name} 평가 중...")
        
        try:
            results = evaluate_with_ranx_similarity(
                retriever, questions, reference_contexts, 
                k=k, method=method_key, similarity_threshold=0.5
            )
            
            if results:
                all_results[method_name] = results
            else:
                print(f"❌ {method_name} Evaluation Failed | {method_name} 평가 실패")
                
        except Exception as e:
            print(f"❌ Error during {method_name} evaluation | {method_name} 평가 중 오류: {e}")
    
    # Results comparison
    if all_results:
        print("\n🏆 ranx Method Performance Comparison | ranx 방법별 성능 비교:")
        print("="*60)
        
        for metric in ['hit_rate@5', 'ndcg@5', 'map@5', 'mrr']:
            print(f"\n📊 {metric}:")
            
            for method_name, results in all_results.items():
                if metric in results:
                    score = results[metric]
                    print(f"  {method_name:15s}: {score:.3f}")
    
    return all_results
