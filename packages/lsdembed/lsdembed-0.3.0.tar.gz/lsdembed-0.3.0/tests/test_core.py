import pytest
import numpy as np
import tempfile
import os
from pathlib import Path
from lsdembed import LSdembed

class TestLSdembed:
    def test_basic_functionality(self):
        model = LSdembed()
        texts = ["Sample text one", "Another sample text"]
        model.fit(texts)
        results = model.search("sample", top_k=2)
        assert len(results) == 2
    
    def test_parameter_updates(self):
        model = LSdembed()
        model.update_params(alpha=2.0, beta=1.0)
        params = model.engine.get_params()
        assert params.alpha == 2.0
        assert params.beta == 1.0
    
    def test_save_and_load_model(self):
        # Create and fit model
        model = LSdembed({'d': 64, 'alpha': 1.5})  # Smaller dimension for faster tests
        texts = ["Test document one", "Test document two", "Another test document"]
        model.fit(texts)
        
        # Test search before saving
        original_results = model.search("test", top_k=2)
        
        # Save model
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_file:
            model.save_model(tmp_file.name)
            
            # Load model into new instance
            loaded_model = LSdembed.from_pretrained(tmp_file.name + '.gz')
            
            # Test that loaded model produces same results
            loaded_results = loaded_model.search("test", top_k=2)
            
            assert len(loaded_results) == len(original_results)
            
            # Compare embeddings (should be identical)
            original_emb = model.embed_query("test")
            loaded_emb = loaded_model.embed_query("test")
            np.testing.assert_array_almost_equal(original_emb, loaded_emb, decimal=5)
            
            # Clean up
            os.unlink(tmp_file.name + '.gz')
    
    def test_model_info(self):
        model = LSdembed({'d': 128})
        texts = ["Sample text"] * 10
        model.fit(texts)
        
        info = model.get_model_info()
        assert info['status'] == 'fitted'
        assert info['num_chunks'] == 10
        assert info['embedding_dimension'] == 128
        assert 'memory_usage_mb' in info
    
    def test_export_embeddings(self):
        model = LSdembed({'d': 32})
        texts = ["Test text one", "Test text two"]
        model.fit(texts)
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Test NPZ export
            npz_path = Path(tmp_dir) / "embeddings.npz"
            model.export_embeddings(npz_path, format='npz')
            assert npz_path.exists()
            
            # Load and verify NPZ
            data = np.load(npz_path, allow_pickle=True)
            assert 'embeddings' in data
            assert 'chunks' in data
            assert data['embeddings'].shape[0] == 2
            assert data['embeddings'].shape[1] == 32
            
            # Test JSON export
            json_path = Path(tmp_dir) / "embeddings.json"
            model.export_embeddings(json_path, format='json')
            assert json_path.exists()
    
    def test_unfitted_model_errors(self):
        model = LSdembed()
        
        with pytest.raises(ValueError, match="Model must be fitted"):
            model.embed_query("test")
        
        with pytest.raises(ValueError, match="Cannot save unfitted model"):
            model.save_model("test.pkl")
        
        with pytest.raises(ValueError, match="Cannot export unfitted model"):
            model.export_embeddings("test.npz")
    
    def test_compression_options(self):
        model = LSdembed({'d': 64})
        texts = ["Test text"] * 5
        model.fit(texts)
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Test uncompressed save
            uncompressed_path = Path(tmp_dir) / "model.pkl"
            model.save_model(uncompressed_path, compress=False)
            assert uncompressed_path.exists()
            
            # Test compressed save
            compressed_path = Path(tmp_dir) / "model_compressed.pkl"
            model.save_model(compressed_path, compress=True)
            assert (compressed_path.parent / (compressed_path.name + '.gz')).exists()
            
            # Both should load correctly
            model1 = LSdembed.from_pretrained(uncompressed_path)
            model2 = LSdembed.from_pretrained(compressed_path)
            
            assert model1.is_fitted
            assert model2.is_fitted