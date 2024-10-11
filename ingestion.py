from dotenv import load_dotenv
import os
import sys
import io
load_dotenv()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from consts import INDEX_NAME

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import ReadTheDocsLoader
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from firecrawl.firecrawl import FirecrawlApp
from langchain.schema import Document

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def ingest_docs():
    loader = ReadTheDocsLoader("langchain-docs/api.python.langchain.com/en/latest", encoding='utf-8')
    raw_documents = loader.load()
    print(f"loaded {len(raw_documents)} documents")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50)
    documents = text_splitter.split_documents(raw_documents)
    print(f"split {len(documents)} documents")
    for doc in documents:
        new_url = doc.metadata["source"]
        new_url = new_url.replace("langchain-docs", "https:/")
        doc.metadata.update({"source": new_url})

    print(f"going to add {len(documents)} documents to pinecone")

    PineconeVectorStore.from_documents(
        documents, embeddings, index_name=INDEX_NAME
    )

def ingest_docs2() -> None:
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    url = "https://nextjs.org/docs"

    page_content = app.scrape_url(url=url,
                                        params={"onlyMainContent": True})
    print(page_content)
    doc = Document(page_content=str(page_content), metadata={"source": url})

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    docs = text_splitter.split_documents([doc])

    PineconeVectorStore.from_documents(docs, embeddings, index_name=os.getenv("INDEX_NAME"))


if __name__ == "__main__":
    ingest_docs2()