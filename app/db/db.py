from sqlmodel import create_engine,Session,SQLModel
DB_URL="postgresql://postgres:test@localhost:5432/"
engine = create_engine(DB_URL,echo=True)
def init_db():
    """Initialize the database and create all tables"""
    try:
        # Import all models here to ensure they're registered with SQLModel
        from db.schema import User, Product, Order
        
        # Create all tables
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