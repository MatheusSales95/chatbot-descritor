import streamlit as st
import requests

st.title("🔥 DescrEVE: Assistente INPE")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Pergunte algo..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        r = requests.post("http://localhost:8000/api/v1/chat",
                          json={"text": prompt})
        res = r.json()
        with st.chat_message("assistant"):
            st.markdown(res["response"])
        st.session_state.messages.append(
            {"role": "assistant", "content": res["response"]})
    except:
        st.error("Erro de conexão com a API.")
