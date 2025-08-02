from lsdembed import LSdembed
import os

# Initialize with custom parameters
params = {
    'd': 256,           # Lower dimension for speed
    'alpha': 1.5,       # Stronger repulsion
    'beta': 0.3,        # Weaker attraction
    'r_cutoff': 2.5     # Smaller cutoff radius
}

model = LSdembed(params)

# Fit on your corpus with error handling
try:
    if os.path.exists('your_documents.txt'):
        with open('your_documents.txt', 'r', encoding='utf-8') as f:
            text = f.read()
        print("Loaded text from your_documents.txt")
    else:
        # Use sample data for demonstration
        text = """
        This is sample text for demonstration purposes.
        You can replace this with your actual document content.
        The LSdembed library will process this text and create embeddings.
        
        Machine learning is a powerful tool for understanding text.
        Natural language processing helps computers comprehend human language.
        Text embeddings capture semantic meaning in numerical form.
        
        Physics-inspired algorithms can model complex relationships.
        Particle dynamics simulate semantic interactions between words.
        This approach creates rich, contextual representations.
        """
        print("Using sample data since 'your_documents.txt' not found")
    
    model.fit([text], chunk_size=800)
    print("Model training completed successfully!")
    
except Exception as e:
    print(f"Error during model training: {e}")
    exit(1)

# Save the trained model with error handling
try:
    model.save_model('my_lsd_model.pkl', compress=True)
    print("Model saved successfully!")
except Exception as e:
    print(f"Error saving model: {e}")

# Search for relevant content
try:
    results = model.search("machine learning artificial intelligence", top_k=5)
    
    print(f"\nFound {len(results)} relevant chunks:")
    for i, (chunk, score) in enumerate(results, 1):
        print(f"\n{i}. Score: {score:.4f}")
        print(f"Text: {chunk[:200]}...")
        print("---")
except Exception as e:
    print(f"Error during search: {e}")

# Later, load the saved model with error handling
try:
    if os.path.exists('my_lsd_model.pkl.gz'):
        loaded_model = LSdembed.from_pretrained('my_lsd_model.pkl.gz')
        print("Model loaded successfully!")
        
        # Use loaded model for search
        new_results = loaded_model.search("physics simulation", top_k=3)
        print(f"Found {len(new_results)} results from loaded model")
        
        for i, (chunk, score) in enumerate(new_results, 1):
            print(f"{i}. Score: {score:.4f} - {chunk[:100]}...")
    else:
        print("Saved model file not found, using current model")
        loaded_model = model
        
except Exception as e:
    print(f"Error loading model: {e}")
    loaded_model = model  # Fallback to current model

# Export embeddings for external use with error handling
try:
    os.makedirs('exports', exist_ok=True)
    
    loaded_model.export_embeddings('exports/embeddings.npz', format='npz')
    print("Exported embeddings as NPZ format")
    
    loaded_model.export_embeddings('exports/embeddings.csv', format='csv')
    print("Exported embeddings as CSV format")
    
    loaded_model.export_embeddings('exports/embeddings.json', format='json')
    print("Exported embeddings as JSON format")
    
except Exception as e:
    print(f"Error exporting embeddings: {e}")

# Get model information
try:
    info = loaded_model.get_model_info()
    print(f"\nModel Information:")
    print(f"Status: {info['status']}")
    print(f"Number of chunks: {info['num_chunks']}")
    print(f"Embedding dimension: {info['embedding_dimension']}")
    print(f"Vocabulary size: {info['vocabulary_size']}")
    print(f"Memory usage: {info['memory_usage_mb']['total_approximate']:.2f} MB")
    
    print(f"\nModel Parameters:")
    for param, value in info['parameters'].items():
        print(f"  {param}: {value}")
        
except Exception as e:
    print(f"Error getting model info: {e}")

print("\nExample completed successfully!")