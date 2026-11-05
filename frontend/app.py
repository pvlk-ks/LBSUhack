import streamlit as st 
import pandas as pd
import requests

st.set_page_config(page_title="Подготовка к олимпиадам", layout="wide")

if "current_screen" not in st.session_state:
    st.session_state.current_screen = "login_screen"


if st.session_state.current_screen == "login_screen":
    st.subheader("Привет! Вы находитесь на экране входа.")

    col_class, col_subject, col_stage = st.columns([1, 1, 1])

    with col_class:
        choice_class = st.radio(
    "Выберите класс:",
    [" 5 класс", "6 класс", "7 класс", "8 класс", "9 класс", "10 класс", "11 класс"]
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


# ---- ЛЕВАЯ КОЛОНКА (Ввод данных) ----
with col_sidebar:
    st.header("⚙️ Настройки")
    
    inv = st.slider("Стартовые инвестиции ($):", min_value=1000.0, max_value=50000.0, value=10000.0, step=1000.0)
    rev = st.slider("Ежемесячная выручка ($):", min_value=500.0, max_value=20000.0, value=3000.0, step=500.0)
    exp = st.slider("Ежемесячные расходы ($):", min_value=100.0, max_value=10000.0, value=1800.0, step=100.0)
    
    # НОВАЯ ФИЧА: Загрузчик файлов (просто визуализируем для MVP, что сайт умеет принимать Excel)
    uploaded_file = st.file_uploader("Или загрузите отчет (Excel/CSV):", type=["csv", "xlsx"])
    if uploaded_file is not None:
        st.success("Файл успешно загружен!")
    
    run_model = st.button("Запустить финансовую модель", use_container_width=True)

# ---- ПРАВАЯ КОЛОНКА (Основной контент) ----
with col_main:
    if run_model:
        payload = {
            "investments": inv,
            "monthly_revenue": rev,
            "monthly_expenses": exp
        }
        
        BACKEND_URL = "http://backend:8000/api/v1/calculate"
        
        try:
            with st.spinner('Считаем модель и строим прогнозы...'):
                response = requests.post(BACKEND_URL, json=payload)
                data_json = response.json()
            
            if data_json.get("status") == "success":
                matrix = data_json.get("result")
                df = pd.DataFrame(matrix)
                
                # ---- НОВАЯ ФИЧА 1: КРАСИВЫЕ МЕТРИКИ НАД ГРАФИКОМ ----
                # Вытаскиваем финальную цифру прибыли за последний год из DataFrame
                final_profit = df["Net_Profit"].iloc[-1]
                
                # Считаем простую точку окупаемости (инвестиции / чистая прибыль в месяц)
                monthly_profit = rev - exp
                if monthly_profit > 0:
                    payback_period = round(inv / monthly_profit, 1)
                    payback_text = f"{payback_period} мес."
                else:
                    payback_text = "Проект убыточен"

                # Создаем под-колонки для карточек метрик
                m_col1, m_col2 = st.columns(2)
                with m_col1:
                    if final_profit>0:
                        st.metric(label="💰 Финальный баланс (через 3 года)", value=f"${final_profit:,.2f}", delta=f"доход превысил вложения в {round(final_profit/inv, 1)}")
                    elif final_profit==0:
                        st.metric(label="💰 Финальный баланс (через 3 года)", value=f"${final_profit:,.2f}", delta=f"вложения равны доходу", delta_color="yellow", delta_arrow="off")
                    else:
                        st.metric(label="💰 Финальный баланс (через 3 года)", value=f"${final_profit:,.2f}", delta=f"вложения превысили доход в {round(-inv/final_profit, 1)}", delta_color="inverse", delta_arrow="down")
                with m_col2:
                    st.metric(label="⏱️ Срок окупаемости проекта", value=payback_text, delta="Идеально" if monthly_profit > 0 else "Внимание", delta_color="normal" if monthly_profit > 0 else "inverse", delta_arrow="up" if monthly_profit > 0 else "down")
                
                st.markdown("---") # Визуальный разделитель
                
                # Переименовываем колонки для красивого отображения на русском
                df_russian = df.rename(columns={"Timeline": "Срок прогноза", "Net_Profit": "Чистая прибыль ($)"})
                
                # ---- НОВАЯ ФИЧА 2: ИНТЕРАКТИВНЫЕ ВКЛАДКИ ----
                tab_charts, tab_data, tab_video = st.tabs(["📈 Аналитические Графики", "📋 Исходная Таблица", "видос"])
                
                with tab_charts:
                    st.subheader("Динамика роста капитала компании")
                    # Строим график по переименованным русским колонкам
                    st.line_chart(df_russian, x="Срок прогноза", y="Чистая прибыль ($)")
                    
                with tab_data:
                    st.subheader("Сводные данные от бэкенда")
                    st.dataframe(df_russian, use_container_width=True)

                with tab_video:
                    st.subheader("видосик")
                    st.video("https://www.youtube.com/watch?v=sHA_2QGqXAk")
                
        except Exception as e:
            st.error(f"Ошибка подключения к бэкенд-контейнеру: {e}")
    else:
        st.info("👈 Настройте параметры слева и нажмите кнопку «Запустить финансовую модель», чтобы увидеть графики и метрики.")
