from sqlmodel import create_engine,Session,SQLModel
from config.secrets import DB_URL
engine = create_engine(DB_URL,echo=False)
def init_db():
    try:
        SQLModel.metadata.create_all(engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        raise
def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()