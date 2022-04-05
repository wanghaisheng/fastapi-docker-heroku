from fastapi import FastAPI
from webcrawler import WebCrawler
from sitemapgen import Generator          # Import the Generator class


app = FastAPI()


@app.get("/{url}")
async def root(url:str):
    # Create a generator instance where:

    generator = Generator(site=url,
                        output="sitemap.xml", disguise="http://www.example.com")
    # site = The site to generate a sitemap of. (required)
    # output = The path of the output file. (required) If the sitemap is not be written to a file, just set it to an empty string.
    # disguise = The url to disguise the sitemap for. (optional)

    # Discover all URLs possible from the "site" specified during initialization.
    urls = generator.discover()
    # This function returns the URLs discovered but it's return value can also be ignored if the urls don't matter
    # (If they are ultimately going to be written to a file)
    # Returns a list

    # Generate a String sitemap from the URLs discovered before. Should only be used after calling generator.discover()
    sitemap = generator.genSitemap()
    # This function returns the generated sitemap but it's return value can also be ignored if the sitemap is just to be written to a file.
    # Returns a String

    generator.write()      # Write to the output file specified. No return value

    return {"urls": urls}


@app.get("/sitemap/{url}")
async def crawl(url:str):

    web_crawler = WebCrawler(url)
    return {"urls":web_crawler.crawl_it()}