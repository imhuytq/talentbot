import time
from typing import List, Optional, Type

import pandas as pd
from jinja2 import Environment, PackageLoader, select_autoescape
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import (
    Runnable,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from talentbot.constants import BASE_URL
from talentbot.models import Resume
from talentbot.prompts import RERANK_PROMPT

env = Environment(
    loader=PackageLoader("talentbot", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)
template = env.get_template("resume.txt.jinja")

_THRESHOLD = 70


def generate_resume_url(resume) -> str:
    return f"{BASE_URL}/Resumes?id={resume.id}"
    # return generate_signed_url(resume.cv_file, 3600 * 8)


class ResumeSearchInput(BaseModel):
    jd: str = Field(description="should be a job description")


class ResumeSearchTool(BaseTool):
    llm: Runnable
    retriever: BaseRetriever
    sesssion: Session
    name = "resume_search"
    description = "useful when looking for resumes that match a job description."
    args_schema: Type[BaseModel] = ResumeSearchInput

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def _run(
        self, jd: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> List[dict]:
        """Use the tool."""
        documents = self.retriever.invoke(jd)
        resume_ids = [doc.metadata["resume_id"] for doc in documents]
        stmt = select(
            Resume.id, Resume.name, Resume.data, Resume.summary, Resume.cv_file
        ).where(Resume.id.in_(resume_ids))
        result = self.sesssion.execute(stmt).all()
        now = time.time()
        current_time = time.strftime("%A, %B %d, %Y %H:%M", time.localtime(now))
        chain = RERANK_PROMPT | self.llm | JsonOutputParser()
        inputs = []
        for row in result:
            txt = template.render(**row.data)
            inputs.append(
                {"id": row.id, "jd": jd, "resume": txt, "current_time": current_time}
            )

        results = chain.batch(inputs)
        resumes = []
        for i, resume in enumerate(result):
            rank_result = results[i]
            score = int(rank_result["score"])
            if score >= _THRESHOLD:
                reason = rank_result["reason"]
                resumes.append(
                    {
                        "id": resume.id,
                        "name": resume.name,
                        "score": score,
                        "reason": reason,
                        "resume_url": generate_resume_url(resume),
                    }
                )

        if not resumes:
            return []

        df = pd.DataFrame(resumes)
        # sort by score
        df = df.sort_values(by="score", ascending=False)
        # remove score column
        df = df.drop(columns=["score"])
        return df.to_dict(orient="records")


class ResumeSummarizationInput(BaseModel):
    id: str | int = Field(description="should be a resume id")


class ResumeSummarizationTool(BaseTool):
    sesssion: Session
    name = "resume_summarization"
    description = "useful when you want to summarize a resume."
    args_schema: Type[BaseModel] = ResumeSummarizationInput

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def _run(
        self, id: str | int, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> List[dict]:
        """Use the tool."""
        resume_id = int(id)
        resume = self.sesssion.get(Resume, resume_id)
        if not resume:
            return "Resume not found"
        return resume.summary


class ResumeDetailsInput(BaseModel):
    id: str | int = Field(description="should be a resume id")


class ResumeDetailsTool(BaseTool):
    sesssion: Session
    name = "resume_details"
    description = "useful when you want to get details of a resume."
    args_schema: Type[BaseModel] = ResumeDetailsInput

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def _run(
        self, id: str | int, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> List[dict]:
        """Use the tool."""
        resume_id = int(id)
        resume = self.sesssion.get(Resume, resume_id)
        if not resume:
            return "Resume not found"
        txt = template.render(**resume.data)
        return txt
