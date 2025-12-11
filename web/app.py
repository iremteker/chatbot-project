import streamlit as st
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from chatbot.agents.orchestrator import OrchestratorAgent

if "agent" not in st.session_state:
    st.session_state.agent= OrchestratorAgent()
agent = st.session_state.agent


st.title("AI Chatbot")
st.write("Bu chatbot üzerinden hava durumunu sorabilir, kayıt olma işlemi yapabilir veya normal sohbet edebilirsiniz.")

user_input = st.text_input("Bir mesaj yazın: ")

if user_input:
    response = agent.run(user_input)

    st.markdown("Chatbot Yanıtı: ")

    if isinstance(response, dict):
        st.json(response)
    else:
        st.write(response)