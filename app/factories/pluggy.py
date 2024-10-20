from app.utils.settings import Settings
from app.services.pluggy import PluggyService
from app.dal.pluggy import PluggyDal
from sqlalchemy.orm import Session 
from fastapi import Depends
from app.factories.database import get_db

settings = Settings()

def get_pluggy_dal(db: Session = Depends(get_db)) -> PluggyDal:
    dal = PluggyDal(db)
    try:
        yield dal
    finally:
        pass

def get_pluggy_service(
    dal: PluggyDal = Depends(get_pluggy_dal)
) -> PluggyService:
    service = PluggyService(settings, dal)
    try:
        yield service
    finally: 
        pass
