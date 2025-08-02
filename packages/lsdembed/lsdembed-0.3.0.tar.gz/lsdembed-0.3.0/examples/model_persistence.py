from lsdembed import LSdembed
import numpy as np
import os

# Train and save multiple models with different parameters
def train_and_save_models():
    # Generate more realistic sample data
    texts = [
        f"Document {i}: This is a sample text about machine learning and artificial intelligence. "
        f"It discusses various topics including natural language processing, computer vision, "
        f"and deep learning algorithms. The content varies to provide diverse training data."
        for i in range(100)
    ]
    
    try:
        # Create models directory
        os.makedirs('models', exist_ok=True)
        
        print("Training high precision model...")
        # Model 1: High precision
        model_hp = LSdembed({
            'd': 512,
            'alpha': 2.0,
            'beta': 0.8,
            'r_cutoff': 4.0,
            'seed': 42  # For reproducibility
        })
        model_hp.fit(texts)
        model_hp.save_model('models/high_precision_model.pkl')
        print("High precision model saved!")
        
        print("Training fast inference model...")
        # Model 2: Fast inference
        model_fast = LSdembed({
            'd': 128,
            'alpha': 1.0,
            'beta': 0.3,
            'r_cutoff': 2.0,
            'seed': 42  # For reproducibility
        })
        model_fast.fit(texts)
        model_fast.save_model('models/fast_model.pkl')
        print("Fast inference model saved!")
        
        print("Both models trained and saved successfully!")
        
    except Exception as e:
        print(f"Error during model training/saving: {e}")
        raise

# Load and compare models
def compare_models():
    try:
        # Check if model files exist
        hp_model_path = 'models/high_precision_model.pkl.gz'
        fast_model_path = 'models/fast_model.pkl.gz'
        
        if not os.path.exists(hp_model_path):
            print(f"High precision model not found at {hp_model_path}")
            return
        
        if not os.path.exists(fast_model_path):
            print(f"Fast model not found at {fast_model_path}")
            return
        
        print("Loading models...")
        hp_model = LSdembed.from_pretrained(hp_model_path)
        fast_model = LSdembed.from_pretrained(fast_model_path)
        print("Models loaded successfully!")
        
        # Test queries
        queries = [
            "machine learning algorithms",
            "artificial intelligence",
            "natural language processing"
        ]
        
        for query in queries:
            print(f"\n{'='*50}")
            print(f"Query: '{query}'")
            print('='*50)
            
            try:
                hp_results = hp_model.search(query, top_k=3)
                fast_results = fast_model.search(query, top_k=3)
                
                print("\nHigh Precision Model Results:")
                for i, (chunk, score) in enumerate(hp_results, 1):
                    print(f"  {i}. Score: {score:.4f}")
                    print(f"     Text: {chunk[:100]}...")
                
                print("\nFast Model Results:")
                for i, (chunk, score) in enumerate(fast_results, 1):
                    print(f"  {i}. Score: {score:.4f}")
                    print(f"     Text: {chunk[:100]}...")
                    
            except Exception as e:
                print(f"Error during search for query '{query}': {e}")
        
        # Model info comparison
        try:
            hp_info = hp_model.get_model_info()
            fast_info = fast_model.get_model_info()
            
            print(f"\n{'='*50}")
            print("Model Comparison")
            print('='*50)
            
            print(f"High Precision Model:")
            print(f"  Dimension: {hp_info['embedding_dimension']}D")
            print(f"  Memory: {hp_info['memory_usage_mb']['total_approximate']:.1f}MB")
            print(f"  Chunks: {hp_info['num_chunks']}")
            print(f"  Vocabulary: {hp_info['vocabulary_size']}")
            
            print(f"\nFast Model:")
            print(f"  Dimension: {fast_info['embedding_dimension']}D")
            print(f"  Memory: {fast_info['memory_usage_mb']['total_approximate']:.1f}MB")
            print(f"  Chunks: {fast_info['num_chunks']}")
            print(f"  Vocabulary: {fast_info['vocabulary_size']}")
            
            # Performance comparison
            memory_ratio = hp_info['memory_usage_mb']['total_approximate'] / fast_info['memory_usage_mb']['total_approximate']
            print(f"\nMemory Usage Ratio (HP/Fast): {memory_ratio:.1f}x")
            
        except Exception as e:
            print(f"Error getting model information: {e}")
            
    except Exception as e:
        print(f"Error loading or comparing models: {e}")


def demonstrate_export_functionality():
    """Demonstrate different export formats"""
    try:
        if os.path.exists('models/fast_model.pkl.gz'):
            print("\nDemonstrating export functionality...")
            model = LSdembed.from_pretrained('models/fast_model.pkl.gz')
            
            # Create exports directory
            os.makedirs('exports', exist_ok=True)
            
            # Export in different formats
            model.export_embeddings('exports/embeddings.npz', format='npz')
            print("Exported embeddings as NPZ format")
            
            model.export_embeddings('exports/embeddings.csv', format='csv')
            print("Exported embeddings as CSV format")
            
            model.export_embeddings('exports/embeddings.json', format='json')
            print("Exported embeddings as JSON format")
            
            print("All exports completed successfully!")
            
        else:
            print("Fast model not available for export demonstration")
            
    except Exception as e:
        print(f"Error during export demonstration: {e}")


if __name__ == "__main__":
    try:
        print("LSdembed Model Persistence Example")
        print("=" * 40)
        
        # Train and save models
        train_and_save_models()
        
        # Compare models
        compare_models()
        
        # Demonstrate export functionality
        demonstrate_export_functionality()
        
        print("\nExample completed successfully!")
        
    except Exception as e:
        print(f"Example failed with error: {e}")
        exit(1)