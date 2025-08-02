import re
import math
from collections import defaultdict
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter

class TextProcessor:
    def __init__(self, token_pattern: str = r'\w+', chunk_size: int = 300, chunk_overlap: int = 50):
        self.token_pattern = re.compile(token_pattern)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def tokenize(self, text: str) -> List[str]:
        return [token.lower() for token in self.token_pattern.findall(text)]
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Splits input text into chunks using LangChain's RecursiveCharacterTextSplitter.
        This provides better performance and more intelligent splitting.
        """
        chunks = self.text_splitter.split_text(text)
        return [chunk.strip() for chunk in chunks if chunk.strip()]
    
    def calculate_idf(self, chunks: List[str]) -> Dict[str, float]:
        """Calculates Inverse Document Frequency for semantic mass."""
        doc_freq = defaultdict(int)
        total_docs = len(chunks)
        for chunk in chunks:
            tokens_in_chunk = set(self.tokenize(chunk))
            for token in tokens_in_chunk:
                doc_freq[token] += 1
                
        idf_scores = {
            token: math.log(total_docs / (count + 1))
            for token, count in doc_freq.items()
        }
        print(f"Calculated IDF for {len(idf_scores)} unique tokens.")
        return idf_scores