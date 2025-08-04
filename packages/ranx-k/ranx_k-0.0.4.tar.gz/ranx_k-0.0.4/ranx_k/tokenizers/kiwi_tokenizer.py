"""
Kiwi-based Korean tokenizer for ROUGE evaluation.

This module provides KiwiTokenizer class that integrates Kiwi morphological analyzer
with rouge_score library for accurate Korean text tokenization.

Original concept inspired by rouge_score tokenizers module.
Modified and extended for Korean language support.
"""

import re
from typing import List, Set

try:
    from kiwipiepy import Kiwi
    KIWI_AVAILABLE = True
except ImportError:
    KIWI_AVAILABLE = False


class KiwiTokenizer:
    """
    Kiwi-based Korean tokenizer compatible with rouge_score library.
    
    This tokenizer integrates Kiwi morphological analyzer to provide accurate
    Korean text tokenization for ROUGE evaluation. It supports both morpheme-level
    and noun-only tokenization with Korean stopword filtering.
    
    Args:
        use_stemmer (bool): Compatibility parameter (not used in Kiwi).
        method (str): Tokenization method - 'morphs' or 'nouns'.
        use_stopwords (bool): Whether to filter Korean stopwords.
        
    Example:
        >>> tokenizer = KiwiTokenizer(method='morphs', use_stopwords=True)
        >>> tokens = tokenizer.tokenize("자연어처리는 인공지능의 핵심 기술입니다.")
        >>> print(tokens)
        ['자연어', '처리', '인공', '지능', '핵심', '기술']
    """
    
    def __init__(self, use_stemmer: bool = False, method: str = 'morphs', 
                 use_stopwords: bool = True):
        """
        Initialize KiwiTokenizer.
        
        Args:
            use_stemmer: Compatibility parameter for rouge_score interface.
            method: Tokenization method ('morphs' for morphemes, 'nouns' for nouns only).
            use_stopwords: Whether to remove Korean stopwords.
        """
        if not KIWI_AVAILABLE:
            raise ImportError(
                "Kiwi is required for KiwiTokenizer. Install with: pip install kiwipiepy"
            )
            
        self.kiwi = Kiwi()
        self.method = method
        self.use_stopwords = use_stopwords
        
        # Korean stopwords - can be extended based on needs
        self.korean_stopwords: Set[str] = {
            '은', '는', '이', '가', '을', '를', '에', '의', '로', '으로', '와', '과',
            '도', '만', '라', '이다', '있다', '없다', '하다', '되다', '수', '것',
            '들', '등', '및', '또는', '그리고', '하지만', '그러나', '따라서',
            '그', '이', '저', '그것', '이것', '저것', '여기', '거기', '저기',
            '때문', '위해', '통해', '대해', '에서', '부터', '까지', '동안'
        } if use_stopwords else set()
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text using Kiwi morphological analyzer.
        
        This is the main interface method called by rouge_score library.
        
        Args:
            text: Text to tokenize.
            
        Returns:
            List of tokens.
            
        Example:
            >>> tokenizer = KiwiTokenizer()
            >>> tokens = tokenizer.tokenize("한국어 자연어처리는 어렵습니다.")
            >>> print(tokens)
            ['한국어', '자연어', '처리', '어렵']
        """
        if not text or not text.strip():
            return []
        
        # Preprocess text
        text = self._preprocess_text(text)
        
        try:
            if self.method == 'morphs':
                return self._tokenize_morphs(text)
            elif self.method == 'nouns':
                return self._tokenize_nouns(text)
            else:
                raise ValueError(f"Unsupported tokenization method: {self.method}")
        except Exception as e:
            # Fallback to simple tokenization if Kiwi fails
            return self._fallback_tokenize(text)
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text by removing punctuation and normalizing whitespace.
        
        Args:
            text: Input text.
            
        Returns:
            Preprocessed text.
        """
        # Remove punctuation and normalize whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _tokenize_morphs(self, text: str) -> List[str]:
        """
        Tokenize using morphological analysis.
        
        Extracts meaningful morphemes (nouns, verbs, adjectives, adverbs) 
        while filtering out functional words and stopwords.
        
        Args:
            text: Preprocessed text.
            
        Returns:
            List of morpheme tokens.
        """
        analyzed = self.kiwi.analyze(text)
        tokens = []
        
        for token, pos, _, _ in analyzed[0][0]:
            # Select meaningful POS tags (Nouns, Verbs, Modifiers)
            if (pos.startswith(('N', 'V', 'M')) and 
                len(token) > 1 and 
                token.lower() not in self.korean_stopwords):
                tokens.append(token.lower())
        
        return tokens
    
    def _tokenize_nouns(self, text: str) -> List[str]:
        """
        Extract only nouns from text.
        
        Uses Kiwi's morphological analysis to identify nouns.
        Filters for noun POS tags only.
        
        Args:
            text: Preprocessed text.
            
        Returns:
            List of noun tokens.
        """
        analyzed = self.kiwi.analyze(text)
        tokens = []
        
        for token, pos, _, _ in analyzed[0][0]:
            # Select only noun POS tags (N*)
            if (pos.startswith('N') and 
                len(token) > 1 and 
                token.lower() not in self.korean_stopwords):
                tokens.append(token.lower())
        
        return tokens
    
    def _fallback_tokenize(self, text: str) -> List[str]:
        """
        Fallback tokenization using simple space splitting.
        
        Used when Kiwi analysis fails. Applies basic filtering
        to remove short tokens and stopwords.
        
        Args:
            text: Text to tokenize.
            
        Returns:
            List of space-split tokens.
        """
        return [token.lower() for token in text.split() 
                if len(token) > 1 and token.lower() not in self.korean_stopwords]
    
    def add_stopwords(self, stopwords: List[str]) -> None:
        """
        Add custom stopwords to the existing set.
        
        Args:
            stopwords: List of stopwords to add.
            
        Example:
            >>> tokenizer = KiwiTokenizer()
            >>> tokenizer.add_stopwords(['커스텀', '불용어'])
        """
        self.korean_stopwords.update(stopwords)
    
    def remove_stopwords(self, stopwords: List[str]) -> None:
        """
        Remove stopwords from the existing set.
        
        Args:
            stopwords: List of stopwords to remove.
        """
        self.korean_stopwords.difference_update(stopwords)
    
    def get_stopwords(self) -> Set[str]:
        """
        Get current set of stopwords.
        
        Returns:
            Set of current stopwords.
        """
        return self.korean_stopwords.copy()
