from fastapi import FastAPI
import requests
from app.fws import *
from fastapi.responses import ORJSONResponse
app = FastAPI()
def trueurl(url):

    r = requests.head(url, allow_redirects=True)
    return r.url
@app.get("/sitemap/", response_class=ORJSONResponse)
async def sitemap(url:str):
    print('check url',url)
    # if not isvaliddomain(url):
    #     return {"urls": 'not a valid domain'}
    if url.startswith("http://"):
        pass
    elif url.startswith("https://"):
        pass
    else:
        url='https://'+url
    url =trueurl(url)

    urls= crawler(url,'report.txt',1)

    print(urls)

    # return {"urls": urls}
    return {"urls": urls}