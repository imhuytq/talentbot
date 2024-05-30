import pandas as pd
import streamlit as st
from jinja2 import Environment, PackageLoader, select_autoescape
from sqlalchemy import select

from talentbot.constants import DB_DSN
from talentbot.models import Resume
from talentbot.utils import generate_signed_url

st.set_page_config(page_title="Resumes", page_icon="📄", layout="wide")


@st.cache_resource(ttl="1h")
def configure_env():
    env = Environment(
        loader=PackageLoader("talentbot", "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    return env


conn = st.connection("sql", type="sql", url=DB_DSN)
env = configure_env()
template = env.get_template("resume.md")
# template2 = env.get_template("resume.txt.jinja")


with conn.session as s:
    if not st.query_params.get("id"):
        count = s.query(Resume).count()
        st.header(f"Resumes ({count})")
        stmt = select(
            Resume.id,
            Resume.name,
            Resume.email,
            Resume.cv_file,
            Resume.created_at,
        ).order_by(Resume.created_at.desc())
        result = s.execute(stmt).all()

        df = pd.DataFrame(result, columns=["ID", "Name", "Email", "CV", "Created At"])
        df["ID"] = df["ID"].apply(lambda x: f"?id={x}")
        df["CV"] = df["CV"].apply(lambda x: generate_signed_url(x))
        st.dataframe(
            df,
            hide_index=True,
            column_config={
                "ID": st.column_config.LinkColumn(display_text="([0-9]+)"),
                "CV": st.column_config.LinkColumn(display_text="Download"),
            },
        )
    else:
        resume_id = st.query_params.get("id")
        resume = s.get(Resume, resume_id)
        st.header(resume.name)
        if resume.cv_file:
            cv_url = generate_signed_url(resume.cv_file)
            st.link_button("Download CV", cv_url)
        profile_tab, summary_tab = st.tabs(["Profile", "Summary"])

        with profile_tab:
            # profile = template2.render(**resume.data)
            # st.text(profile)
            profile = template.render(**resume.data)
            st.write(profile)

        with summary_tab:
            st.write(resume.summary)
