import os
from langchain_mistralai import ChatMistralAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from .utils import transform_text_to_docs

llm = ChatMistralAI(model="mistral-large-latest")

def save_to_readme(
    content: str,
    filename: str = "crawler.md",
    ai_prompt: str = "Write a concise summary of the following"
):
    """
    Save the processed content in the data/processed folder (by default,
    .md file). Before that, build a prompt and invoke the model
    to generate a summary.
    """

    
    processed_dir = os.path.join("data", "processed")
    os.makedirs(processed_dir, exist_ok=True)

    
    output_path = os.path.join(processed_dir, filename)

    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"{ai_prompt}\n\n{{context}}")
    ])

    chain = create_stuff_documents_chain(llm, prompt)

    
    docs = transform_text_to_docs(content)
    result = chain.invoke({"context": docs})

    
    print("Generated summary snippet:", result[:50])
    with open(output_path, "a", encoding="utf-8") as file:
        file.write(result + "\n\n")
