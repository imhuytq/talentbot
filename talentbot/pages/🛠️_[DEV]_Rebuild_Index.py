import time

import streamlit as st
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import select

from talentbot.constants import DB_DSN, INDEX_RESUMES
from talentbot.models import Resume
from talentbot.retriever import create_vector_store


@st.cache_resource(ttl="1h")
def configure_vector_store(index_name):
    return create_vector_store(index_name)


st.set_page_config(page_title="[DEV] Rebuild Index", page_icon="🛠️")
st.header("[DEV] Build Index")
st.warning(
    """\
This page is for development purposes only.
It is used to rebuild the search index for resumes.
In production, the index is automatically updated when a new resume is uploaded.\
""",
    icon=":material/warning:",
)

db = configure_vector_store(INDEX_RESUMES)

conn = st.connection("sql", type="sql", url=DB_DSN)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=250)

with st.form("check_form", clear_on_submit=True):
    submitted = st.form_submit_button("Check Index Status")

    if submitted:
        with st.spinner("Checking index status..."):
            # query = {"query": {"match": {"metadata.resume_id": 1}}}
            # response = db.client.search(index="resumes", body=query)
            # ids = [hit["_id"] for hit in response["hits"]["hits"]]
            # st.text(ids)
            # db.delete(ids, refresh_indices=False)
            # doc = Document(page_content=summary, metadata={"resume_id": resume_id})
            # docs = text_splitter.split_documents([doc])
            # query = {"query": {"match": {"metadata.resume_id": 1}}}
            # response = db.client.search(index="resumes", body=query)
            # ids = [hit['_source']['id'] for hit in response["hits"]["hits"]]
            # st.text(ids)
            count = db.client.count(index="resumes").get("count", 0)
            if count > 0:
                st.success(f"Index contains {count} documents")
            else:
                st.error("Index is empty")

with st.form("form", clear_on_submit=True):
    submitted = st.form_submit_button("Rebuild Index")

    if submitted:
        with st.spinner("Rebuilding index..."):
            with conn.session as s:
                try:
                    db.delete_index()
                except Exception:
                    pass
                time.sleep(1)
                stmt = select(Resume.id, Resume.summary).order_by(
                    Resume.created_at.desc()
                )
                result = s.execute(stmt).all()
                docs = [
                    Document(page_content=res.summary, metadata={"resume_id": res.id})
                    for res in result
                ]
                docs = text_splitter.split_documents(docs)
                st.write(db.add_documents(docs))

                st.success("Index rebuilt successfully")
