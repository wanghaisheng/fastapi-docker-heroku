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


SEO_TITLE = "ShopConna™ shopify store link detect "
SEO_DESCRIPTION = "shopify store watch toolkit"

LANDING_PAGE_HEADING = r"""
<h1 align="center"><strong>ShopConna™ shopify store link detect </strong></h1>
"""

PRODUCT_HUNT_FEATURED_BANNER = r"""
<div align="center"><a href="https://www.producthunt.com/posts/burplist?utm_source=badge-featured&utm_medium=badge&utm_souce=badge-burplist" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=304966&theme=light" alt="Burplist - Free price comparison tool for craft beers | Product Hunt" style="width: 250px; height: 54px;" width="250" height="54" /></a></div>
"""

LANDING_PAGE_SUBHEADING = r"""
<h3 align="center">ShopConna™ shopify store watch toolkit</h1>
<p align="center">
    <img alt="Cheers" class="img" width="50%" height="50%" src="https://media.giphy.com/media/DGWAx8d3IkICs/giphy.gif">
</p>
"""

LANDING_PAGE_DESCRIPTION_English = r"""
# What is ShopConna™?
As part of shopify store watch toolkit,This  shopify store link detect project aims to detect all links in a shopify store and then monitor them daily,if there is any changes we can notify through wechat .

🔎 A free **brand watch tool** for influencers.
📊 **Handsoff** to mannually looking for potential shopify trending product 
❤️ Saving  **10X** time than manually monitor bunch of stores.
💯 wechat is all your need,no PC no Proxy at all.
    image and pdf report send to your wechat account


## How to use?

📚  input shopify store url 
📚  save links as you wish

## Is this free?

🥳 Short answer: Yes.
🙌 Long answer: _Yessssssssssss_.
"""
@seo(SEO_TITLE, SEO_DESCRIPTION)
@config(theme="minty")
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
    url = input("input your target domain")    
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
    # put_text('bot is busy crawling now')
    put_loading(shape='border', color='success').style('width:4rem; height:4rem')
    clear('introduction')
    urls= crawler(url,'report.txt',1)
    data=[]
    for i in len(urls):
        item =[].append(i,urls[i],url)
        data.append(item)
    # put_logbox('log',200)
    # with battery.redirect_stdout():

        # logbox_append('log',)
    put_table(data, header=['id', 'url', 'domain'])



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