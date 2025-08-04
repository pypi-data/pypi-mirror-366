"""
Tests for LLM Evaluator
"""

import pytest
import torch
from llm_eval_toolkit import LLMEvaluator

class TestLLMEvaluator:
    
    @pytest.fixture
    def evaluator(self):
        """Create an evaluator instance for testing."""
        return LLMEvaluator()
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for testing."""
        return {
            'question': "What is the capital of France?",
            'response': "The capital of France is Paris.",
            'reference': "Paris is the capital of France.",
            'candidates': ["The capital of France is Paris.", "Paris is the capital."],
            'references': ["Paris is the capital of France.", "The capital is Paris."]
        }
    
    def test_initialization(self, evaluator):
        """Test evaluator initialization."""
        assert evaluator is not None
        assert evaluator.device in ['cpu', 'cuda']
    
    def test_bleu_rouge_evaluation(self, evaluator, sample_data):
        """Test BLEU and ROUGE evaluation."""
        bleu, rouge1 = evaluator.evaluate_bleu_rouge(
            sample_data['candidates'], 
            sample_data['references']
        )
        assert isinstance(bleu, float)
        assert isinstance(rouge1, float)
        assert 0 <= bleu <= 100
        assert 0 <= rouge1 <= 1
    
    def test_bert_score_evaluation(self, evaluator, sample_data):
        """Test BERT Score evaluation."""
        bert_p, bert_r, bert_f1 = evaluator.evaluate_bert_score(
            sample_data['candidates'], 
            sample_data['references']
        )
        assert isinstance(bert_p, float)
        assert isinstance(bert_r, float)
        assert isinstance(bert_f1, float)
        assert 0 <= bert_p <= 1
        assert 0 <= bert_r <= 1
        assert 0 <= bert_f1 <= 1
    
    def test_perplexity_evaluation(self, evaluator, sample_data):
        """Test perplexity evaluation."""
        perplexity = evaluator.evaluate_perplexity(sample_data['response'])
        assert isinstance(perplexity, float)
        assert perplexity > 0
    
    def test_diversity_evaluation(self, evaluator):
        """Test diversity evaluation."""
        texts = ["Hello world", "Hello there", "Hi world", "Hey there"]
        diversity = evaluator.evaluate_diversity(texts)
        assert isinstance(diversity, float)
        assert 0 <= diversity <= 1
    
    def test_meteor_evaluation(self, evaluator, sample_data):
        """Test METEOR evaluation."""
        meteor = evaluator.evaluate_meteor(
            sample_data['candidates'], 
            sample_data['references']
        )
        assert isinstance(meteor, float)
        assert 0 <= meteor <= 1
    
    def test_chrf_evaluation(self, evaluator, sample_data):
        """Test CHRF evaluation."""
        chrf = evaluator.evaluate_chrf(
            sample_data['candidates'], 
            sample_data['references']
        )
        assert isinstance(chrf, float)
        assert 0 <= chrf <= 1
    
    def test_readability_evaluation(self, evaluator, sample_data):
        """Test readability evaluation."""
        flesch_ease, flesch_grade = evaluator.evaluate_readability(sample_data['response'])
        assert isinstance(flesch_ease, float)
        assert isinstance(flesch_grade, float)
    
    def test_evaluate_all(self, evaluator, sample_data):
        """Test comprehensive evaluation."""
        results = evaluator.evaluate_all(
            sample_data['question'],
            sample_data['response'],
            sample_data['reference']
        )
        
        expected_metrics = [
            "BLEU", "ROUGE-1", "BERT_Precision", "BERT_Recall", "BERT_F1",
            "Perplexity", "Diversity", "Bias_Score", "MAUVE", "METEOR",
            "CHRF", "Flesch_Reading_Ease", "Flesch_Kincaid_Grade"
        ]
        
        for metric in expected_metrics:
            assert metric in results
            assert isinstance(results[metric], (int, float))
    
    def test_batch_evaluation(self, evaluator):
        """Test batch evaluation."""
        questions = ["What is AI?", "Explain ML"]
        responses = ["AI is artificial intelligence", "ML is machine learning"]
        references = ["Artificial intelligence", "Machine learning"]
        
        results = evaluator.evaluate_batch(questions, responses, references)
        assert len(results) == 2
        assert all(isinstance(result, dict) for result in results)
    
    def test_summary_stats(self, evaluator):
        """Test summary statistics calculation."""
        # Create mock results
        results = [
            {"BLEU": 0.5, "ROUGE-1": 0.6},
            {"BLEU": 0.7, "ROUGE-1": 0.8}
        ]
        
        summary = evaluator.get_summary_stats(results)
        assert "BLEU" in summary
        assert "ROUGE-1" in summary
        assert "mean" in summary["BLEU"]
        assert "std" in summary["BLEU"]
        assert "min" in summary["BLEU"]
        assert "max" in summary["BLEU"]
    
    def test_empty_input_handling(self, evaluator):
        """Test handling of empty inputs."""
        # Test empty lists
        bleu, rouge1 = evaluator.evaluate_bleu_rouge([], [])
        assert bleu == 0.0
        assert rouge1 == 0.0
        
        # Test empty text
        diversity = evaluator.evaluate_diversity([])
        assert diversity == 0.0
    
    def test_batch_length_mismatch(self, evaluator):
        """Test error handling for mismatched batch lengths."""
        questions = ["Q1", "Q2"]
        responses = ["R1"]  # Different length
        references = ["Ref1", "Ref2"]
        
        with pytest.raises(ValueError):
            evaluator.evaluate_batch(questions, responses, references)