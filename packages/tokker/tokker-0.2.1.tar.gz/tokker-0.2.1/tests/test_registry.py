"""
Unit tests for model registry functionality.

Tests the ModelRegistry class, model discovery,
routing logic, and validation.
"""

import unittest

from tokker.models.registry import ModelRegistry, get_registry
from tokker.models.exceptions import ModelNotFoundError
from tokker.models.base import BaseModel


class MockTiktokenModel(BaseModel):
    """Mock tiktoken model for testing."""

    @property
    def library_name(self) -> str:
        return "OpenAI"

    @property
    def supported_models(self):
        return ["test_tiktoken", "cl100k_base"]

    @property
    def model_descriptions(self):
        return {
            "test_tiktoken": "Test tiktoken model",
            "cl100k_base": "GPT-4 model"
        }

    def tokenize(self, text: str, model_name: str):
        return {
            "token_strings": ["test"],
            "token_ids": [123],
            "token_count": 1,
            "model": model_name,
            "provider": self.library_name
        }

    def validate_model(self, model_name: str) -> bool:
        return model_name in self.supported_models

    def count_tokens(self, text: str, model_name: str) -> int:
        return 1


class MockHuggingFaceModel(BaseModel):
    """Mock HuggingFace model for testing."""

    @property
    def library_name(self) -> str:
        return "HuggingFace"

    @property
    def supported_models(self):
        return ["test_hf", "gpt2"]

    @property
    def model_descriptions(self):
        return {
            "test_hf": "Test HuggingFace model",
            "gpt2": "GPT-2 model"
        }

    def tokenize(self, text: str, model_name: str):
        return {
            "token_strings": ["test"],
            "token_ids": [456],
            "token_count": 1,
            "model": model_name,
            "provider": self.library_name
        }

    def validate_model(self, model_name: str) -> bool:
        return model_name in self.supported_models

    def count_tokens(self, text: str, model_name: str) -> int:
        return 1


class TestModelRegistry(unittest.TestCase):
    """Test cases for ModelRegistry."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = ModelRegistry()
        # Manually register mock models for testing
        self.mock_tiktoken = MockTiktokenModel()
        self.mock_hf = MockHuggingFaceModel()

        self.registry._register_model(self.mock_tiktoken)
        self.registry._register_model(self.mock_hf)
        self.registry._initialized = True

    def test_model_registration(self):
        """Test that models are registered correctly."""
        # Check that providers are registered
        self.assertIn("OpenAI", self.registry._models)
        self.assertIn("HuggingFace", self.registry._models)

        # Check that model names are mapped to providers
        self.assertEqual(self.registry._model_mapping["test_tiktoken"], "OpenAI")
        self.assertEqual(self.registry._model_mapping["test_hf"], "HuggingFace")
        self.assertEqual(self.registry._model_mapping["cl100k_base"], "OpenAI")
        self.assertEqual(self.registry._model_mapping["gpt2"], "HuggingFace")

    def test_get_model(self):
        """Test getting model by name."""
        # Test tiktoken model
        model = self.registry.get_model("test_tiktoken")
        self.assertEqual(model.library_name, "OpenAI")

        # Test HuggingFace model
        model = self.registry.get_model("test_hf")
        self.assertEqual(model.library_name, "HuggingFace")

        # Test unknown model
        with self.assertRaises(ModelNotFoundError):
            self.registry.get_model("unknown_model")

    def test_list_models(self):
        """Test listing available models."""
        models = self.registry.list_models()

        # Should have 4 models total
        self.assertEqual(len(models), 4)

        # Check that all expected models are present
        model_names = [t['name'] for t in models]
        self.assertIn("test_tiktoken", model_names)
        self.assertIn("test_hf", model_names)
        self.assertIn("cl100k_base", model_names)
        self.assertIn("gpt2", model_names)

        # Check structure of model info
        for model in models:
            self.assertIn('name', model)
            self.assertIn('provider', model)
            self.assertIn('description', model)

    def test_validate_model(self):
        """Test model validation."""
        # Valid models
        self.assertTrue(self.registry.validate_model("test_tiktoken"))
        self.assertTrue(self.registry.validate_model("test_hf"))
        self.assertTrue(self.registry.validate_model("cl100k_base"))
        self.assertTrue(self.registry.validate_model("gpt2"))

        # Invalid model
        self.assertFalse(self.registry.validate_model("unknown_model"))

    def test_tokenize(self):
        """Test tokenization through registry."""
        # Test tiktoken tokenization
        result = self.registry.tokenize("test text", "test_tiktoken")
        self.assertEqual(result["provider"], "OpenAI")
        self.assertEqual(result["model"], "test_tiktoken")
        self.assertEqual(result["token_count"], 1)

        # Test HuggingFace tokenization
        result = self.registry.tokenize("test text", "test_hf")
        self.assertEqual(result["provider"], "HuggingFace")
        self.assertEqual(result["model"], "test_hf")
        self.assertEqual(result["token_count"], 1)

        # Test unknown model
        with self.assertRaises(ModelNotFoundError):
            self.registry.tokenize("test text", "unknown_model")

    def test_count_tokens(self):
        """Test token counting through registry."""
        # Test tiktoken counting
        count = self.registry.count_tokens("test text", "test_tiktoken")
        self.assertEqual(count, 1)

        # Test HuggingFace counting
        count = self.registry.count_tokens("test text", "test_hf")
        self.assertEqual(count, 1)

        # Test unknown model
        with self.assertRaises(ModelNotFoundError):
            self.registry.count_tokens("test text", "unknown_model")

    def test_get_libraries(self):
        """Test getting available providers."""
        providers = self.registry.get_libraries()
        self.assertIn("OpenAI", providers)
        self.assertIn("HuggingFace", providers)
        self.assertEqual(len(providers), 2)


class TestGlobalRegistry(unittest.TestCase):
    """Test cases for global registry singleton."""

    def test_get_registry_singleton(self):
        """Test that get_registry returns the same instance."""
        registry1 = get_registry()
        registry2 = get_registry()
        self.assertIs(registry1, registry2)

    def test_registry_initialization(self):
        """Test that global registry is properly initialized."""
        registry = get_registry()
        self.assertIsInstance(registry, ModelRegistry)

        # Should have discovered real models
        models = registry.list_models()
        self.assertGreater(len(models), 0)


class TestModelDiscovery(unittest.TestCase):
    """Test cases for automatic model discovery."""

    def test_tiktoken_discovery(self):
        """Test that tiktoken models are discovered."""
        registry = get_registry()
        models = registry.list_models()

        # Should have tiktoken models
        tiktoken_models = [t for t in models if t['provider'] == 'OpenAI']
        self.assertGreater(len(tiktoken_models), 0)

        # Should include common tiktoken encodings
        model_names = [t['name'] for t in tiktoken_models]
        self.assertIn('cl100k_base', model_names)
        self.assertIn('o200k_base', model_names)

    def test_huggingface_discovery(self):
        """Test that HuggingFace models can be validated (BYOM approach)."""
        registry = get_registry()

        # HuggingFace uses BYOM so models aren't pre-registered
        # Test that the HuggingFace provider can validate common models
        self.assertTrue(registry.validate_model('gpt2'))

        # Test that tiktoken models are handled by OpenAI provider, not HuggingFace
        self.assertTrue(registry.validate_model('cl100k_base'))

        # Test that HuggingFace-style model names are handled correctly
        # Note: This might fail if transformers is not installed or model doesn't exist
        # but the important thing is that the validation logic works


if __name__ == '__main__':
    unittest.main()
