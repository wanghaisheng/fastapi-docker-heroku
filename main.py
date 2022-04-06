from fastapi import FastAPI
import requests
from app.fws import *
from fastapi.responses import ORJSONResponse
import uvicorn
from pywebio.input import *
from pywebio.io_ctrl import Output, OutputList
from pywebio.output import *
from pywebio.platform import seo
from pywebio.platform.page import config
from pywebio.session import run_js, set_env
from pywebio.platform.fastapi import asgi_app
import time
import pywebio_battery as battery
from app.constants import *
app = FastAPI()
apiapp = FastAPI()
def trueurl(url):

    r = requests.head(url, allow_redirects=True)
    return r.url
@apiapp.get("/sitemap/", response_class=ORJSONResponse)
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



@config(theme="minty",title=SEO_TITLE, description=SEO_DESCRIPTION)
def index() -> None:
    # Page heading
    put_html(LANDING_PAGE_HEADING)
    lang='English'
    if lang == 'English':
        LANDING_PAGE_DESCRIPTION = LANDING_PAGE_DESCRIPTION_English

    with use_scope('introduction'):
        # put_html(PRODUCT_HUNT_FEATURED_BANNER)
        # put_html(LANDING_PAGE_SUBHEADING)
        put_markdown(LANDING_PAGE_DESCRIPTION, lstrip=True)
    # run_js(HEADER)
    # run_js(FOOTER)
    
    url = input("input your target domain",datalist=popular_shopify_stores)    
    print('check url',url)
    # if not isvaliddomain(url):
    #     return {"urls": 'not a valid domain'}
    if url.startswith("http://"):
        pass
    elif url.startswith("https://"):
        pass
    else:
        url='https://'+url
    # url =trueurl(url)
    # put_text('bot is busy crawling now',url)
    put_loading(shape='border', color='success').style('width:4rem; height:4rem')
    clear('introduction')


    put_html('</br>')
    set_env(auto_scroll_bottom=True)
    with use_scope('log'):

        with battery.redirect_stdout():

            urls= crawler(url,1)
    data=[]
    for i in len(urls):
        item =[].append(i,urls[i],url)
        data.append(item)
    # put_logbox('log',200)

        # logbox_append('log',)
    clear('log')
    # qufen html   image  video 
    put_file(urlparse(url).netloc+'.txt', data, 'download me')
    put_collapse('preview urls',put_table(data, header=['id', 'url', 'domain']))


home = asgi_app(index)

app.mount("/", home)
app.mount("/api", apiapp)


if __name__ == '__main__':
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    if (os.environ.get('PORT')):
        port = int(os.environ.get('PORT'))
    else:
        port = 5001
    
    uvicorn.run(app='main:app',
                host="0.0.0.0",
                port=port,
                reload=False,
                debug=True,
                proxy_headers=True,
                log_config=log_config)