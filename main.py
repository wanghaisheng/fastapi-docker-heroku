from fastapi import FastAPI
import requests
import pandas as pd

from app.fws import *
from fastapi.responses import ORJSONResponse
import uvicorn
from pywebio.input import *
from pywebio.io_ctrl import Output, OutputList
from pywebio.output import *
from pywebio.platform import seo
from pywebio.platform.page import config
from pywebio.session import run_js, set_env
from pywebio import config, session

from pywebio.platform.fastapi import asgi_app
import time
import pywebio_battery as battery
from app.constants import *
import advertools as adv

app = FastAPI()


def trueurl(url):

    r = requests.head(url, allow_redirects=True)
    return r.url


@app.get("/sitemapurl/", response_class=ORJSONResponse)
def sitemap1(url: str):
    # print('check url', url)
    domain = ''
    results = []

    if url.startswith("http://"):
        domain = urlparse(url).netloc
    elif url.startswith("https://"):
        domain = urlparse(url).netloc

    else:
        domain = url.split('/')[0]
    print('domain is ', domain)
    if not 'www' in domain:
        domain = 'www.'+domain
    try:
        filename =urlparse(url).netloc
        index=[]
        if not os.path.exists(filename+'-adv-sitemap.jl'):

            index = adv.sitemap_to_df(
                'https://'+domain+'/robots.txt', recursive=False)['loc'].tolist()
            index.to_json(filename+'-adv-sitemap.jl')
        else:
            index=pd.read_json(filename+'-adv-sitemap.jl')
        urls = []
        for url in index:
            locs = adv.sitemap_to_df(url)['loc'].tolist()
            urllocs = {"sitemap": url,
                       "loc": locs}
            urls.append(urllocs)
        sitemapindex = {'domain': domain,
                        "sitemapurl": index,
                        "urls": urls
                        }
        results.append(sitemapindex)
    except:
        print('no robots.txt')

    return {"results": results}


@app.get("/crawlurl/", response_class=ORJSONResponse)
async def sitemap(url: str):
    print('check url', url)
    # if not isvaliddomain(url):
    #     return {"urls": 'not a valid domain'}
    if url.startswith("http://"):
        pass
    elif url.startswith("https://"):
        pass
    else:
        url = 'https://'+url
    url = trueurl(url)

    urls = crawler(url, 1)

    print(urls)

    # return {"urls": urls}
    return {"urls": urls}



@app.get("/subdomain/", response_class=ORJSONResponse)
async def subdomain(url: str):
    print('check url', url)
    # if not isvaliddomain(url):
    #     return {"urls": 'not a valid domain'}
    if url.startswith("http://"):
        pass
    elif url.startswith("https://"):
        pass
    else:
        url = 'https://'+url
    url = trueurl(url)

    urls = crawler(url, 1)
    domains=[]
    for url in urls:
        filename =urlparse(url).netloc
        if 'www' in filename:
            filename=filename.replace('www.','')
        domains.append(url)
    print(urls)
    return {"domains": list(set(domains))}





return_home = """
location.href='/'
"""
def check_form(data):
    # if len(data['name']) > 6:
    #     return ('name', 'Name to long!')
    # if data['age'] <= 0:
    #     return ('age', 'Age cannot be negative!')
    pass


@config(theme="minty", title=SEO_TITLE, description=SEO_DESCRIPTION)
def index() -> None:
    # Page heading
    put_html(LANDING_PAGE_HEADING)
    lang = 'English'
    if lang == 'English':
        LANDING_PAGE_DESCRIPTION = LANDING_PAGE_DESCRIPTION_English
    session.run_js('WebIO._state.CurrentSession.on_session_close(()=>{setTimeout(()=>location.reload(), 40000})')    

    with use_scope('introduction'):
        # put_html(PRODUCT_HUNT_FEATURED_BANNER)
        # put_html(LANDING_PAGE_SUBHEADING)
        put_markdown(LANDING_PAGE_DESCRIPTION, lstrip=True)
    # run_js(HEADER)
    # run_js(FOOTER)

    data = input_group("sitemap is fast for most,insane crawl is your last straw for those dont have /robots.txt file ",[
        input("input your target domain", datalist=popular_shopify_stores,name='url'),
        radio("with or without sitemap?", ['sitemap', 'crawl','subdomain'],inline=True,name='q1')

    ], validate=check_form)

    url = data['url']
    print('check url', url)

    q1 = data['q1']
    # if not isvaliddomain(url):
    #     return {"urls": 'not a valid domain'}
    if url.startswith("http://"):
        pass
    elif url.startswith("https://"):
        pass
    else:
        url = 'https://'+url
    # url =trueurl(url)

    with use_scope('loading'):

        put_loading(shape='border', color='success').style(
            'width:4rem; height:4rem')
    clear('introduction')

    put_html('</br>')
    set_env(auto_scroll_bottom=True)
    urls = []
    # with use_scope('log'):

    #     with battery.redirect_stdout():

    #         urls = crawler(url, 1)
    data = []
    data_product=[]
    data_collection=[]
    data_pages=[]
    data_blog=[]
    if q1=='subdomain':
        urls=[]
        with use_scope('log'):

            with battery.redirect_stdout():
                filename =urlparse(url).netloc
                if not os.path.exists(filename+'-adv.jl'):
                    put_text('first crawl for this domain ,it will takes some time')

                    adv.crawl(url, filename+'-adv.jl', follow_links=True,exclude_url_params=True)

                crawl_df = pd.read_json(filename+'-adv.jl', lines=True)

                urls = crawl_df['url'].tolist()
        clear('log')

        domains=[]
        for url in urls:
            filename =urlparse(url).netloc
            if 'www' in filename:
                filename=filename.replace('www.','')
            domains.append(url)

        urls = list(set(domains))
        if len(urls) < 1:
            put_text('there is no subdomain found in this domain', url)
            put_button("Try again", onclick=lambda: run_js(
                return_home), color='success', outline=True)
        else:
            for idx, item in enumerate(urls):
                t=[]
                t.append(idx)
                t.append(item)
                t.append(url)
                data.append(t)   
                if 'collection' in item:
                    print('collection')
                    data_collection.append(t)
                elif 'blog' in item:
                    print('blog')

                    data_blog.append(t)
                elif 'product' in item:
                    print('product')

                    data_product.append(t)
                elif 'pages' in item:
                    data_pages.append(t)                 
    elif q1 == 'sitemap':
        urls=[]
        filename =urlparse(url).netloc
        if  os.path.exists(filename+'-adv.jl'):

            crawl_df = pd.read_json(filename+'-adv.jl', lines=True)

            urls = crawl_df['url'].tolist()

            urls = list(urls)
            if len(urls) < 1:
                put_text('there is no url found in this domain', url)
                put_button("Try again", onclick=lambda: run_js(
                    return_home), color='success', outline=True)
            else:
                for idx, item in enumerate(urls):
                    t=[]
                    t.append(idx)
                    t.append(item)
                    t.append(url)
                    data.append(t)
                    if 'collection' in item:
                        print('collection')
                        data_collection.append(t)
                    elif 'blog' in item:
                        print('blog')

                        data_blog.append(t)
                    elif 'product' in item:
                        print('product')

                        data_product.append(t)
                    elif 'pages' in item:
                        data_pages.append(t)
        else:

            with use_scope('log'):

                with battery.redirect_stdout():


                    urls = sitemap1(url)['results']
            clear('log')

            # urls = list(urls)
            # print(urls)
            if len(urls) < 1:
                put_text('there is no url found in this domain', url)
                put_button("Try again", onclick=lambda: run_js(
                    return_home), color='success', outline=True)
            else:
                urls = urls[0]['urls']
                locs = []
                for idx, item in enumerate(urls):
                    locs.extend(item['loc'])
                for idx, item in enumerate(locs):
                    t=[]
                    t.append(idx)
                    t.append(item)
                    t.append(url)
                    # print('======',t)
                    if 'collection' in item:
                        print('collection')
                        data_collection.append(t)
                    elif 'blog' in item:
                        print('blog')

                        data_blog.append(t)
                    elif 'product' in item:
                        print('product')

                        data_product.append(t)
                    elif 'pages' in item:
                        data_pages.append(t)
                    data.append(t)
    else:
        urls=[]
        with use_scope('log'):
                # urls = crawler(url, 1)
            with battery.redirect_stdout():
                filename =urlparse(url).netloc
                if not os.path.exists(filename+'-adv.jl'):
                    put_text('first crawl for this domain ,it will takes some time')
                adv.crawl(url, filename+'-adv.jl', follow_links=True,exclude_url_params=True,custom_settings={'CLOSESPIDER_PAGECOUNT': 10000})
                crawl_df = pd.read_json(filename+'-adv.jl', lines=True)

                urls = crawl_df['url'].tolist()

        clear('log')

        urls = list(urls)
        if len(urls) < 1:
            put_text('there is no url found in this domain', url)
            put_button("Try again", onclick=lambda: run_js(
                return_home), color='success', outline=True)
        else:
            for idx, item in enumerate(urls):
                t=[]
                t.append(idx)
                t.append(item)
                t.append(url)
                data.append(t)
                print(item)
                if 'collection' in item:
                    print('collection')
                    data_collection.append(t)
                elif 'blog' in item:
                    print('blog')

                    data_blog.append(t)
                elif 'product' in item:
                    print('product')

                    data_product.append(t)
                elif 'pages' in item:
                    data_pages.append(t)
    # print(data, '====')


    # put_logbox('log',200)
    if len(data) > 0:
        encoded=''
        for i in data:
            encoded=encoded+','.join(str(i))
            encoded=encoded+'\n'
        # array=bytearray(encoded.encode('utf-8'))
        clear('loading')
        clear('log')
        
        put_collapse('preview all, display  500 max', put_table(
            data[:500], header=['id', 'url', 'domain']))
        put_collapse('preview collection', put_table(
            data_collection, header=['id', 'url', 'domain']))
        put_collapse('preview product', put_table(
            data_product, header=['id', 'url', 'domain']))
        put_collapse('preview pages', put_table(
            data_pages, header=['id', 'url', 'domain']))
        put_collapse('preview blog', put_table(
            data_blog, header=['id', 'url', 'domain']))            
        put_row([
        put_button("Try again", onclick=lambda: run_js(
            return_home), color='success', outline=True),
        put_button("Back to Top", onclick=lambda: run_js(
            scroll_to('ROOT', position='top') ), color='success', outline=True),
        put_file(urlparse(url).netloc+'.txt', bytes(encoded, 'utf-8'), 'download all')             
             ])                   



home = asgi_app(index)

app.mount("/", home)


# api.mount('/static', StaticFiles(directory='static'), name='static')
# api.include_router(home.router)
# api.include_router(weather_api.router)


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
