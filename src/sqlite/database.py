from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from ..models.Shops import  *


print('running')
conn_string = 'sqlite:///data.sqlite3'
engine = create_engine(conn_string)
Base.metadata.create_all(engine)  # here we create all tables
Session = sessionmaker(bind=engine)
dbsession = Session()


