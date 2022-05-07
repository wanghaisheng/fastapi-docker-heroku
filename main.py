# -*- coding: utf-8 -*-

from fastapi import FastAPI
import requests
from ESD import EnumSubDomain
import validators
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

from pywebio.platform.fastapi import webio_routes,asgi_app

import time
import pywebio_battery as battery
from app.constants import *
from app.privacy import privacy
from app.terms import terms
from app.t import *
from app.feedback import *
import advertools as adv
from urllib.parse import urlparse, unquote_plus, urlunparse

from usp.objects.page import (
    SitemapPage,
    SitemapNewsStory,
    SitemapPageChangeFrequency,
)
from usp.objects.sitemap import (
    IndexRobotsTxtSitemap,
    PagesXMLSitemap,
    IndexXMLSitemap,
    InvalidSitemap,
    PagesTextSitemap,
    IndexWebsiteSitemap,
    PagesRSSSitemap,
    PagesAtomSitemap,
)
from usp.tree import sitemap_tree_for_homepage

app = FastAPI()

def strip_url_to_homepage(url: str) -> str:
    """
    Strip URL to its homepage.
    :param url: URL to strip, e.g. "http://www.example.com/page.html".
    :return: Stripped homepage URL, e.g. "http://www.example.com/"
    """
    # if not url:
    #     raise StripURLToHomepageException("URL is empty.")
    domain=''
    try:
        uri = urlparse(url)
        assert uri.scheme, "Scheme must be set."
        assert uri.scheme.lower() in ['http', 'https'], "Scheme must be http:// or https://"
        uri = (
            uri.scheme,
            uri.netloc,
            '/',  # path
            '',  # params
            '',  # query
            '',  # fragment
        )
        domain = urlunparse(uri)
    except Exception as ex:
        print("Unable to parse URL {}: {}".format(url, ex))

    return domain





def trueurl(url):

    r = requests.head(url, allow_redirects=True)
    return r.url


def formatdomain(url):

    if url.startswith("http://"):
        domain = urlparse(url).netloc
    elif url.startswith("https://"):
        domain = urlparse(url).netloc

    else:
        domain = url.split('/')[0]
    print('domain is ', domain)
    if not 'www' in domain:
        domain = 'www.'+domain
    return domain


@app.get("/sitemapurl/", response_class=ORJSONResponse)
def sitemap1(url: str):
    # print('check url', url)
    domain = formatdomain(url)
    results = []

    try:
        filename = urlparse(url).netloc
        index = []
        if not os.path.exists(filename+'-adv-sitemap.jl'):

            index = adv.sitemap_to_df(
                'https://'+domain+'/robots.txt', recursive=False)['loc'].tolist()
            index.to_json(filename+'-adv-sitemap.jl')

        else:
            index = pd.read_json(filename+'-adv-sitemap.jl')
        urls = []
        for url in index:
            # data = supabase.table("shop_sitemaps").insert({"name":"Germany"}).execute()

            locs = adv.sitemap_to_df(url)['loc'].tolist()
            urllocs = {"sitemap": url,
                       "loc": locs}
            urls.append(urllocs)
        sitemapindex = {'domain': domain,
                        "sitemapurl": url,
                        "urls": locs
                        }
        results.append(sitemapindex)
    except:
        print('no robots.txt')

    return {"results": results}


@app.get("/laststraw/", response_class=ORJSONResponse)
async def laststraw(url: str):
    print('check url', url)

    url = trueurl(url)

    urls = crawler(url, 1)

    print(urls)

    # return {"urls": urls}
    return {"urls": urls}


@app.get("/esd/", response_class=ORJSONResponse)
async def esd(url: str):


    domains = EnumSubDomain(url).run()
    return {"domains": list(set(domains))}

@app.get("/subdomain/", response_class=ORJSONResponse)
async def subdomain(url: str):
    print('check url', url)
    # if not isvaliddomain(url):
    #     return {"urls": 'not a valid domain'}

    url = trueurl(url)

    urls = crawler(url, 1)
    domains = []
    for url in urls:
        filename = urlparse(url).netloc
        if 'www' in filename:
            filename = filename.replace('www.', '')
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


def does_url_exist(url):
    try: 
        r = requests.head(url)
        if r.status_code < 400:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        print(e)
        # handle your exception


@config(theme="minty", title=SEO_TITLE, description=SEO_DESCRIPTION)
def index() -> None:
    # Page heading
    put_html(LANDING_PAGE_HEADING)
    lang = 'English'
    if lang == 'English':
        LANDING_PAGE_DESCRIPTION = LANDING_PAGE_DESCRIPTION_English
    run_js(
        'WebIO._state.CurrentSession.on_session_close(()=>{setTimeout(()=>location.reload(), 40000})')
    run_js(FOOTER)
    with use_scope('introduction'):
        # put_html(PRODUCT_HUNT_FEATURED_BANNER)
        # put_html(LANDING_PAGE_SUBHEADING)
        put_markdown(LANDING_PAGE_DESCRIPTION, lstrip=True)
    # run_js(HEADER)
    # run_js(FOOTER)

    inputdata = input_group("usp is  fast for most, adv sitemap is plan B,insane crawl is your last straw for those dont have /robots.txt file ", [
        input("input your target domain",
              datalist=popular_shopify_stores, name='url'),
        radio("with or without sitemap?", [
              'usp','subdomain','adv sitemap', 'insanecrawl'], inline=True, value='usp',name='q1')

    ], validate=check_form)

    url = inputdata['url']
    print('raw url', url)
        

    q1 = inputdata['q1']
    # if not isvaliddomain(url):
    #     return {"urls": 'not a valid domain'}
    if url.startswith("http://"):
        pass
    elif url.startswith("https://"):
        pass
    else:
        url = 'https://'+url
    print('format url', url)
    

    clear('introduction')

    if not validators.url(url):

        put_text('pls give us a valid url')
        put_button("Try again", onclick=lambda: run_js(
                        return_home), color='success', outline=True)        
    else:

        url =strip_url_to_homepage(url)
        print('domain in  url', url)

        print('root domain in  url', url)        
        url =trueurl(url)
        with use_scope('loading'):

            put_loading(shape='border', color='success').style(
                'width:4rem; height:4rem')
            put_text('ShopConan is working on it')


            put_html('</br>')
            set_env(auto_scroll_bottom=True)
            urls = []
            # with use_scope('log'):

            #     with battery.redirect_stdout():

            #         urls = crawler(url, 1)
            data = []
            data_product = []
            data_collection = []
            data_pages = []
            data_blog = []
            backend='sqlite'
            domain_in_url = formatdomain(url)
            if backend=='supabase':
                from app.supabase.dbmanipulation import Query_urls_list_In_Db,Update_urls_list_In_Db
            elif backend=='sqlite':
                from app.sqlite.dbmanipulation import Query_urls_list_In_Db,Update_urls_list_In_Db
            urls=Query_urls_list_In_Db(domain_in_url)

            print('=====',len(urls))
            if len(urls)==0:


                if q1 == 'subdomain':
                    start = time.time()

                    with use_scope('log'):

                        with battery.redirect_stdout():


                            put_text(
                                'first crawl for this domain ,it will takes some time')
                            domains = EnumSubDomain(url).run()


                            urls = list(set(domains))
                            print('url=====',urls)
                            supabaseupdate('shop', {'subdomains': urls}, domain)
                    clear('log')

                    if len(urls) < 1:
                        put_text('there is no subdomain found in this domain', url)
                        put_button("Try again", onclick=lambda: run_js(
                            return_home), color='success', outline=True)
                    else:
                        for idx, item in enumerate(urls):
                            t = []
                            t.append(str(idx))
                            t.append(item)
                            t.append(url)
                            data.append(t)
                    end = time.time()
                    put_text('Parsing is complete! time consuming: %.4fs' %
                                (end - start))                
                elif q1=='insanecrawl':
                    start = time.time()
                    domain = trueurl(domain)

                    urls = crawler(domain, 1)
                    end = time.time()
                    put_text('Parsing is complete! time consuming: %.4fs' %
                                (end - start))

                elif q1=='usp':
                    print('==============usp is started==============')

                    start = time.time()

                    tree = sitemap_tree_for_homepage(url)
                    # SitemapPage(url=https://www.indiehackers.com/forum/the-business-of-podcasting-with-jeff-meyerson-of-software-engineering-daily-e2b157d5de, priority=0.2, last_modified=2019-09-04 18:27:13+00:00, change_frequency=SitemapPageChangeFrequency.MONTHLY, news_story=None)

                    urls=[x.url for x in tree.all_pages()]
                    end = time.time()
                    put_text('Parsing is complete! time consuming: %.4fs' %
                                (end - start))
                    print('==============usp is done==============')
                elif q1=='sitemapdetect':
                    start = time.time()


                    tree = sitemap_tree_for_homepage(url)
                    # SitemapPage(url=https://www.indiehackers.com/forum/the-business-of-podcasting-with-jeff-meyerson-of-software-engineering-daily-e2b157d5de, priority=0.2, last_modified=2019-09-04 18:27:13+00:00, change_frequency=SitemapPageChangeFrequency.MONTHLY, news_story=None)
                    if InvalidSitemap in tree.sub_sitemaps:
                        print('you need last straw')
                        urls = crawler(url, 1)

                    else:
                        robot=tree.sub_sitemaps[0].url
                        indexxmlsimap=[ x.url for x in tree.sub_sitemaps[0].sub_sitemaps]
                        urls=[ x.url for x in tree.all_pages]

                    #  IndexWebsiteSitemap(url=http://www.cettire.com/, sub_sitemaps=[InvalidSitemap(url=http://www.cettire.com/robots.txt, reason=No parsers support sitemap from http://www.cettire.com/robots.txt)])
                    # 根据这个结果 我们可以对url进行分类 这种情况只能暴力crawl
                    end = time.time()
                    put_text('Parsing is complete! time consuming: %.4fs' %
                                (end - start))        
                else:
                    start = time.time()

                    urls = []
                    urllocs=[]
                # print('existing db',len(supabase_db.table("tiktoka_douyin_users").select('uid').execute()[0]),data,data[0])

                    print('this domain data dont exist', domain, data.data)

                    with use_scope('log'):

                        with battery.redirect_stdout():
                            url=''
                            if does_url_exist('https://'+domain+'/robots.txt'):
                                url='https://'+domain+'/robots.txt'
                            elif does_url_exist('https://'+domain+'/sitemap.xml'):
                                # print('--',index)
                                url='https://'+domain+'/sitemap.xml'
                            else:
                                print('there is no sitemap for this domain')
                            if not url=='':
                                index = adv.sitemap_to_df(
                                    url, recursive=False)
                                index=index['loc'].tolist()
                                # index.to_json(filename+'-adv-sitemap.jl')
                                sitemapurls = []
                                if len(index) == 0:
                                    print('there is no url found ')
                                else:
                                    for url in index:
                                        # data = supabase.table("shop_sitemaps").insert({"name":"Germany"}).execute()

                                        locs = adv.sitemap_to_df(url)['loc'].tolist()
                                        urlloc = {"sitemap": url,
                                                "loc": locs}
                                        urllocs.append(urlloc)


                                supabaseop(
                                    'shop', {"domain": domain, 'subdomains': urllocs, "sitemapurls": sitemapurls})

                        clear('log')

                        # urls = list(urls)
                        # print(urls)
                        if len(urllocs) < 1:
                            put_text('there is no url found in this domain', urllocs)
                            put_text('report us through email: shopconanofficial@gmail.com')

                            put_button("Try another", onclick=lambda: run_js(
                                return_home), color='success', outline=True)
                        else:

                            urlloc = urllocs[0]['urls']
                            # locs = []
                            for idx, item in enumerate(urlloc):
                                urls.extend(item['loc'])
                    end = time.time()
                    put_text('Parsing is complete! time consuming: %.4fs' %
                                (end - start))
                Update_urls_list_In_Db(urls,url)
            put_text('Preparing downloading files')
            print('length',len(urls))
            preview=urls

            if len(urls)>500:
                preview=urls[:499]
            for idx, item in enumerate(preview):
                t = []
                t.append(str(idx))
                t.append(item)
                t.append(url)
                # print('======',t)
                if 'collection' in item:
                    # print('collection')
                    data_collection.append(t)
                elif 'blog' in item:
                    # print('blog')

                    data_blog.append(t)
                elif 'product' in item:
                    # print('product')

                    data_product.append(t)
                elif 'pages' in item:
                    data_pages.append(t)
                data.append(t)
            clear('loading')

            # put_logbox('log',200)
            if len(urls) > 0:
                encoded = ''
                for i in urls:
                    print(i,type(i))
                    # encoded = encoded+','.join(list(i))
                    encoded+=i
                    encoded = encoded+'\n'
                array=encoded.encode('utf-8')
                clear('log')

                put_collapse('total results: '+str(len(urls))+', only can preview first 500', put_table(
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
                        scroll_to('ROOT', position='top')), color='success', outline=True),
                    put_file(urlparse(url).netloc+'.txt',
                            array, 'download all')
                ])

            else:

                put_row([
                    put_button("Try another option", onclick=lambda: run_js(
                        return_home), color='success', outline=True),
                    put_button("Back to Top", onclick=lambda: run_js(
                        scroll_to('ROOT', position='top')), color='success', outline=True)

                ])
# home = asgi_app(index)
# app.mount("/", home)
app.mount("/", FastAPI(routes=webio_routes(index)))
# app.mount("/t/", asgi_app(t))

# app.mount("/feedback/", FastAPI(routes=webio_routes(feedback)))
# app.mount("/privacy/", FastAPI(routes=webio_routes(privacy)))
# # app.mount("/terms", FastAPI(routes=webio_routes(terms)))
# termsapp = asgi_app(terms)
# app.mount("/terms/", termsapp)

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
