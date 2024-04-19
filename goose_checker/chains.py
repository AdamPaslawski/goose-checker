import tiktoken
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import PromptTemplate

from goose_checker.context import TerraformContext, get_terraform_context
from goose_checker.diff import GitDiff
from goose_checker.models import GooseChecker, GooseCheckerResponse, ApprovalChainResponse
from goose_checker.prompts import aggregation_prompt, base_prompt, terraform_prompt
from goose_checker.response_schema import (
    approve_or_deny_schema,
    cot_issues,
    list_issues,
    improvements_aggregation,
)


def get_token_len(string, model_name: str = "gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model_name)  # Make this dynamic
    num_tokens = len(encoding.encode(string))
    return num_tokens


def _build_context_subprompt(context: TerraformContext, quota: int):
    subprompt = f"""
    file_name: {context.file_name}

    contents: {context.contents}
    """

    # TODO: Probably a more intelligent way to do this...
    if get_token_len(subprompt) > quota:
        proportion = quota / get_token_len(subprompt)
        subprompt = subprompt[: int(proportion * len(subprompt))]

    return subprompt


def _build_diff_subprompt(diff: GitDiff, quota: int) -> dict:
    subprompt = f"""
    file_name: {diff.file_name}
    diff: {diff.diff}
    """
    if get_token_len(subprompt) > quota:
        proportion = quota / get_token_len(subprompt)
        subprompt = subprompt[: int(proportion * len(subprompt))]

    tokens_used = get_token_len(subprompt)

    return {"subprompt": subprompt, "tokens_used": tokens_used}


def base_checker(diff: GitDiff, goose_checker: GooseChecker) -> GooseCheckerResponse:

    # Core chain to analyze terraform diff
    response_schemas = [cot_issues,
                        list_issues]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    model = goose_checker._get_model()

    diff_and_tokens_used: dict = _build_diff_subprompt(diff, goose_checker.quota)

    prompt_template = PromptTemplate.from_template(
        base_prompt,
        partial_variables={
            "format_instructions": format_instructions,
            "diff_subprompt": diff_and_tokens_used["subprompt"],
        },
    )

    chain = prompt_template | model | output_parser

    output = chain.invoke({})
    return GooseCheckerResponse(
        file_name=diff.file_name,
        chain_of_thought=output["chain_of_thought_on_issues"],
        issues=output["list_issues"].split(","),
    )


def terraform_checker(
    diff: GitDiff, goose_checker: GooseChecker
) -> GooseCheckerResponse:

    # Core chain to analyze terraform diff
    response_schemas = [cot_issues,
                        list_issues]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    model = goose_checker._get_model()
    format_len = get_token_len(format_instructions)

    # 1. Build Context
    terraform_context = get_terraform_context(diff)
    # 2. get our model
    model = goose_checker._get_model()
    # 3. Build our Chain using context
    diff_and_tokens_used: dict = _build_diff_subprompt(diff, goose_checker.quota)

    quota_remain = (
        goose_checker.quota - diff_and_tokens_used["tokens_used"] - format_len
    )

    context_subprompt = ""
    for context in terraform_context:

        context_sub_subprompt = _build_context_subprompt(context, quota_remain)
        context_subprompt += context_sub_subprompt
        quota_remain = quota_remain - get_token_len(context_sub_subprompt)

        if quota_remain < 250:
            break

    prompt_template = PromptTemplate.from_template(
        terraform_prompt,
        partial_variables={
            "format_instructions": format_instructions,
            "context_subprompt": context_subprompt,
            "diff_subprompt": diff_and_tokens_used["subprompt"],
        },
    )

    chain = prompt_template | model | output_parser

    output = chain.invoke({})
    return GooseCheckerResponse(
        file_name=diff.file_name,
        chain_of_thought=output["chain_of_thought_on_issues"],
        issues=output["list_issues"].split(","),
    )


def approve_or_deny(
    responses: list[GooseCheckerResponse], goose_checker: GooseChecker
) -> ApprovalChainResponse:
    response_schemas = [improvements_aggregation, approve_or_deny_schema]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    model = goose_checker._get_model()

    evaluations_subprompt = ""

    for response in responses:
        evaluations_subprompt = f"""
        file_name: {response.file_name}
        Feedback: {response.chain_of_thought}
        """

    prompt_template = PromptTemplate.from_template(
        aggregation_prompt,
        partial_variables={
            "format_instructions": format_instructions,
            "evaluations_subprompt": evaluations_subprompt,
        },
    )

    chain = prompt_template | model | output_parser

    result = chain.invoke({})

    if isinstance(result['approve_or_deny'], str):
        if result['approve_or_deny'].lower().strip() == "true":
            result['approve_or_deny'] = True
        elif result['approve_or_deny'].lower().strip() == "false":
            result['approve_or_deny'] = False

    return ApprovalChainResponse(approved = result["approve_or_deny"], instructions_to_engineer = result["instructions_to_engineer"])
