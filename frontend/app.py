import streamlit as st 
import pandas as pd
import requests

st.set_page_config(page_title="Подготовка к олимпиадам", layout="wide")

if "current_screen" not in st.session_state:
    st.session_state.current_screen = "login_screen"

if "current_task_index" not in st.session_state:
    st.session_state["current_task_index"] = 1




if st.session_state.current_screen == "login_screen":
    st.subheader("Привет! Вы находитесь на экране входа.")

    col_class, col_subject, col_stage = st.columns([1, 1, 1])

    with col_class:
        choice_class = st.radio(
    "Выберите класс:",
    ["5 класс", "6 класс", "7 класс", "8 класс", "9 класс", "10 класс", "11 класс"]
)
    with col_subject:
        choice_subject = st.radio(
    "Выберите предмет:",
    ["математика", "физика", "химия", "география", "обществоведение", "история вс.", "история Беларуси"]
)

    with col_stage:
            choice_stage = st.radio(
        "Выберите этап:",
        ["школьный", "районный", "областной", "республиканский"]
)
    choice_cfg = st.button("Применить Изменений", use_container_width=True)

if choice_cfg:
    payload = {
        "choice_class": choice_class,
        "choice_subject": choice_subject,
        "choice_stage": choice_stage
    }
    
    BACKEND_URL = "http://backend:8000/get-task"
    
    try:
        with st.spinner('обрабатываем ваши данные'):
            response = requests.post(BACKEND_URL, json=payload)
            data_json = response.json()
        
        if data_json.get("status") == "success":
            matrix = data_json.get("result")
            st.session_state.current_screen = "tasks"
            
    except Exception as e:
        st.error(f"Ошибка подключения к бэкенд-контейнеру: {e}")


if st.session_state.current_screen == "tasks":
    banner_tab, task_tab, check_result_tab, end_task_tab = st.tabs(1,4,1,1)
    current_task = st.session_state["current_task_index"]
    with task_tab:
        st.text(text=f"задача {current_task}")