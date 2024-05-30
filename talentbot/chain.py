import os
import time

import boto3
from langchain_anthropic import ChatAnthropic
from langchain_community.document_loaders import (
    UnstructuredFileLoader,
)
from langchain_core.documents import Document
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import (
    ConfigurableField,
    Runnable,
    RunnableLambda,
)
from langchain_openai import (
    ChatOpenAI,
)

from talentbot.document_loader import (
    DocDocumentLoader,
    DocxDocumentLoader,
    PDFDocumentLoader,
)
from talentbot.models import JsonResume
from talentbot.prompts import (
    RESTRUCTURE_CSV_PROMPT,
    RESTRUCTURE_PROMPT,
    SUMMARY_PROMPT,
)

s3 = boto3.client("s3")


def load_docunment(file) -> Document:
    is_xlsx = (
        file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    if is_xlsx:
        import pandas as pd
        from openpyxl import load_workbook

        wb = load_workbook(file)
        sheet = wb.active
        df = pd.DataFrame(sheet.values)
        text = df.to_csv(sep="\t", index=False)
        doc = Document(page_content=text, metadata={"is_csv": True})
    else:
        if file.type == "application/msword":
            loader_name = DocDocumentLoader
        elif (
            file.type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            loader_name = DocxDocumentLoader
        elif file.type == "application/pdf":
            loader_name = PDFDocumentLoader
        else:
            loader_name = UnstructuredFileLoader
        loader = loader_name(
            None,
            file=file,
            strategy="fast",  # without OCR
        )
        doc = loader.load()[0]
    return doc


def get_current_utc_time():
    now = time.time()
    current_time = time.strftime("%A, %B %d, %Y %H:%M", time.localtime(now))
    return current_time


def create_resume_chain(llm: Runnable):
    def route(data):
        if data.get("is_csv", False):
            return RESTRUCTURE_CSV_PROMPT
        return RESTRUCTURE_PROMPT

    jsonresume_chain = (
        RunnableLambda(route) | llm | JsonOutputParser(pydantic_object=JsonResume)
    )
    summary_chain = SUMMARY_PROMPT | llm | StrOutputParser()
    chain = (
        RunnableLambda(load_docunment)
        | {
            "input": lambda doc: doc.page_content,
            "is_csv": lambda doc: doc.metadata.get("is_csv", False),
            "current_time": lambda _: get_current_utc_time(),
        }
        | {
            "structured": jsonresume_chain,
            "summary": summary_chain,
        }
    )
    return chain


llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=4096,
).configurable_alternatives(
    # This gives this field an id
    # When configuring the end runnable, we can then use this id to configure this field
    ConfigurableField(id="llm"),
    default_key="openai_gpt_4o",
    anthropic_claude_3_opus=ChatAnthropic(
        model="claude-3-opus-20240229",
        temperature=0,
        max_tokens=4096,
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", "not_provided"),
    ),
    # gemini_pro=ChatVertexAI(
    #     model="gemini-pro",
    #     temperature=0,
    #     max_tokens=4096,
    #     convert_system_message_to_human=True,
    # ),
)

resume_chain = create_resume_chain(llm)
