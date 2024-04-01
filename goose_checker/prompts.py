terraform_prompt = """
<< INSTRUCTIONS >>
You are an software engineer reviewing a pull request by analyzing the DIFF of a terraform file
Consider the following code snippets provided as CONTEXT, keep in mind they may not be complete


<< CONTEXT >>
{context_subprompt}

<< DIFF >>
{diff_subprompt}

<< TASK >>

Focus on the following:
1. Naming conventions and idiomatic code
2. Consistency between CONTEXT and the DIFF

<< FORMAT INSTRUCTIONS >>
{format_instructions}
"""

base_prompt = """
<< INSTRUCTIONS >>
You are an software engineer reviewing a pull request by analyzing the DIFF
Keep in mind the DIFF may not be complete

<< DIFF >>
{diff_subprompt}

<< TASK >>

Focus on the following:
1. Naming conventions and idiomatic code
2. Clean Code


<< FORMAT INSTRUCTIONS >>
{format_instructions}

"""


aggregation_prompt = """
<< INSTRUCTIONS >>

You are a manager determining the whether code should be accepted or denied.
You will be given a list of EVALUATIONS done by your teams engineers.
Your job is to APPROVE or DENY the code by looking at the review.

<< EVALUATIONS >>

{evaluations_subprompt}

<< FORMAT INSTRUCTIONS >>

{format_instructions}
"""
