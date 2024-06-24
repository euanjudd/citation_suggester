# Academic Citation Suggester

## Overview

The Academic Citation Suggester is a tool to help researchers quickly find relevant academic citations. This tool leverages the capabilities of large language models (LLMs) to provide more accurate and contextually relevant citation suggestions compared to traditional keyword-based search methods.

## Inspiration

Autocomplete takes the last few words and picks the word that most commonly comes next. This fails us often and so obviously it will fail LLMs often too. To predict the next token more accurately, it will have to understand the meaning of what came before and apply reasoning to predict what comes next. It is this that allows LLMs to discern the primary topic of a text, such as "soft robotics," even if those exact words are not used. This capability makes LLMs a powerful tool for identifying relevant keywords, enhancing the process of finding relevant academic references.

## How to Use

- Paste the full text of your document into the first textbox.
- Enter the specific sentence that requires a citation in the second textbox.
- Click the "Suggest Citations" button to receive citation suggestions.

## Tools Used

- **Replicate API**: Used Llama 3 8b Instruct to extract keywords from user input.
- **CrossRef API**: Accessed relevant academic citations.
- **Django**: Created a user-friendly web interface for inputting documents and displaying citation suggestions.