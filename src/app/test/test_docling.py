"""
@File    :  test_docling.py
@Author  :  CongPeiQiang
@Time    :  2026/5/25 12:06
@Desc    :  
"""
from langchain_pymupdf4llm import PyMuPDF4LLMLoader

file_path = "https://patentimages.storage.googleapis.com/aa/80/e5/7ef9a628254e36/CN1406291A.pdf"
loader = PyMuPDF4LLMLoader(file_path)
docs = loader.load()
print(docs)