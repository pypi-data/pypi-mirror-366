"""
Unit tests for CLI functionality.

Tests the CLI argument parsing, command handling,
and output formatting.
"""

import unittest
from unittest.mock import Mock, patch
from io import StringIO

from tokker.cli.tokenize import (
    create_parser,
    handle_models,
    handle_model_default,
    handle_tokenize,
    main
)


class TestCLIParser(unittest.TestCase):
    """Test cases for CLI argument parsing."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = create_parser()

    def test_basic_tokenize_args(self):
        """Test basic tokenization arguments."""
        # Test with text argument
        args = self.parser.parse_args(['Hello world'])
        self.assertEqual(args.text, 'Hello world')
        self.assertIsNone(args.model)
        self.assertEqual(args.output, 'json')

        # Test with model
        args = self.parser.parse_args(['Hello world', '--model', 'gpt2'])
        self.assertEqual(args.text, 'Hello world')
        self.assertEqual(args.model, 'gpt2')

        # Test with output format
        args = self.parser.parse_args(['Hello world', '--output', 'plain'])
        self.assertEqual(args.text, 'Hello world')
        self.assertEqual(args.output, 'plain')

    def test_models_args(self):
        """Test models list arguments."""
        args = self.parser.parse_args(['--models'])
        self.assertTrue(args.models)

    def test_model_default_args(self):
        """Test model default arguments."""
        args = self.parser.parse_args(['--model-default', 'cl100k_base'])
        self.assertEqual(args.model_default, 'cl100k_base')

    def test_no_args(self):
        """Test parsing with no arguments (stdin mode)."""
        args = self.parser.parse_args([])
        self.assertIsNone(args.text)
        self.assertFalse(args.models)
        self.assertIsNone(args.model_default)





class TestHandleModels(unittest.TestCase):
    """Test cases for models command handling."""

    @patch('tokker.cli.tokenize.get_registry')
    @patch('builtins.print')
    def test_models_output(self, mock_print, mock_get_registry):
        """Test models output."""
        # Mock registry and models
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.list_models.return_value = [
            {'name': 'cl100k_base', 'provider': 'OpenAI', 'description': 'GPT-4 model'},
            {'name': 'gpt2', 'provider': 'HuggingFace', 'description': 'GPT-2 model'},
        ]

        # Call function
        handle_models()

        # Verify print calls
        self.assertTrue(mock_print.called)


class TestHandleModelDefault(unittest.TestCase):
    """Test cases for model default command handling."""

    @patch('tokker.cli.tokenize.config')
    @patch('tokker.cli.tokenize.get_registry')
    @patch('builtins.print')
    def test_valid_model_default(self, mock_print, mock_get_registry, mock_config):
        """Test setting valid default model."""
        # Mock registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.validate_model.return_value = True
        mock_registry.list_models.return_value = [
            {'name': 'cl100k_base', 'provider': 'OpenAI', 'description': 'GPT-4 model'}
        ]

        # Mock config
        mock_config.config_file = "/path/to/config.json"

        # Call function
        handle_model_default("cl100k_base")

        # Verify model was set
        mock_config.set_default_model.assert_called_once_with("cl100k_base")

        # Verify success message
        calls = mock_print.call_args_list
        success_message = calls[0][0][0]
        self.assertIn("✓ Default model set to: cl100k_base (OpenAI) - GPT-4 model", success_message)

    @patch('tokker.cli.tokenize.get_registry')
    @patch('sys.exit')
    def test_invalid_model_default(self, mock_exit, mock_get_registry):
        """Test setting invalid default model."""
        # Mock registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.validate_model.return_value = False
        mock_registry.list_models.return_value = [
            {'name': 'cl100k_base', 'provider': 'OpenAI', 'description': 'GPT-4 model'}
        ]

        # Call function
        handle_model_default("invalid_model")

        # Verify exit was called
        mock_exit.assert_called_once_with(1)


class TestHandleTokenize(unittest.TestCase):
    """Test cases for tokenize command handling."""

    @patch('tokker.cli.tokenize.count_words')
    @patch('tokker.cli.tokenize.config')
    @patch('tokker.cli.tokenize.get_registry')
    @patch('builtins.print')
    def test_tokenize_with_specific_model(self, mock_print, mock_get_registry, mock_config, mock_count_words):
        """Test tokenization with specific model."""
        # Mock config
        mock_config.get_delimiter.return_value = "⎮"

        # Mock word counting
        mock_count_words.return_value = 2

        # Mock registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.validate_model.return_value = True
        mock_result = {
            "token_strings": ["Hello", " world"],
            "token_ids": [123, 456],
            "token_count": 2,
            "model": "gpt2",
            "provider": "HuggingFace"
        }
        mock_registry.tokenize.return_value = mock_result

        # Call function
        handle_tokenize("Hello world", "gpt2", "json")

        # Verify tokenization was called
        mock_registry.tokenize.assert_called_once_with("Hello world", "gpt2")

        # Verify output was printed
        mock_print.assert_called_once()

    @patch('tokker.cli.tokenize.count_words')
    @patch('tokker.cli.tokenize.config')
    @patch('tokker.cli.tokenize.get_registry')
    @patch('builtins.print')
    def test_tokenize_with_default_model(self, mock_print, mock_get_registry, mock_config, mock_count_words):
        """Test tokenization with default model."""
        # Mock config
        mock_config.get_default_model.return_value = "cl100k_base"
        mock_config.get_delimiter.return_value = "⎮"

        # Mock word counting
        mock_count_words.return_value = 2

        # Mock registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.validate_model.return_value = True
        mock_result = {
            "token_strings": ["Hello", " world"],
            "token_ids": [123, 456],
            "token_count": 2,
            "model": "cl100k_base",
            "provider": "OpenAI"
        }
        mock_registry.tokenize.return_value = mock_result

        # Call function
        handle_tokenize("Hello world", None, "json")

        # Verify default model was used
        mock_registry.tokenize.assert_called_once_with("Hello world", "cl100k_base")

        # Verify output was printed
        mock_print.assert_called_once()

    @patch('tokker.cli.tokenize.config')
    @patch('tokker.cli.tokenize.get_registry')
    @patch('sys.exit')
    def test_tokenize_invalid_model(self, mock_exit, mock_get_registry, mock_config):
        """Test tokenization with invalid model."""
        # Mock registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry
        mock_registry.validate_model.return_value = False
        mock_registry.list_models.return_value = [
            {'name': 'cl100k_base', 'provider': 'OpenAI', 'description': 'GPT-4 model'}
        ]

        # Call function and expect sys.exit
        handle_tokenize("Hello world", "invalid_model", "json")
        mock_exit.assert_called_once_with(1)


class TestMainFunction(unittest.TestCase):
    """Test cases for main CLI entry point."""

    @patch('tokker.cli.tokenize.handle_models')
    @patch('sys.argv', ['tok', '--models'])
    def test_main_models(self, mock_handle_models):
        """Test main function with models command."""
        result = main()
        self.assertEqual(result, 0)
        mock_handle_models.assert_called_once()

    @patch('tokker.cli.tokenize.handle_model_default')
    @patch('sys.argv', ['tok', '--model-default', 'gpt2'])
    def test_main_model_default(self, mock_handle_default):
        """Test main function with model default command."""
        result = main()
        self.assertEqual(result, 0)
        mock_handle_default.assert_called_once_with("gpt2")

    @patch('tokker.cli.tokenize.handle_tokenize')
    @patch('sys.argv', ['tok', 'Hello world'])
    def test_main_tokenize(self, mock_handle_tokenize):
        """Test main function with tokenize command."""
        result = main()
        self.assertEqual(result, 0)
        mock_handle_tokenize.assert_called_once_with("Hello world", None, "json")

    @patch('tokker.cli.tokenize.handle_tokenize')
    @patch('sys.stdin', StringIO('Hello from stdin'))
    @patch('sys.argv', ['tok'])
    def test_main_stdin(self, mock_handle_tokenize):
        """Test main function with stdin input."""
        result = main()
        self.assertEqual(result, 0)
        mock_handle_tokenize.assert_called_once_with("Hello from stdin", None, "json")


if __name__ == '__main__':
    unittest.main()
