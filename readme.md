# Deploy fastAPI to Heroku using Docker

[FastAPI](https://fastapi.tiangolo.com/) Modern, fast, web framework for Python  
[Docker](https://www.docker.com/) Containerization software  
[Heroku](https://www.heroku.com/) Hosting platform

## Requirements

[Git](https://git-scm.com/) (or just download the repo)  
[Heroku cli](https://devcenter.heroku.com/articles/heroku-cli) (to run the heroku commands)


## db backend

https://github.com/vicogarcia16/fastapi_airtable


## Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/wanghaisheng/fastapi-docker-heroku)

## Instructions


>https://link-discovery.herokuapp.com/sitemap/?url=


https://link-discovery.herokuapp.com/sitemap/?url=https://x.hacking8.com/



#
https://github.com/sfu-db/connector-x/discussions/270

https://github.com/juanretamales/DataframeToDB




import connectorx as cx

postgres_url = "postgresql://username:password@server:port/database"
query = "SELECT * FROM lineitem"

cx.read_sql(postgres_url, query)





import pandas as pd
import dataframetodb
from dataframetodb import Table, refactor
from datetime import datetime
import os

nametable = "nameTable"
engine = dataframetodb.create_engine('sqlite:///{}.sqlite'.format(nametable)) #create engine for use SQLAlchemy
df = pd.read_csv("./dataset/data.csv") # Get the DataFrame
df = refactor(df) # Returns a dataframe with the correct dtype compatible with DataframeToDB.
table_class = Table(name=nametable, df=df) #create Table instance
table_class.toDb(df, engine, 'append') #insert data in database, in this example sqlite

