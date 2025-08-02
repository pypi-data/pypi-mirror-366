#!/usr/bin/env python3
"""
Demo script showing the improved text chunking with LangChain RecursiveCharacterTextSplitter
"""

from lsdembed import LSdembed
from lsdembed.text_processor import TextProcessor

def main():
    print("=== LangChain RecursiveCharacterTextSplitter Demo ===\n")
    
    # Sample text for demonstration
    sample_text = """
    Artificial Intelligence (AI) is a broad field of computer science focused on creating systems capable of performing tasks that typically require human intelligence. These tasks include learning, reasoning, problem-solving, perception, and language understanding.
    
    Machine Learning (ML) is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. It uses algorithms to parse data, learn from it, and make informed decisions or predictions.
    
    Deep Learning is a specialized subset of machine learning that uses artificial neural networks with multiple layers (hence "deep") to model and understand complex patterns in data. It has been particularly successful in areas like image recognition, natural language processing, and speech recognition.
    
    Natural Language Processing (NLP) combines computational linguistics with machine learning and deep learning models to give computers the ability to understand, interpret, and generate human language in a valuable way.
    """
    
    print("1. Testing TextProcessor with different chunk sizes:")
    print("-" * 50)
    
    # Test with small chunks
    processor_small = TextProcessor(chunk_size=200, chunk_overlap=50)
    chunks_small = processor_small.chunk_text(sample_text)
    
    print(f"Small chunks (200 chars, 50 overlap): {len(chunks_small)} chunks")
    for i, chunk in enumerate(chunks_small, 1):
        print(f"  Chunk {i}: {len(chunk)} chars")
        print(f"    Preview: {chunk.strip()[:80]}...")
        print()
    
    # Test with larger chunks
    processor_large = TextProcessor(chunk_size=400, chunk_overlap=100)
    chunks_large = processor_large.chunk_text(sample_text)
    
    print(f"Large chunks (400 chars, 100 overlap): {len(chunks_large)} chunks")
    for i, chunk in enumerate(chunks_large, 1):
        print(f"  Chunk {i}: {len(chunk)} chars")
        print(f"    Preview: {chunk.strip()[:80]}...")
        print()
    
    print("2. Testing LSdembed with single text input:")
    print("-" * 50)
    
    # Create and fit model with single text
    model = LSdembed({'d': 128})
    model.fit(sample_text, chunk_size=250)
    
    print(f"Model fitted with {len(model.chunks)} chunks")
    print(f"Vocabulary size: {len(model.idf_scores)} unique tokens")
    print()
    
    # Test searches
    queries = [
        "machine learning algorithms",
        "neural networks deep learning",
        "natural language understanding",
        "artificial intelligence systems"
    ]
    
    for query in queries:
        print(f"Search query: '{query}'")
        results = model.search(query, top_k=3)
        
        for i, (text, score) in enumerate(results, 1):
            print(f"  Result {i} (score: {score:.3f}):")
            print(f"    {text.strip()[:100]}...")
        print()
    
    print("3. Backward compatibility test with list of texts:")
    print("-" * 50)
    
    # Test with list of texts (backward compatibility)
    texts = [
        "Machine learning is transforming industries worldwide.",
        "Deep learning models require large amounts of data.",
        "Natural language processing enables human-computer interaction.",
        "Artificial intelligence will shape the future of technology."
    ]
    
    model_list = LSdembed({'d': 64})
    model_list.fit(texts, chunk_size=100)
    
    print(f"Model fitted with list input: {len(model_list.chunks)} chunks")
    
    results = model_list.search("machine learning", top_k=2)
    print("Search results:")
    for i, (text, score) in enumerate(results, 1):
        print(f"  Result {i} (score: {score:.3f}): {text}")
    
    print("\n=== Demo completed successfully! ===")

if __name__ == "__main__":
    main()