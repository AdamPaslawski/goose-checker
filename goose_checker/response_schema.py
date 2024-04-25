from langchain.output_parsers import ResponseSchema

approve_or_deny_schema = ResponseSchema(
    name="approve_or_deny",
    description="A boolean True or False to approve or deny the changes. A True to approve, False to deny.",
)
improvements_aggregation = ResponseSchema(
    name="instructions_to_engineer",
    description="Feedback to the engineer based on the issues. explain clearly how to fix them. Use numbered steps if possible.",
)

cot_issues = ResponseSchema(
    name="chain_of_thought_on_issues",
    description="Full thought process on issues within the code",
)

list_issues = ResponseSchema(
    name="list_issues",
    description="A comma separated list of issues found in the code",
)
