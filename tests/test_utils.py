import threading
import time
from pathlib import Path
from unittest import mock

import pytest
from llm_devtale.node import NodeType
from llm_devtale.templates import SYSTEM_PROMPT
from llm_devtale.utils import (TokenCounter, generate_summary, get_prompt,
                               parallel_process)


class TestParallelProcess:
    def test_parallel_process_simple(self):
        """Test parallel processing of a simple function."""

        def square(x):
            return x * x

        items = [1, 2, 3, 4, 5]
        results = parallel_process(items, square)

        assert sorted(results) == [1, 4, 9, 16, 25]

    def test_parallel_process_with_error(self):
        """Test parallel processing handling errors."""

        def failing_function(x):
            if x == 3:
                raise ValueError("Test error")
            return x * x

        items = [1, 2, 3, 4]
        with mock.patch("logging.Logger.error") as mock_error:
            results = parallel_process(items, failing_function)

        # Should get results for non-failing items
        assert 1 in results
        assert 4 in results
        assert 16 in results

        # Should log error
        mock_error.assert_called_once()


class TestPrompt:
    def test_get_prompt_does_not_exist(self):
        with pytest.raises(Exception):
            prompt = get_prompt("")  # type: ignore

    def test_get_prompt(self):
        prompt = get_prompt(NodeType.FILE)
        assert isinstance(prompt, str)

    def test_token_counter(self):
        assert TokenCounter.count_tokens("This is my prompt") == 4


class TestSummary:
    def test_generate_summary(self):
        mock_llm_model = mock.MagicMock()

        expected_llm_response = "This is a mocked summary."
        mock_llm_model.prompt.return_value.text.return_value = expected_llm_response

        # Define test data
        test_data = {"name": "test_file.txt", "content": "print('hello world')"}
        test_summary_type = NodeType.FILE

        with mock.patch(
            "llm_devtale.utils.get_prompt", return_value="File content: {data[content]}"
        ) as mock_get_prompt:
            result_summary = generate_summary(
                mock_llm_model, test_data, test_summary_type
            )

            mock_get_prompt.assert_called_once_with(test_summary_type)

            expected_prompt_for_llm = "File content: print('hello world')"
            mock_llm_model.prompt.assert_called_once_with(
                expected_prompt_for_llm, system=SYSTEM_PROMPT
            )

            assert result_summary == expected_llm_response
