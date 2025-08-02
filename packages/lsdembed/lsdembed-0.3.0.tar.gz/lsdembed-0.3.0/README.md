# lsdembed - Physics-Inspired Text Embedding Library

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Lagrangian Semantic Dynamics Embeddings[LSDEmbed] is a novel text embedding library that uses physics-inspired algorithms to create high-quality semantic embeddings. By modeling text tokens as particles in a physical system with forces of attraction and repulsion, lsdembed captures nuanced semantic relationships that traditional methods might miss.

<h3 align="center">
  <code>pip install lsdembed</code>
</h3>

## Features

- **Physics-Inspired Embeddings**: Uses particle physics simulation to model semantic relationships
- **High Performance**: Optimized C++ backend with OpenMP parallelization
- **Flexible Parameters**: Customizable physics parameters for different use cases
- **Memory Efficient**: Spatial hashing and memory-aware processing
- **Easy Persistence**: Save and load trained models with compression support
- **Multiple Export Formats**: Export embeddings as NPZ, CSV, or JSON

## Installation

### Prerequisites

- Python 3.8 or higher
- C++ compiler with C++17 support
- OpenMP (optional, for parallel processing)

### Install from Source

```bash
git clone https://github.com/datasciritwik/lsdembed.git
cd lsdembed
pip install -e .
```

### Dependencies

The library requires:
- `numpy>=1.21.0`
- `scipy>=1.7.0`
- `pandas>=1.3.0`
- `pybind11>=2.6.0` (for building)

## Quick Start

```python
from lsdembed import LSdembed
from lsdembed.text_processor import TextProcessor

# Single text input (new preferred method)
model = LSdembed({'d': 128})
model.fit("Your entire document text here", chunk_size=300)

# Custom chunking parameters
processor = TextProcessor(chunk_size=200, chunk_overlap=50)
chunks = processor.chunk_text("Your text here")

# Backward compatible list input
model.fit(["Text 1", "Text 2", "Text 3"])
```

## Advanced Usage

### Custom Parameters

```python
# Configure physics parameters for your use case
params = {
    'd': 256,           # Embedding dimension
    'alpha': 1.5,       # Repulsion strength
    'beta': 0.3,        # Attraction strength
    'gamma': 0.2,       # Damping coefficient
    'r_cutoff': 2.5,    # Force cutoff radius
    'dt': 0.05,         # Integration time step
    'scale': 0.1,       # Initial position scale
    'seed': 42          # Random seed for reproducibility
}

model = lsdembed(params)
```

### Model Persistence

```python
# Save trained model
model.save_model('my_model.pkl', compress=True)

# Load model later
loaded_model = lsdembed.from_pretrained('my_model.pkl.gz')

# Or load into existing instance
model = lsdembed()
model.load_model('my_model.pkl.gz')
```

### Export Embeddings

```python
# Export in different formats
model.export_embeddings('embeddings.npz', format='npz')
model.export_embeddings('embeddings.csv', format='csv')
model.export_embeddings('embeddings.json', format='json')
```

### Model Information

```python
# Get detailed model information
info = model.get_model_info()
print(f"Status: {info['status']}")
print(f"Chunks: {info['num_chunks']}")
print(f"Dimension: {info['embedding_dimension']}")
print(f"Memory usage: {info['memory_usage_mb']['total_approximate']:.2f} MB")
```

## Physics Parameters Guide

Understanding the physics parameters helps you tune the model for your specific use case:

- **`d` (dimension)**: Higher dimensions capture more nuanced relationships but require more memory
- **`alpha` (repulsion)**: Controls how strongly dissimilar tokens repel each other
- **`beta` (attraction)**: Controls sequential attraction between adjacent tokens
- **`gamma` (damping)**: Higher values lead to faster convergence but may reduce quality
- **`r_cutoff`**: Limits interaction range, affecting both performance and quality
- **`dt`**: Smaller values improve stability but increase computation time
- **`scale`**: Initial randomization scale, affects convergence behavior

### Recommended Configurations

**High Precision (slower, better quality):**
```python
params = {'d': 512, 'alpha': 2.0, 'beta': 0.8, 'r_cutoff': 4.0, 'dt': 0.02}
```

**Fast Inference (faster, good quality):**
```python
params = {'d': 128, 'alpha': 1.0, 'beta': 0.3, 'r_cutoff': 2.0, 'dt': 0.1}
```

**Balanced (recommended starting point):**
```python
params = {'d': 256, 'alpha': 1.5, 'beta': 0.5, 'r_cutoff': 3.0, 'dt': 0.05}
```

## API Reference

### lsdembed Class

#### `__init__(params=None)`
Initialize the lsdembed model with optional parameters.

#### `fit(texts, chunk_size=1000)`
Fit the model on a corpus of texts.
- `texts`: List of strings to train on
- `chunk_size`: Maximum characters per chunk

#### `embed_query(query)`
Embed a single query string.
- Returns: numpy array of embedding

#### `search(query, top_k=5)`
Search for similar chunks.
- Returns: List of (text, score) tuples

#### `save_model(filepath, compress=True)`
Save the fitted model to disk.

#### `load_model(filepath)`
Load a saved model from disk.

#### `export_embeddings(filepath, format='npz')`
Export embeddings in specified format ('npz', 'csv', 'json').

#### `get_model_info()`
Get comprehensive model information.

#### `update_params(**kwargs)`
Update model parameters after initialization.

### TextProcessor Class

#### `tokenize(text)`
Tokenize text using the configured pattern.

#### `chunk_texts(texts, max_chars=300)`
Split texts into chunks.

#### `calculate_idf(chunks)`
Calculate IDF scores for tokens.

## Performance Tips

1. **Memory Management**: For large corpora, use smaller embedding dimensions or process in batches
2. **Parallel Processing**: Ensure OpenMP is available for best performance
3. **Parameter Tuning**: Start with balanced parameters and adjust based on your data
4. **Chunk Size**: Optimal chunk size depends on your text length and domain

## Examples

See the `examples/` directory for complete examples:
- `basic_usage.py`: Simple usage example
- `model_persistence.py`: Saving and loading models

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use lsdembed in your research, please cite:

```bibtex
@software{lsdembed,
  title={lsdembed: Physics-Inspired Text Embedding Library},
  author={Ritwik singh},
  year={2025},
  url={https://github.com/datasciritwik/lsdembed}
}
```

## Changelog

### Version 0.1.0
- Initial release
- Physics-inspired embedding algorithm
- C++ backend with Python bindings
- Model persistence and export functionality
