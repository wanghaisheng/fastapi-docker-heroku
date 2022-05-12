from .database import dbsession
from ..models.Shops import Shops
import os



def Query_subdomain_In_db(url) -> list:
    domain=url
    urls=[]
    data = dbsession.table("shops").select(
        'subdomains').eq("domain", domain).execute()
    # print(type(data))
    # print('existing db',len(dbsession.table("tiktoka_douyin_users").select('uid').execute()[0]),data,data[0])
    if len(data.data) > 0:
        print('this domain exist', domain, data.data)
        urls = data.data
    
    return urls        


def Query_urls_list_In_Db(url) -> list:
    domain=url
    urls=[]
    data = dbsession.table("shops").select(
        'urls_list').eq("domain", domain).execute()
    # print(type(data))
    # print('existing db',len(dbsession.table("tiktoka_douyin_users").select('uid').execute()[0]),data,data[0])
    if len(data.data) > 0:
        print('this domain exist', domain, data.data)
        urls = data.data
    return urls        

def Add_New_Shops_In_Db(tablename, shopdetail, domain) -> bool:
    try:
        data = dbsession.table(tablename).update(
            shopdetail).eq("domain", domain).execute()
        return True
    except:
        # raise Exception
        return False


def supabaseop(tablename, domaininfo) -> bool:
    try:
        data = dbsession.table(tablename).insert(domaininfo).execute()
        return True
    except:
        # raise Exception
        return False




