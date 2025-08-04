# LLM Evaluator

A comprehensive evaluation toolkit for Large Language Models (LLMs) that provides various metrics to assess the quality, coherence, and safety of generated text.

## Features

- **Text Quality Metrics**: BLEU, ROUGE, BERT Score, METEOR, CHRF
- **Language Model Metrics**: Perplexity using GPT-2
- **Diversity Metrics**: N-gram diversity analysis
- **Safety Metrics**: Bias and hate speech detection
- **Semantic Similarity**: MAUVE score for distribution comparison
- **Readability Metrics**: Flesch Reading Ease and Flesch-Kincaid Grade
- **Hallucination Detection**: NLI-based contradiction detection, entity hallucination, numerical hallucination, and semantic similarity

## Installation

Install the package using pip:

```bash
pip install llm-evaluator-toolkit
```

Or install from source:

```bash
git clone git@github.com:AnSwati/LLM_evaluator_1.0.git
cd LLM_evaluator_1.0.0
pip install -e .
```

## Quick Start

```python
from llm_evaluator import LLMEvaluator

# Initialize the evaluator
evaluator = LLMEvaluator()

# Evaluate a single response
question = "What is the capital of France?"
response = "The capital of France is Paris."
reference = "Paris is the capital of France."

results = evaluator.evaluate_all(question, response, reference)
print(results)

# Check hallucination metrics
print(f"Hallucination score: {results['Hallucination_Score']}")
print(f"NLI contradiction: {results['NLI_Contradiction']}")
print(f"Entity hallucination: {results['Entity_Hallucination']}")

# Evaluate multiple responses
questions = ["What is AI?", "Explain machine learning"]
responses = ["AI is artificial intelligence", "ML is a subset of AI"]
references = ["Artificial intelligence", "Machine learning uses algorithms"]

batch_results = evaluator.evaluate_batch(questions, responses, references)
summary = evaluator.get_summary_stats(batch_results)
print(summary)
```

For more detailed examples of hallucination detection, see the [examples/hallucination_test.py](examples/hallucination_test.py) script and [examples/HALLUCINATION_DETECTION.md](examples/HALLUCINATION_DETECTION.md) documentation.

## Available Metrics

### Text Quality Metrics
- **BLEU**: Measures n-gram overlap between generated and reference text
- **ROUGE-1**: Measures unigram overlap (recall-oriented)
- **BERT Score**: Semantic similarity using BERT embeddings
- **METEOR**: Considers synonyms and paraphrases
- **CHRF**: Character-level F-score

### Language Model Metrics
- **Perplexity**: Measures how well a language model predicts the text

### Diversity Metrics
- **Diversity**: Ratio of unique bigrams to total tokens

### Safety Metrics
- **Bias Score**: Detects potential hate speech or bias

### Semantic Metrics
- **MAUVE**: Measures similarity between text distributions

### Readability Metrics
- **Flesch Reading Ease**: Text readability score
- **Flesch-Kincaid Grade**: Grade level required to understand the text

### Hallucination Detection Metrics
- **NLI Hallucination**: Uses Natural Language Inference to detect contradictions
- **Entity Hallucination**: Detects non-existent entities in generated text
- **Numerical Hallucination**: Identifies incorrect numbers and statistics
- **Semantic Similarity**: Measures overall semantic alignment
- **Combined Hallucination Score**: Weighted combination of hallucination metrics

## API Reference

### LLMEvaluator

The main class for evaluating LLM outputs.

#### Methods

- `evaluate_all(question, response, reference)`: Evaluate all metrics for a single triplet
- `evaluate_batch(questions, responses, references)`: Evaluate multiple triplets
- `get_summary_stats(results)`: Calculate summary statistics for batch results
- `evaluate_bleu_rouge(candidates, references)`: Calculate BLEU and ROUGE scores
- `evaluate_bert_score(candidates, references)`: Calculate BERT Score
- `evaluate_perplexity(text)`: Calculate perplexity
- `evaluate_diversity(texts)`: Calculate diversity score
- `evaluate_bias(text)`: Evaluate bias/hate speech
- `evaluate_meteor(candidates, references)`: Calculate METEOR score
- `evaluate_chrf(candidates, references)`: Calculate CHRF score
- `evaluate_readability(text)`: Calculate readability metrics
- `evaluate_mauve(reference_texts, generated_texts)`: Calculate MAUVE score
- `evaluate_hallucination_nli(generated_text, reference_text)`: Detect hallucinations using NLI
- `evaluate_entity_hallucination(generated_text, reference_text)`: Detect entity hallucinations
- `evaluate_numerical_hallucination(generated_text, reference_text)`: Detect numerical hallucinations
- `evaluate_semantic_similarity(generated_text, reference_text)`: Calculate semantic similarity

## Requirements

- Python 3.8+
- PyTorch
- Transformers
- Various NLP libraries (see requirements.txt)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this library in your research, please cite:

```bibtex
@software{llm_evaluator,
  title={LLM Evaluator: A Comprehensive Evaluation Toolkit for Large Language Models},
  author={Swati Tyagi},
  year={2024},
  url={https://github.com/AnSwati/llm_eval_toolkit}
}
```