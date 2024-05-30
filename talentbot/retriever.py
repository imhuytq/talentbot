import logging
from typing import List

import boto3
import boto3.session
from langchain.retrievers.multi_query import (
    MultiQueryRetriever as BaseMultiQueryRetriever,
)
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_core.callbacks import (
    AsyncCallbackManagerForRetrieverRun,
    CallbackManagerForRetrieverRun,
)
from langchain_core.documents import Document
from opensearchpy import AWSV4SignerAuth, RequestsHttpConnection

from talentbot.prompts import SEARCH_QUERY_PROMPT

logger = logging.getLogger(__name__)

service = "aoss"  # must set the service as 'aoss'
region = "ap-southeast-1"
credentials = boto3.Session().get_credentials()
# awsauth = AWS4Auth(refreshable_credentials=credentials, region=region, service=service)
auth = AWSV4SignerAuth(credentials, region, service)


class MultiQueryRetriever(BaseMultiQueryRetriever):
    def unique_union(self, documents: List[Document]) -> List[Document]:
        unique_documents = super().unique_union(documents)
        # remove same source metadata
        seen = set()
        new_documents = []
        for doc in unique_documents:
            if doc.metadata["resume_id"] not in seen:
                seen.add(doc.metadata["resume_id"])
                new_documents.append(doc)

        return new_documents

    def generate_queries(
        self, question: str, run_manager: CallbackManagerForRetrieverRun
    ) -> List[str]:
        """Generate queries based upon user input.

        Args:
            question: user query

        Returns:
            List of LLM generated queries that are similar to the user input
        """
        lines = super().generate_queries(question, run_manager)
        filtered_lines = [line for line in lines if line.strip()]
        if self.verbose:
            logger.info(f"Filtered generated queries: {filtered_lines}")
        return filtered_lines

    async def agenerate_queries(
        self, question: str, run_manager: AsyncCallbackManagerForRetrieverRun
    ) -> List[str]:
        """Generate queries based upon user input.

        Args:
            question: user query

        Returns:
            List of LLM generated queries that are similar to the user input
        """
        lines = await super().generate_queries(question, run_manager)
        filtered_lines = [line for line in lines if line.strip()]
        if self.verbose:
            logger.info(f"Filtered generated queries: {filtered_lines}")
        return filtered_lines


def create_vector_store(index_name):
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    docsearch = OpenSearchVectorSearch(
        index_name=index_name,
        embedding_function=embedding_function,
        opensearch_url="https://ax2dqkndahwt0w9xe6f2.ap-southeast-1.aoss.amazonaws.com",
        http_auth=auth,
        use_ssl=True,
        timeout=300,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        engine="faiss",
    )
    return docsearch


def create_retriever(llm, vector_store):
    retriever = MultiQueryRetriever.from_llm(
        retriever=vector_store.as_retriever(search_kwargs={"k": 20}),
        llm=llm,
        prompt=SEARCH_QUERY_PROMPT,
        # include_original=True,
    )
    return retriever
