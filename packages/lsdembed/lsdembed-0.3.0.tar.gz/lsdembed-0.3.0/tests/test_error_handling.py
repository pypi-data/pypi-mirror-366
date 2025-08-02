import pytest
import numpy as np
import tempfile
import os
from pathlib import Path
from lsdembed import LSdembed
from lsdembed.text_processor import TextProcessor


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_empty_texts_input(self):
        """Test handling of empty text input"""
        model = LSdembed()
        
        # Empty list should not crash
        model.fit([])
        assert model.is_fitted
        
        # Empty strings should not crash
        model.fit(["", "   ", "\n\n"])
        assert model.is_fitted
    
    def test_invalid_parameters(self):
        """Test invalid parameter handling"""
        # Negative dimension should be handled gracefully
        with pytest.raises((ValueError, RuntimeError)):
            model = LSdembed({'d': -10})
            model.fit(["test text"])
        
        # Zero dimension should be handled
        with pytest.raises((ValueError, RuntimeError)):
            model = LSdembed({'d': 0})
            model.fit(["test text"])
        
        # Invalid alpha/beta values
        model = LSdembed({'alpha': -1.0, 'beta': -1.0})
        # Should not crash but may produce unexpected results
        model.fit(["test text"])
    
    def test_memory_limits(self):
        """Test behavior with large inputs"""
        model = LSdembed({'d': 32})  # Small dimension for memory efficiency
        
        # Very large text should be handled
        large_text = "word " * 10000
        model.fit([large_text])
        
        # Many small texts
        many_texts = ["text " + str(i) for i in range(1000)]
        model.fit(many_texts)
        
        assert model.is_fitted
    
    def test_concurrent_access(self):
        """Test thread safety of search operations"""
        import threading
        import time
        
        model = LSdembed({'d': 64})
        texts = ["Sample text " + str(i) for i in range(100)]
        model.fit(texts)
        
        results = []
        errors = []
        
        def search_worker():
            try:
                for _ in range(10):
                    result = model.search("sample", top_k=3)
                    results.append(result)
                    time.sleep(0.01)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=search_worker)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Should have no errors and consistent results
        assert len(errors) == 0
        assert len(results) > 0
    
    def test_file_permission_errors(self):
        """Test file I/O error handling"""
        model = LSdembed({'d': 32})
        model.fit(["test text"])
        
        # Try to save to invalid path
        with pytest.raises((OSError, PermissionError, FileNotFoundError)):
            model.save_model("/invalid/path/model.pkl")
        
        # Try to load non-existent file
        with pytest.raises((FileNotFoundError, OSError)):
            model.load_model("non_existent_file.pkl")
    
    def test_corrupted_model_file(self):
        """Test loading corrupted model files"""
        model = LSdembed({'d': 32})
        model.fit(["test text"])
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_file:
            # Write corrupted data
            tmp_file.write(b"corrupted data")
            tmp_file.flush()
            
            # Should raise appropriate error
            with pytest.raises((pickle.UnpicklingError, EOFError, ValueError)):
                import pickle
                model.load_model(tmp_file.name)
            
            os.unlink(tmp_file.name)
    
    def test_unicode_handling(self):
        """Test Unicode and special character handling"""
        model = LSdembed({'d': 32})
        
        # Unicode text
        unicode_texts = [
            "Hello 世界",
            "Café résumé naïve",
            "🚀 Emoji text 🎉",
            "Mixed: αβγ δεζ ηθι",
            "RTL: مرحبا بالعالم"
        ]
        
        model.fit(unicode_texts)
        results = model.search("world", top_k=2)
        
        assert len(results) >= 0  # Should not crash
    
    def test_extreme_chunk_sizes(self):
        """Test extreme chunk size values"""
        model = LSdembed({'d': 32})
        text = "This is a test text with multiple sentences. " * 10
        
        # Very small chunk size
        model.fit([text], chunk_size=10)
        assert model.is_fitted
        
        # Very large chunk size
        model.fit([text], chunk_size=10000)
        assert model.is_fitted
    
    def test_export_format_errors(self):
        """Test export format error handling"""
        model = LSdembed({'d': 32})
        model.fit(["test text"])
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Invalid format
            with pytest.raises(ValueError, match="Unsupported format"):
                model.export_embeddings(
                    Path(tmp_dir) / "test.xyz", 
                    format='invalid_format'
                )
    
    def test_search_edge_cases(self):
        """Test search with edge case queries"""
        model = LSdembed({'d': 32})
        model.fit(["The quick brown fox", "jumps over lazy dog"])
        
        # Empty query
        results = model.search("", top_k=1)
        assert len(results) >= 0
        
        # Very long query
        long_query = "word " * 1000
        results = model.search(long_query, top_k=1)
        assert len(results) >= 0
        
        # Special characters only
        results = model.search("!@#$%^&*()", top_k=1)
        assert len(results) >= 0
        
        # Top_k larger than corpus
        results = model.search("fox", top_k=100)
        assert len(results) <= 2  # Should not exceed corpus size


class TestTextProcessorEdgeCases:
    """Test TextProcessor edge cases"""
    
    def test_empty_input(self):
        processor = TextProcessor()
        
        # Empty string tokenization
        tokens = processor.tokenize("")
        assert tokens == []
        
        # Empty string chunking
        chunks = processor.chunk_text("")
        assert chunks == []
    
    def test_special_characters(self):
        processor = TextProcessor()
        
        # Only special characters
        tokens = processor.tokenize("!@#$%^&*()")
        assert len(tokens) == 0  # Default pattern only matches word characters
        
        # Mixed content
        tokens = processor.tokenize("Hello! How are you?")
        assert "hello" in tokens  # tokenizer converts to lowercase
        assert "how" in tokens
        assert "!" not in tokens
    
    def test_custom_token_pattern(self):
        # Custom pattern that includes punctuation
        processor = TextProcessor(token_pattern=r'[\w!?]+')
        tokens = processor.tokenize("Hello! How are you?")
        
        assert len(tokens) > 0
    
    def test_idf_calculation_edge_cases(self):
        processor = TextProcessor()
        
        # Empty chunks
        idf_scores = processor.calculate_idf([])
        assert len(idf_scores) == 0
        
        # Single chunk
        idf_scores = processor.calculate_idf(["hello world"])
        assert len(idf_scores) > 0
        
        # Duplicate chunks
        idf_scores = processor.calculate_idf(["hello world", "hello world"])
        assert "hello" in idf_scores
        assert "world" in idf_scores


class TestMemoryStress:
    """Memory stress tests"""
    
    @pytest.mark.slow
    def test_large_corpus_handling(self):
        """Test handling of large corpus (marked as slow test)"""
        model = LSdembed({'d': 64})
        
        # Generate large corpus
        large_corpus = []
        for i in range(5000):
            text = f"Document {i} contains various words and phrases. " * 5
            large_corpus.append(text)
        
        # Should handle large corpus without crashing
        model.fit(large_corpus, chunk_size=200)
        
        # Search should still work
        results = model.search("document", top_k=10)
        assert len(results) > 0
    
    @pytest.mark.slow
    def test_high_dimensional_embeddings(self):
        """Test high-dimensional embeddings (marked as slow test)"""
        model = LSdembed({'d': 1024})  # High dimension
        texts = ["Sample text " + str(i) for i in range(100)]
        
        model.fit(texts)
        results = model.search("sample", top_k=5)
        
        assert len(results) > 0
        assert model.get_model_info()['embedding_dimension'] == 1024