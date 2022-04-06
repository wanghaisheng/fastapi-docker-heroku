import httpx
import bs4 as soup
import googlesearch as google
from typing import Set
import sys
import json
import logging
import aiosqlite
import datetime
import asyncio


with open("deadlinks.csv", "w") as f:
    f.write("")

logging.basicConfig(level=logging.WARN, format="%(levelname)-8s %(message)s", handlers=[
    logging.StreamHandler(sys.stdout),
    logging.FileHandler("deadlinks.csv")])


def get_base_url(url: str) -> str:
    return "/".join(url.split("/")[:3])


async def google_domain_search(domain: str) -> Set[str]:
    print(f"Expanding {domain}")
    result = set((get_base_url(i) for i in google.search(
        f"site:{domain}", tld="no", lang="no", pause=5) if domain in i))
    return result


def handle_url(url: str, current):
    https = 's' if "https" in str(current.url) else ''

    if url.startswith("http"):
        if https:
            return (url, url.replace("s", '', 1))
        else:
            return (url[:4] + 's' + url[4:], url)

    elif url.startswith("#"):
        output = (str(current.url) + url,
                  str(current.url).replace('s', '', 1) + url)
        if str(current.url)[4].lower() == 's':
            return output
        else:
            return (output[1], output[0])

    elif url.startswith("//"):
        return ("https:" + url, "http:" + url)
    elif url.startswith("/"):
        return ("https://" + current.url.host + url, "http://" + current.url.host + url)
    else:
        return ("https://" + current.url.host + "/" + url, "http://" + current.url.host + "/" + url)


async def search_domain(domain: str, visited: Set[str], database_queue) -> None:
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get("https://" + domain)
        except httpx.ConnectError as e:
            print(f"Got an ssl error in {domain}")
            return
        except Exception:
            try:
                resp = await client.get("http://" + domain)
            except httpx.ConnectError as e:
                print(f"Got a connection error in {domain}")
                return
            else:
                await database_queue.put((str(resp.url), resp.url.host, str(resp.url), "557", str(datetime.datetime.today())))

        to_search = set([resp])
        while to_search:
            current = to_search.pop()

            if not current.url.host.endswith(domain):
                continue
            if str(current.url) in visited:
                continue
            visited.add(str(current.url))

            # Get all the URLs in the current page
            try:
                text = soup.BeautifulSoup(current.text, "html.parser")
            except:
                print(current)
                continue
            hrefs = {i.get("href") for i in text.find_all(
                href=True)}
            srcs = {i.get("src") for i in text.find_all(
                src=True)}

            # Loop over the URLs in the current page
            for url in hrefs | srcs:
                if any(url.startswith(i) for i in ["mailto:", "tel:", "javascript:", "#content-middle", "about:blank", "skype:"]):
                    continue
                if url == "#" or "linkedin" in url or "\\" in url:
                    continue

                try:  # getting the content of the URL we're checking currently
                    full_urls = handle_url(str(url), current)
                    #TODO: add the full url, so it actually skips already searched 
                    if full_urls[0] in visited or full_urls[1] in visited:
                        continue
                    resp = await client.get(full_urls[0])
                    await asyncio.sleep(0.5)

                    if resp.status_code == 403:
                        pass

                    if 200 <= resp.status_code < 300 or resp.status_code == 301 or resp.status_code == 302:
                        if ".js" not in full_urls[0] and resp.url.host.endswith(domain):
                            to_search.add(resp)

                        logging.debug(
                            f"{full_urls[0]},{url},{str(current.url)},{resp.status_code}")

                    else:  # Got an HTTP error
                        await database_queue.put((str(current.url), current.url.host, full_urls[0], str(resp.status_code), str(datetime.datetime.today())))
                        # await cur.execute("""INSERT INTO errors VALUES (?,?,?,?)""", (str(current.url), full_url, str(resp.status_code), str(datetime.date.today())))
                        # await cur.commit()
                        # await con.commit()
                        logging.error(
                            f"{full_urls[0]},{url},{str(current.url)},{resp.status_code}")

                except httpx.ConnectError as e:  # SSL errors and such?
                    if not e.args[0].startswith("[SSL: WRONG_VERSION_NUMBER]"):
                        continue

                    try:
                        resp_https = await client.get(full_urls[1])
                    except Exception as e:
                        print("130".e.args)
                    else:
                        if 200 <= resp_https.status_code < 300 or resp_https.status_code == 301 or resp_https.status_code == 302:
                            await database_queue.put((str(current.url), current.url.host, full_urls[1], "557", str(datetime.datetime.today())))
                            logging.error(
                                f"{full_urls[1]},{url},{str(current.url)},{e.args}")

                except httpx.ConnectTimeout as e:
                    # TODO: what do we do on a timeout
                    #print("139"," timeout ",e)
                    continue

                except httpx.TooManyRedirects as e:
                    # TODO: edit redirect maximum?
                    #print("144"," redirects ",e)
                    continue

                except OSError:
                    await database_queue.put((str(current.url), current.url.host, full_urls[1], "5", str(datetime.datetime.today())))

                except httpx.ConnectError as e:  # Semaphore error?
                    await database_queue.put((str(current.url), current.url.host, full_urls[0], "0", str(datetime.datetime.today())))
                    # await cur.execute("""INSERT INTO errors VALUES (?,?,?,?)""", (str(current.url), full_url, str(e.args), str(datetime.date.today())))
                    # await cur.commit()
                    # await con.commit()
                    logging.error(
                        f"{full_urls[0]},{url},{str(current.url)},{e.args}")
                except httpx.RemoteProtocolError:
                    print("protocol error")


async def database_worker(data_queue, insert_length) -> None:
    try:
        async with aiosqlite.connect(DATABASE_NAME) as con:
            cursor = await con.cursor()
            stored_data = []
            try:
                while True:
                    await asyncio.sleep(1)
                    # (source,target,code,timestamp) = await data_queue.get()
                    data = await data_queue.get()
                    stored_data.append(data)
                    if len(stored_data) >= insert_length:
                        await cursor.executemany(
                            "INSERT INTO errors VALUES (?,?,?,?,?)", stored_data)
                        stored_data = []
                        await con.commit()
                    data_queue.task_done()
            except asyncio.CancelledError:
                print("storing final data")
                if len(stored_data) != 0:
                    await cursor.executemany(
                        "INSERT INTO errors VALUES (?,?,?,?,?)", stored_data)
                    await con.commit()
                print("stored final data")
            finally:
                print("trying to close")
                print("closing")
                return
    except Exception as e:
        print("185",e.args)


DATABASE_NAME = "data.db"


async def main() -> None:
    visited = set()
    # domains = set(['https://www.uia.no', 'https://cair.uia.no', 'https://home.uia.no', 'https://kompetansetorget.uia.no', 'https://icnp.uia.no', 'http://friluft.uia.no', 'https://passord.uia.no', 'https://windplan.uia.no', 'https://appsanywhere.uia.no', 'https://shift.uia.no', 'https://insitu.uia.no', 'https://lyingpen.uia.no', 'https://platinum.uia.no', 'https://dekomp.uia.no', 'https://naturblogg.uia.no', 'https://enters.uia.no', 'https://wisenet.uia.no', 'https://libguides.uia.no', 'http://ciem.uia.no'])  
    con = await aiosqlite.connect(DATABASE_NAME)
    cur = await con.cursor()
    domains = set()
    try:
        rows = await cur.execute("SELECT domain FROM subdomains where should_search=1")
        for (i,) in await rows.fetchall():
            #print(i)
            domains.add(i)
    except Exception as e:
        print(e.args)
        with open("config.json") as file:
            data = json.loads(file.read())
        domains = set(filter(lambda x: data[x], data.keys()))
    await cur.close()
    if not domains:
        print("No domains to search")
        return
    # _ = await asyncio.wait([search_domain(domain, visited) for domain in domains],return_when=asyncio.ALL_COMPLETED)
    # worker_amount = 6
    # task_queue = asyncio.Queue()
    insert_length = 1
    database_queue = asyncio.Queue()
    # result_queue = asyncio.Queue()
    data_worker = asyncio.create_task(
        database_worker(database_queue, insert_length))
    workers = []

    #print(domains)
    for domain in domains:
        workers.append(asyncio.create_task(search_domain(
            domain, visited, database_queue), name=domain))
    # await asyncio.gather(*workers, return_exceptions=True)
    (done, running) = await asyncio.wait(workers, return_when=asyncio.FIRST_COMPLETED)
    #print(f"{done=}")
    #print(f"{running=}")
    while running:
        (done_new, running_new) = await asyncio.wait(workers, return_when=asyncio.FIRST_COMPLETED)
        if done_new != done:
            print(f"{len(done_new)}/{len(done_new)+len(running_new)} workers done")
        done, running = done_new, running_new
        await asyncio.sleep(1)
    await database_queue.join()
    data_worker.cancel()
    await data_worker
    for task in done:
        await task
    del done


if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.get_event_loop().run_until_complete(main())
