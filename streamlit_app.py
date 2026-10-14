from __future__ import annotations

import os
from dataclasses import asdict

import streamlit as st

from app.core.config import get_settings
from app.core.credential_store import (
    CredentialStoreError,
    delete_config,
    load_config,
    save_config,
)
from app.ingestion.parser import DocumentParseError
from app.services import KnowledgeService
from app.storage.repository import KnowledgeRepository

st.set_page_config(page_title="知源 · Knowledge Agent", page_icon="📚", layout="wide")

if not os.getenv("DEEPSEEK_API_KEY"):
    try:
        stored_config = load_config()
    except CredentialStoreError:
        stored_config = None
    if stored_config:
        os.environ["DEEPSEEK_API_KEY"] = stored_config.api_key
        os.environ["DEEPSEEK_MODEL"] = stored_config.model


@st.cache_resource
def get_service() -> KnowledgeService:
    settings = get_settings()
    return KnowledgeService(KnowledgeRepository(settings.database_path), settings)


service = get_service()
st.markdown("""
<style>
.stApp {background:linear-gradient(180deg,#f7f9fc,#eef3f8)}
.block-container {max-width:1120px;padding-top:2rem}
.hero {padding:2rem 2.2rem;border-radius:22px;color:white;background:linear-gradient(120deg,#172554,#1d4ed8 60%,#0891b2);margin-bottom:1.2rem}
.hero h1 {margin:0 0 .4rem;font-size:2.2rem}.hero p{margin:0;opacity:.88}
</style><div class="hero"><h1>知源 · Knowledge Agent</h1><p>上传资料，获得有来源、可核验的知识回答。没有证据，就不编造。</p></div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("知识库")
    knowledge_base = st.text_input("知识库名称", "default")
    with st.expander("DeepSeek API 设置", expanded=not bool(get_settings().llm_api_key)):
        st.caption("密钥由 Windows DPAPI 加密，仅当前 Windows 用户可以读取。")
        deepseek_key = st.text_input("API Key", type="password", placeholder="sk-...")
        deepseek_model = st.selectbox(
            "模型", ("deepseek-chat", "deepseek-reasoner", "deepseek-flash")
        )
        save_column, delete_column = st.columns(2)
        if save_column.button("保存", use_container_width=True):
            try:
                save_config(deepseek_key, deepseek_model)
                os.environ["DEEPSEEK_API_KEY"] = deepseek_key.strip()
                os.environ["DEEPSEEK_MODEL"] = deepseek_model
                get_settings.cache_clear()
                get_service.clear()
                st.rerun()
            except CredentialStoreError as exc:
                st.error(str(exc))
        if delete_column.button("删除", use_container_width=True):
            delete_config()
            os.environ.pop("DEEPSEEK_API_KEY", None)
            os.environ.pop("DEEPSEEK_MODEL", None)
            get_settings.cache_clear()
            get_service.clear()
            st.rerun()
        if get_settings().llm_api_key:
            st.success("DeepSeek 已配置")
        else:
            st.info("未配置时使用本地检索回答。")
    uploaded_files = st.file_uploader("上传资料", type=["pdf", "docx", "txt", "md"], accept_multiple_files=True)
    if st.button("解析并加入知识库", type="primary", disabled=not uploaded_files, use_container_width=True):
        for uploaded in uploaded_files or []:
            try:
                result = service.ingest(knowledge_base, uploaded.name, uploaded.getvalue())
                st.success(f"{uploaded.name}：已生成 {result['chunks']} 个片段")
            except (ValueError, DocumentParseError) as exc:
                st.error(f"{uploaded.name}：{exc}")
    st.divider()
    st.caption("当前文档")
    documents = service.repository.list_documents(knowledge_base)
    if not documents:
        st.info("还没有资料")
    for document in documents:
        col1, col2 = st.columns([4, 1])
        col1.caption(str(document["filename"]))
        if col2.button("删除", key=f"delete-{document['id']}"):
            service.repository.delete_document(str(document["id"]))
            st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("citations"):
            with st.expander(f"查看 {len(message['citations'])} 条引用"):
                for citation in message["citations"]:
                    page = f" · 第 {citation['page']} 页" if citation["page"] else ""
                    st.markdown(f"**{citation['source']}**{page}")
                    st.caption(citation["quote"])

question = st.chat_input("针对知识库提问……")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("正在检索并核对来源……"):
            try:
                answer = service.ask(knowledge_base, question)
                st.markdown(answer.text)
                if answer.citations:
                    with st.expander(f"查看 {len(answer.citations)} 条引用", expanded=True):
                        for citation in answer.citations:
                            page = f" · 第 {citation.page} 页" if citation.page else ""
                            st.markdown(f"**{citation.source}**{page} · 相关度 {citation.score:.2f}")
                            st.caption(citation.quote)
                st.session_state.messages.append({"role": "assistant", "content": answer.text, "citations": [asdict(c) for c in answer.citations]})
            except Exception as exc:
                st.error(f"回答失败：{exc}")
