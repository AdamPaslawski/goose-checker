from langchain.output_parsers import ResponseSchema

approve_or_deny_schema = ResponseSchema(
    name="approve_or_deny",
    description="A boolean True or False to approve or deny the changes. A True to approve, False to deny.",
)
improvements_aggregation = ResponseSchema(
    name="instructions_to_engineer",
    description="Write feedback to the engineer. If there are any mistakes or improvements include them here, explain clearly how to fix them. Use numbered steps if possible.",
)

cot_issues = ResponseSchema(
    name="chain_of_thought_on_issues",
    description="Explain fully any issues you see in the code.",
)

list_issues = ResponseSchema(
    name="list_issues",
    description="based on your chain_of_thought on issues, list the issues you see in the code separate each issue with a comma.",
)
