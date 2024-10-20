from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.dal.database import SessionLocal    

def get_db() -> Session:
    db = SessionLocal()
    
    try:
        db.begin()
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    else:
        db.commit()
    finally:
        db.close()
