import time
import pytest
from lsdembed import LSdembed

def test_embedding_speed():
    model = LSdembed()
    # Generate test data
    texts = ["Test text " * 100] * 1000
    
    start_time = time.time()
    model.fit(texts)
    fit_time = time.time() - start_time
    
    start_time = time.time()
    results = model.search("test query")
    search_time = time.time() - start_time
    
    assert fit_time < 30.0  # Should fit 1000 chunks in under 30s
    assert search_time < 0.1  # Should search in under 100ms