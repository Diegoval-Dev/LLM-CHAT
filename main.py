from backend.core2 import run_llm
import streamlit as st
from streamlit_chat import message

st.header("NextJS - Documentation Helper Bot")

# Preguntas relacionadas con Next.js
questions = [
    "¿Qué es Next.js y cuáles son sus principales características?",
    "¿Qué novedades trae",
    "¿Cómo funciona el enrutamiento en y qué cambios hay respecto a versiones anteriores?",
    "¿Cuáles son las ventajas de usar el App Router4?",
    "¿Cómo puedo optimizar el rendimiento?"
]


for question in questions:
    if st.button(question):
        st.session_state["user_prompt_history"].append(question)


prompt = st.text_input("Prompt", placeholder="Enter Your prompt here")


if (
        "chat_answers_history" not in st.session_state
        and "user_prompt_history" not in st.session_state
        and "chat_history" not in st.session_state
):
    st.session_state["chat_answers_history"] = []
    st.session_state["user_prompt_history"] = []
    st.session_state["chat_history"] = []


def create_sources_string(source_urls: set[str]) -> str:
    if not source_urls:
        return ""
    sources_list = list(source_urls)
    sources_list.sort()
    sources_string = "Sources:\n"
    for i, source in enumerate(sources_list):
        corrected_source = source.replace('\\', '/')
        sources_string += f"- [{corrected_source}]({corrected_source})\n"  # Mostrar la URL como texto del enlace
    return sources_string


if prompt or st.session_state["user_prompt_history"]:
    user_input = prompt or st.session_state["user_prompt_history"][-1]

    with st.spinner(text="Loading sources..."):
        generated_response = run_llm(
            query=user_input,
            chat_history=st.session_state["chat_history"],
        )
        sources = set([doc.metadata["source"] for doc in generated_response["source"]])
        formatted_response = (
            f"{generated_response['result']}\n\n{create_sources_string(sources)}"
        )

        # Guardar el historial de chat
        st.session_state["chat_answers_history"].append(formatted_response)
        st.session_state["chat_history"].append(("human", user_input))
        st.session_state["chat_history"].append(("ai", generated_response["result"]))

    # Mostrar el historial de la conversación
    if "chat_answers_history" in st.session_state:
        for generated_response, user_query in zip(
                st.session_state["chat_answers_history"],
                st.session_state["user_prompt_history"]
        ):
            message(user_query, is_user=True)
            st.markdown(generated_response, unsafe_allow_html=True)
