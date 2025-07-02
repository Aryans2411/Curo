# db.py
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))
    conditions = Column(Text)
    allergies = Column(Text)
    medications = Column(Text)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime)

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    rating = Column(Integer)
    comment = Column(Text)
class ChatFeedback(Base):
    __tablename__ = 'chat_feedback'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(Text)
    answer = Column(Text)
    feedback = Column(Integer) # 1 for 👍, 0 for 👎

class PrescriptionFeedback(Base):
    __tablename__ = 'prescription_feedback'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String(255))
    result = Column(Text)
    feedback = Column(Integer)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def init_db():
    Base.metadata.create_all(bind=engine)

# For testing the connection and creating tables
if __name__ == "__main__":
    try:
        init_db()
        print("✅ Tables created and database connected!")
    except Exception as e:
        print("❌ Database connection failed:", e)
