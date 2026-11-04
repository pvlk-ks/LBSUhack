import streamlit as st 
#для создания красивых таблиц
import pandas as pd
#для общения с беком
import requests

st.set_page_config(page_title="LBSUhack Analytics", layout="wide")

st.title("📊 Экономическая Панель Управления (Прототип)")

st.sidebar.header("Экономические показатели")

# Заменили number_input на slider
# Параметры: ("Текст", минимальное значение, максимальное значение, значение по умолчанию, шаг)
inv = st.sidebar.slider("Стартовые инвестиции ($):", min_value=1000.0, max_value=50000.0, value=10000.0, step=1000.0)
rev = st.sidebar.slider("Ежемесячная выручка ($):", min_value=500.0, max_value=20000.0, value=3000.0, step=500.0)
exp = st.sidebar.slider("Ежемесячные расходы ($):", min_value=100.0, max_value=10000.0, value=1800.0, step=100.0)


if st.sidebar.button("Запустить финансовую модель"):
    # введенныe данныe от пользователяв формате json
    # до двуеточия --- названия переменных на беке, после --- переменные на фронте
    payload = {
    "investments": inv,
    "monthly_revenue": rev,
    "monthly_expenses": exp
    }
    
    #адрес точного эндпоинта внутри докер сети (подскажу на дебатах данные, которые хранятся в моих файлах. здесь ии не поможет)
    BACKEND_URL = "http://backend:8000/api/v1/calculate"
    
    try:
        #отправкa бек (указание адреса и прикрепление данных, которые автоматически из пайтон словаря( формат dict) преврвщаются в json)
        #в переменую записывается json ответ от сервера (мой return и статус ответа)
        response = requests.post(BACKEND_URL, json=payload)
        #перевод ответа от моего бека обратно в пайтон словарь, чтобы с ним было удобно работать
        data_json = response.json()
        
        #если мой бек отправил значение success, то переменая matrix будет равна данным, которые посчитаны в моем коде 
        if data_json.get("status") == "success":
            matrix = data_json.get("result")
            
            #перевод массива словарей в красивую таблицу
            df = pd.DataFrame(matrix)
            
            # Строим линейный график встроенной магией Стримлита одной строчкой
            st.subheader("📈 Динамика чистой прибыли (Прогноз на 3 года)")
            st.line_chart(df, x="Timeline", y="Net_Profit")
            
            # Выводим саму таблицу под графиком для проверки точных цифр
            st.subheader("📋 Сводная таблица расчетов")
            st.dataframe(df, use_container_width=True)
            
    except Exception as e:
        st.error(f"Ошибка подключения к бэкенд-контейнеру: {e}")