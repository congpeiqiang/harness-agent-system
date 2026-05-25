from langchain_pymupdf4llm import PyMuPDF4LLMLoader

file_path = "../resources/旅行日记.pdf"
# loader = PyMuPDF4LLMLoader(file_path)
# doc = loader.load()
# print(doc[0].page_content)

from langchain_community.document_loaders.parsers import LLMImageBlobParser
from langchain_openai import ChatOpenAI
from app.core.llms import image_llm_model
loader = PyMuPDF4LLMLoader(
    "../resources/旅行日记.pdf",
    mode="single",
    extract_images=True,
    table_strategy="lines",
    images_parser=LLMImageBlobParser(
        model=image_llm_model
    ),
)
docs = loader.load()

print(docs[0].page_content)