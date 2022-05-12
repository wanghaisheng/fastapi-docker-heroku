from .database import dbsession
from ..models.Shops import Shops,Shop_sitemaps
import json
import sqlalchemy
""" This file will have all function that make any direct query or manipulation in the database. So we can use this funtions as interface of the database. With this we have a single place to edit when some database code should change. 
"""


def Add_New_Shops_In_Db(shopdetail) -> None:
    """ This function insert video object in database
    """
    # newShopsDetails = Shops(
    #     url=url,
    #     title=title,
    #     thumbnail=thumbnail,
    #     downloadPercent=downloadPercent,
    #     videoquality=str(videoquality),
    #     savefile=savefile,
    # )
    dbsession.add(shopdetail)


    # and don't forget to commit your changes
    try:
        dbsession.commit()
    except sqlalchemy.exc.SQLAlchemyError  as e:
        dbsession.rollback()


def Url_In_Database(url) -> bool:
    return (dbsession.query(dbsession.query(Shops).filter(Shops.domain == url).exists()).scalar())


def Query_subdomain_In_db(url) -> list:
    data = dbsession.query(Shops).filter(Shops.domain == url).first()
    if data:
        subdomains=data.subdomains 
        return json.loads(subdomains)
    else:
        return []


def Update_subdomains_In_Db(subdomains, url) -> None:
    data = dbsession.query(Shops).filter(Shops.domain == url).first()
    data.subdomains = json.dumps(subdomains)
    dbsession.merge(data)


    # and don't forget to commit your changes
    try:
        dbsession.commit()
    except sqlalchemy.exc.SQLAlchemyError  as e:
        dbsession.rollback()

def Query_urls_list_In_Db(url) -> list:
    data = dbsession.query(Shops).filter(Shops.domain == url).first()
    if data:
        urls_list=data.urls_list
        return json.loads(urls_list)
    else:
        return []    
def Update_urls_list_In_Db(urls_list, url) -> None:
    data = dbsession.query(Shops).filter(Shops.domain == url).first()
    if data:
# There is another less obvious way though. To save as String by json.dumps(my_list) and then while retrieving just do json.loads(my_column). But it will require you to set the data in a key-value format and seems a bit in-efficient compared to the previous solution.

        data.urls_list = json.dumps(urls_list)
        dbsession.merge(data)
    else:
        data=Shops()
        data.urls_list = urls_list
        dbsession.merge(data)        


    # and don't forget to commit your changes
    try:
        dbsession.commit()
    except sqlalchemy.exc.SQLAlchemyError  as e:
        dbsession.rollback()


def Update_kv_In_Db(k,v,url) -> None:
    data = dbsession.query(Shops).filter(Shops.domain == url).first()
    data.k = v
    dbsession.merge(data)


    # and don't forget to commit your changes
    try:
        dbsession.commit()
    except sqlalchemy.exc.SQLAlchemyError  as e:
        dbsession.rollback()
