import os

from langchain_openai import AzureChatOpenAI, ChatOpenAI
from pydantic import BaseModel


class GooseChecker(BaseModel):
    with_respect_to: str  # The branch or commit to compare against

    @property
    def quota(self) -> int:
        return 4095

    def _get_model(self):
        raise NotImplementedError("Subclasses must implement this method")


class GooseCheckerResponse(BaseModel):
    file_name: str
    chain_of_thought: str
    issues: list

class ApprovalChainResponse(BaseModel):
    approved: bool
    instructions_to_engineer: str

class OpenAIGooseChecker(GooseChecker):
    model: str

    @property
    def quota(self) -> int:
        if self.model == "gpt-3.5-turbo":
            return 4095
        elif self.model == "gpt-4":
            return 8190

        return 4095

    @property
    def api_key(self) -> str:
        try:
            return os.environ["OPENAI_API_KEY"]
        except KeyError:
            raise ValueError("Environment variable OPENAI_API_KEY is not set")

    def _get_model(self):
        return ChatOpenAI(model=self.model, api_key=self.api_key, temperature=0.1)


class AzureGooseChecker(GooseChecker):
    deployment_name: str

    @property
    def quota(self) -> int:
        if "gpt-3.5-turbo" in self.deployment_name:
            return 4095
        elif "gpt-4" in self.deployment_name:
            return 8190

        return 4095

    @property
    def openai_api_version(self) -> str:
        try:
            return os.environ["AZURE_OPENAI_API_VERSION"]
        except KeyError:
            raise ValueError("Environment variable AZURE_OPENAI_API_VERSION is not set")

    @property
    def api_key(self) -> str:
        try:
            return os.environ["AZURE_OPENAI_API_KEY"]
        except KeyError:
            raise ValueError("Environment variable AZURE_OPENAI_API_KEY is not set")

    @property
    def base_url(self) -> str:
        try:
            return os.environ["AZURE_OPENAI_BASE_URL"]
        except KeyError:
            raise ValueError("Environment variable AZURE_OPENAI_BASE_URL is not set")

    def _get_model(self):
        return AzureChatOpenAI(
            deployment_name=self.deployment_name,  # Want to try another model? Check out the AI-Playground in the Analytics Lab Launcher for examples using other models.
            api_version=self.openai_api_version,
            azure_endpoint=self.base_url,
            temperature=0.1,  # a number from 0 to 2
        )
