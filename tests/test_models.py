import os

import pytest

from goose_checker.models import AzureGooseChecker


def test_get_api_key():
    os.environ["AZURE_OPENAI_API_KEY"] = "test_key"
    assert (
        AzureGooseChecker(with_respect_to="main", deployment_name="gpt-4").api_key
        == "test_key"
    )


def test_api_key_not_set():
    del os.environ["AZURE_OPENAI_API_KEY"]
    with pytest.raises(ValueError):
        AzureGooseChecker().api_key
