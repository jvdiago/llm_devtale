CODE_EXTRACTOR_TEMPLATE = """
Given the provided code snippet enclosed within the <<< >>> delimiters, your \
task is to output the classes and method names that are defined within the code. \
You must not include classes that are imported.
Additionally, you should include a concise top-level docstring that summarizes \
the purpose of the code snippet.

Your output must adhere to the following format:
classes=["class_name_1", "class_name_2", ...]
methods=["class_name_1::method_name_1", "class_name_2::method_name_2", ...]
summary="top-level docstring"

Code: <<< {code} >>>
"""

CODE_LEVEL_TEMPLATE = """
Your objective is to generate Google Style docstrings for code elements provided \
in the input. Additionally, you should include a concise top-level docstring that summarizes \
the purpose of the code snippet.

The input consists of a code snippet enclosed within the <<< >>> delimiters.

Your task involves the following steps:

1. Analyze the provided code snippet to locate and identify the methods and/or \
classes that are actually defined within the code snippet.
2. For each identified code element, generate a Google Style docstring.

Focus only on the code elements that are present and defined within the code snippet.
And please refrain from including docstrings within the code.

{format_instructions}

Do not introduce your answer, just output using the above JSON schema, and always \
use escaped newlines.

Input: <<< {code} >>>
"""

NO_CODE_FILE_TEMPLATE = """
Using the following file data enclosed within the <<< >>> delimeters write a \
top-file level concise summary that effectively captures the overall purpose and \
functionality of the file.

file data: <<< {information} >>>

Ensure your final summary is no longer than three sentences.
"""

FILE_LEVEL_TEMPLATE = """
The following summaries enclosed within the <<< >>> delimeters are derived from the \
same code file. Write a top-file level docstring that combines them into a concise  \
final summary that effectively captures the overall purpose and functionality of the \
entire code file.

Summaries: <<< {information} >>>

Ensure your final summary is no longer than three sentences.
"""

FOLDER_LEVEL_TEMPLATE = """
Generate a markdown text using the enclosed \
information within the <<< >>> delimiters as your context. \
Your output must strictly adhere to the provided structure below \
without adding any other section not mentioned on it.

This is the structure your output must have:
----------
#### <<<folder_name>>>
<<<folder_overview>>> (Provide a concise one-line sentence that describes the \
primary purpose of the folder, utilizing all the contextual details available.)

**Files list:**

- **<<<file_name>>>**: <<<file_description>>> (short description of \
what the file does.)
----------

Folder information: <<< {information} >>>

Ensure proper formatting and adhere to Markdown syntax guidelines.
Do not add sections that are not listed in the provided structure.
Do not backticks around the list titles and headers.
"""


ROOT_LEVEL_TEMPLATE = """
Generate a markdown text using the enclosed \
information within the <<< >>> delimiters as your context. \
Your output must strictly adhere to the provided structure below \
without adding any other section not mentioned on it.

This is the structure your output must have:
Structure:
----------
# <<<repository_name>>> (Please ensure that the initial letter \
is capitalized)

## Description
(Provide a concise one-line sentence that describes the primary \
purpose of the code, utilizing all the contextual details \
available.)

## Overview
(In this section, your task is to create a single, well-structured \
five-lines paragraph that concisely communicates the reasons behind the \
repository's creation, its objectives, and the mechanics underlying \
its functionality.)
----------

Repository information: <<< {information} >>>

Ensure proper formatting and adhere to Markdown syntax guidelines.
Do not add sections that are not listed in the provided structure.
"""

FOLDER_SHORT_DESCRIPTION_TEMPLATE = """
Generate a one-line description of the folder's purpose based on \
its following readme enclosed within the <<< >>> delimiters

README: <<< {information} >>>
"""

ORGANIZATION_TEMPLATE = """
Based on the information provided in the context enclosed with <<<>>> with the contents of the README file found within the code, the README file generated using LLMs and the project name extract the United Nations organization name that owns the project. If the organization name cannot be found in the Readme context try to extract it from the project name. The organization might be in full form or in acronym, use both to try to guess the organization.

<<< {information} >>>

The output should be in lower case and it should be the full name (no acronyms). Only output the name of the organization or an empty string, nothing else

Example of inputs: WFP, UNICC, World Health Organization
Example of outputs: world food program, united nations international children's emergency fund, world health organization
"""
