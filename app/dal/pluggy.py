from sqlalchemy.orm import Session, load_only
from app.models.models import PluggyConfig
from datetime import datetime

class PluggyDal():
    
    def __init__(self, db_session: Session):
        self.db: Session = db_session

    def get_pluggy_api_key(self) -> PluggyConfig:
        return self.db.query(PluggyConfig).options(load_only("api_key", "api_key_expiration")).first()
    
    def get_pluggy_api_key(self) -> PluggyConfig:
        return self.db.query(PluggyConfig).options(load_only(PluggyConfig.api_key, PluggyConfig.api_key_expiration)).first()
    
    def get_pluggy_connect_token(self):
        return self.db.query(PluggyConfig).options(
            load_only(PluggyConfig.connect_token, PluggyConfig.connect_token_expiration)
        ).first()
    
    def create_pluggy_api_key(self, api_key: str, expiration: datetime):
        pluggy_config = PluggyConfig(
            api_key=api_key,
            api_key_expiration=expiration
        )
        self.db.add(pluggy_config) 
        self.db.commit() 

    def update_pluggy_api_key(self, api_key: str, expiration: datetime):
        pluggy_config = self.db.query(PluggyConfig).first()
        
        if pluggy_config:

            pluggy_config.api_key = api_key
            pluggy_config.api_key_expiration = expiration
            self.db.commit()  
        else:
            self.create_pluggy_api_key(api_key, expiration)

    def update_pluggy_connect_token(self, connect_token: str, expiration: datetime):
        pluggy_config = self.db.query(PluggyConfig).first()
        
        if pluggy_config:

            pluggy_config.connect_token = connect_token
            pluggy_config.connect_token_expiration = expiration
            self.db.commit() 
        else:
            self.create_pluggy_connect_token(connect_token, expiration)

    def create_pluggy_connect_token(self, connect_token: str, expiration: datetime):

        pluggy_config = PluggyConfig(
            connect_token=connect_token,
            connect_token_expiration=expiration
        )
        self.db.add(pluggy_config)
        self.db.commit()