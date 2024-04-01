from langchain.output_parsers import ResponseSchema

approve_or_deny_schema = ResponseSchema(
    name="approve_or_deny",
    description="A boolean True or False to approve or deny.",
)
silly_mistakes_aggregation_schema = ResponseSchema(
    name="silly_mistakes",
    description="If there are any silly mistakes, explain clearly how to fix them here. Use numbered steps if possible.",
)

other_issues_explanation_schema = ResponseSchema(
    name="other_issues_explanation",
    description="A brief explanation. This is where you can include any other issues you find relating to performance or improving the code. If there are no other issues, you can leave this field blank.",
)

silly_mistakes_explaination_schema = ResponseSchema(
    name="silly_mistakes_explanation",
    description="A brief explanation of any silly mistakes found in the code. If there are no silly mistakes, you can leave this field blank.",
)
