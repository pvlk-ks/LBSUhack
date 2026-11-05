import os
import requests
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Boolean, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pgvector.sqlalchemy import Vector

app = FastAPI(title="LBSUHack Core API")

# Разрешаем CORS, чтобы Streamlit не ругался
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/olympiads_db")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://docker.internal")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Document(Base):
    __tablename__ = "olymp"
    id = Column(Integer, primary_key=True, index=True)
    grade = Column(Integer)
    subject = Column(String)
    stage = Column(String)
    year = Column(Integer)
    title = Column(String)
    text = Column(String)
    correct_answer = Column(String) # Поменял на String, так как ответы бывают дробными "0.6" или текстом
    level = Column(String)
    vector = Column(Vector(3))

# Автоматически создаем таблицы в Postgres
Base.metadata.create_all(bind=engine)

# Функция для безопасного подключения к сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция первичного наполнения базы, если она пустая
def seed_data():
    db = SessionLocal()
    if db.query(Document).count() == 0:
        demo_tasks = [
            Document(grade=5, subject="математика", stage="школьный", year=2024, 
                     title="Задача №1", text="Найдите длину вектора с координатами (3;4).", 
                     correct_answer="5", level="Легкий", vector=[1.0, 0.8, 0.0]),
            Document(grade=5, subject="математика", stage="школьный", year=2024, 
                     title="Задача №2", text="В прямоугольном треугольнике со сторонами 3, 4, 5 найдите косинус угла напротив стороны 3.", 
                     correct_answer="0.8", level="Средний", vector=[0.9, 0.5, 0.4]),
            Document(grade=5, subject="математика", stage="школьный", year=2024, 
                     title="Задача №3", text="Вычислите значение выражения: sin^2(45) + cos^2(45).", 
                     correct_answer="1", level="Сложный", vector=[0.2, 0.1, 1.0])
        ]
        db.add_all(demo_tasks)
        db.commit()
    db.close()

seed_data()

# Твоя Pydantic-модель для валидации данных от напарника
class BusinessModel(BaseModel):
    choice_class: str    # Ожидаем строку вида "5 класс" или просто "5"
    choice_subject: str  # Например, "математика"
    choice_stage: str    # Например, "школьный"

@app.post("/get-task")
def get_task(data: BusinessModel, db: Session = Depends(get_db)):
    # Вытаскиваем только цифры из строки класса (например, из "5 класс" сделает инт 5)
    try:
        grade_digits = int(''.join(filter(str.isdigit, data.choice_class)))
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат класса. Ожидается число или строка с числом.")

    # Делаем запрос в Postgres со всеми фильтрами напарника
    tasks = db.query(Document).filter(
        Document.grade == grade_digits,
        Document.subject.ilike(data.choice_subject.strip()),
        Document.stage.ilike(data.choice_stage.strip())
    ).all()

    if not tasks:
        return {"status": "empty", "result": []}

    # Формируем красивый ответ для фронтенда
    result_list = []
    for task in tasks:
        result_list.append({
            "id": task.id,
            "title": task.title,
            "text": task.text,
            "level": task.level,
            "year": task.year
        })

    return {
        "status": "success",
        "result": result_list
    }