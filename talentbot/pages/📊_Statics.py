import pandas as pd
import streamlit as st
from sqlalchemy import func, select

from talentbot.constants import DB_DSN
from talentbot.models import ResumeIndustry

st.set_page_config(page_title="Statics", page_icon="📊", layout="wide")
st.header("Statics")


conn = st.connection("sql", type="sql", url=DB_DSN)

with conn.session as s:
    stmt = (
        select(
            ResumeIndustry.industry, func.count(ResumeIndustry.id).label("resume_count")
        )
        .where(ResumeIndustry.confidence >= 0.8)
        .group_by(ResumeIndustry.industry)
        .order_by(func.count(ResumeIndustry.id).desc())
    )
    result = s.execute(stmt).all()

    df = pd.DataFrame(result, columns=["Industry", "Count"])
    top_5_industries = df.head(5).set_index("Industry")
    st.write("### Top 5 Industries")
    st.bar_chart(top_5_industries)
    st.write("### Resume Count by Industry")
    st.dataframe(df, hide_index=True)
