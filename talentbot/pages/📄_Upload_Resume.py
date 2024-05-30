import boto3
import streamlit as st
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import delete, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from talentbot.chain import resume_chain
from talentbot.constants import DB_DSN, INDEX_RESUMES, MODEL_OPTIONS
from talentbot.models import JsonResume, Resume, ResumeIndustry
from talentbot.retriever import create_vector_store

st.set_page_config(page_title="Upload Resume", page_icon="📄")
st.header("Upload Resume")


ALLOWED_EXTENSIONS = {"txt", "pdf", "doc", "docx", "xlsx"}

model_options = MODEL_OPTIONS


@st.cache_resource(ttl="1h")
def configure_vector_store(index_name):
    return create_vector_store(index_name)


def upsert_resume(
    session: Session, resume: JsonResume, cv_file: str, summary: str
) -> int:
    stmt = (
        pg_insert(Resume)
        .values(
            name=resume.name,
            email=resume.email,
            data=resume.dict(),
            cv_file=cv_file,
            summary=summary,
            updated_at=func.now(),
        )
        .on_conflict_do_update(
            index_elements=[Resume.email],
            set_=dict(
                name=resume.name,
                data=resume.dict(),
                cv_file=cv_file,
                summary=summary,
                updated_at=func.now(),
            ),
        )
        .returning(Resume.id)
    )

    result = session.execute(stmt)
    session.commit()
    resume_id = result.scalar()

    delete_stmt = delete(ResumeIndustry).where(ResumeIndustry.resume_id == resume_id)
    session.execute(delete_stmt)

    for industry in resume.prediction.industries:
        session.add(
            ResumeIndustry(
                resume_id=resume_id,
                industry=industry.name,
                confidence=industry.confidence,
            )
        )

    session.commit()
    return resume_id


def index_resume(db, text_splitter, resume_id, summary):
    query = {"query": {"match": {"metadata.resume_id": resume_id}}}
    response = db.client.search(index="resumes", body=query)
    ids = [hit["_id"] for hit in response["hits"]["hits"]]
    db.delete(ids, refresh_indices=False)
    doc = Document(page_content=summary, metadata={"resume_id": resume_id})
    docs = text_splitter.split_documents([doc])
    db.add_documents(docs)


def upload_resume(bucket, file_name, cv, mimetype="application/pdf"):
    s3_client = boto3.client("s3")
    try:
        s3_client.put_object(
            Bucket=bucket, Key=file_name, Body=cv, ContentType=mimetype
        )
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False
    return True


conn = st.connection("sql", type="sql", url=DB_DSN)
db = configure_vector_store(INDEX_RESUMES)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=250)

model = st.sidebar.selectbox(
    "Select a model you want to use",
    list(model_options.keys()),
    format_func=lambda x: model_options[x],
)

with st.form("upload_form", clear_on_submit=True):
    resumes = st.file_uploader(
        "Select the resume(s)", type=ALLOWED_EXTENSIONS, accept_multiple_files=True
    )
    submitted = st.form_submit_button("Upload")

    if submitted:
        if model is None:
            st.error("Please select a model")
        elif len(resumes) == 0:
            st.error("Please upload a resume")
        else:
            with st.spinner("Processing..."):
                result = resume_chain.with_config(configurable={"llm": model}).batch(
                    resumes
                )
                ok = []
                with conn.session as s:
                    for i, res in enumerate(result):
                        original_file = resumes[i]
                        original_file.seek(0)
                        original_file_name = original_file.name
                        s3_file_name = (
                            f"resumes/{original_file.file_id}/{original_file_name}"
                        )
                        if not upload_resume(
                            "talentbot", s3_file_name, original_file, original_file.type
                        ):
                            st.error(f"Error uploading {original_file_name}")
                            continue
                        structured = res.get(
                            "structured", {"error": "Cannot process the resume"}
                        )
                        summary = res.get("summary")
                        if "error" in structured or summary == "I don't know":
                            st.error(
                                f"Error processing {original_file_name}: {structured['error']}"
                            )
                            continue
                        st.success(f"Processed {original_file_name}")
                        data = JsonResume.parse_obj(structured)
                        email = data.email
                        resume_id = upsert_resume(s, data, s3_file_name, summary)
                        doc = Document(
                            page_content=summary, metadata={"resume_id": resume_id}
                        )
                        index_resume(db, text_splitter, resume_id, summary)
                        ok.append(resume_id)

                if len(ok) > 0:
                    st.success(f"{len(ok)} resumes processed")
                    st.page_link(
                        "pages/🛠️_[DEV]_Rebuild_Index.py",
                        label="[DEV] Rebuild index",
                        icon="🔄",
                    )
