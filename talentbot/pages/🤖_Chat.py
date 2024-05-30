from typing import Any, Dict, List, Optional
from uuid import UUID

import streamlit as st
from langchain.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
from langchain.callbacks.base import BaseCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from talentbot.chain import (
    llm,
)
from talentbot.constants import DB_DSN, INDEX_RESUMES, MODEL_OPTIONS
from talentbot.prompts import CHAT_PROMPT
from talentbot.retriever import create_retriever, create_vector_store
from talentbot.tools import ResumeDetailsTool, ResumeSearchTool, ResumeSummarizationTool

st.set_page_config(page_title="Chat", page_icon="🤖")


@st.cache_resource(ttl="1h")
def configure_vector_store(index_name):
    return create_vector_store(index_name)


conn = st.connection("sql", type="sql", url=DB_DSN)
vector_store = configure_vector_store(INDEX_RESUMES)
retriever = create_retriever(llm, vector_store)

resume_search_tool = ResumeSearchTool(
    llm=llm,
    retriever=retriever,
    sesssion=conn.session,
)
resume_summarization_tool = ResumeSummarizationTool(
    sesssion=conn.session,
)
resume_details_tool = ResumeDetailsTool(
    sesssion=conn.session,
)
tools = [resume_search_tool, resume_summarization_tool, resume_details_tool]
agent = create_tool_calling_agent(llm, tools, CHAT_PROMPT)
agent_executor = AgentExecutor(
    agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
)
msgs = StreamlitChatMessageHistory()
agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    # This is needed because in most real world scenarios, a session id is needed
    # It isn't really used here because we are using a simple in memory ChatMessageHistory
    lambda session_id: msgs,
    input_messages_key="input",
    history_messages_key="chat_history",
)


model_options = MODEL_OPTIONS
model = st.sidebar.selectbox(
    "Select a model you want to use",
    list(model_options.keys()),
    format_func=lambda x: model_options[x],
)


class ToolStreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.last_container = None

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when tool starts running."""
        tool_name = serialized["name"]
        if tool_name == resume_search_tool.name:
            msg = "Searching resumes to match the job description..."
        elif tool_name == resume_summarization_tool.name:
            msg = "Summarizing resume..."
        elif tool_name == resume_details_tool.name:
            msg = "Getting resume details..."
        self.last_container = self.container.empty()
        self.last_container.status(msg)

    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when tool ends running."""
        self.last_container.empty()


class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)


for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)


if msg := st.chat_input():
    st.chat_message("user").write(msg)
    with st.chat_message("assistant"):
        message_placeholder = st.container()
        empty = message_placeholder.empty()
        # container.status("running")
        # message_placeholder.markdown("Running...")
        # st.write("heklo")
        st_callback = ToolStreamHandler(message_placeholder)
        # e.status("running")
        # st_callback = StreamlitCallbackHandler(st.container())
        stream_handler = StreamHandler(empty)
        response = agent_with_chat_history.invoke(
            {"input": msg},
            {
                "configurable": {"session_id": "any", "llm": model},
                "callbacks": [st_callback, stream_handler],
            },
        )
