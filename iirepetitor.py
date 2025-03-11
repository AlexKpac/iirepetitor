import streamlit as st
from deepseek_api import (
    get_access_token, sent_prompt_and_get_response,
    upload_file, get_image
)
st.title("ИИ репетитор")

if "file_processed" not in st.session_state:
    st.session_state.file_processed = False

if "access_token" not in st.session_state:
    try:
        st.session_state.access_token = get_access_token()
    except Exception as e:
        st.toast(f"Authorization error: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "initialized" not in st.session_state:
    st.session_state.messages.append(
        {"role": "assistant", "content": "Отправь мне задачу по математике и я научу тебя её решать"}
    )
    st.session_state.initialized = True

for msg in st.session_state.messages:
    if msg.get("is_image"):
        try:
            image_data = get_image(msg["content"], st.session_state.access_token)
            st.chat_message(msg["role"]).image(image_data)
        except Exception as e:
            st.error(f"Ошибка: {e}")
    else:
        st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Ваше сообщение"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Анализирую запрос..."):
        response, is_image = sent_prompt_and_get_response(
            prompt,
            st.session_state.access_token,
            messages=st.session_state.messages
        )
    st.rerun()

uploaded_file = st.file_uploader("Загрузите изображение с задачей", type=["jpg", "png", "jpeg"])
if uploaded_file and not st.session_state.file_processed:
    try:
        if uploaded_file.size > 15 * 1024 * 1024:
            st.error("Файл слишком большой (максимум 15 МБ)")
        else:
            with st.spinner("Загружаю изображение..."):
                file_id = upload_file(uploaded_file, st.session_state.access_token)

                st.session_state.messages.append({
                    "role": "user",
                    "content": file_id,
                    "is_image": True
                })

                with st.spinner("Решаю задачу..."):
                    response, is_image = sent_prompt_and_get_response(
                        "Реши задачу на изображении. Покажи пошаговое решение.",
                        st.session_state.access_token,
                        messages=st.session_state.messages,
                        attachments=[file_id]
                    )

                st.session_state.file_processed = True
                st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
elif uploaded_file:
    st.session_state.file_processed = False

col1, col2 = st.columns(2)
with col1:
    if st.button("Понятно"):
        st.session_state.messages.append({"role": "user", "content": "Спасибо, всё понятно"})
        with st.spinner("Формирую ответ..."):
            sent_prompt_and_get_response(
                "Спасибо, всё понятно",
                st.session_state.access_token,
                messages=st.session_state.messages
            )
        st.rerun()

with col2:
    if st.button("Не понятно"):
        st.session_state.messages.append({"role": "user", "content": "Объясните подробнее"})
        with st.spinner("Уточняю ответ..."):
            sent_prompt_and_get_response(
                "Объясните подробнее",
                st.session_state.access_token,
                messages=st.session_state.messages
            )
        st.rerun()