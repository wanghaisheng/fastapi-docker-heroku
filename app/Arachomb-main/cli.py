from typing import Set
import sys
import json
import sqlite3
import logging
import argparse
import googlesearch as google
import os


DATABASE_NAME = "data.db"

logging.basicConfig(level=logging.WARN, format="%(levelname)-8s %(message)s", handlers=[
    logging.FileHandler("output.log")])


def google_domain_search(domain: str) -> Set[str]:
    result = set((get_base_url(i) for i in google.search(
        f"site:{domain}", tld="no", lang="no", pause=3, stop=100) if domain in i))
    return result


def get_base_url(url: str) -> str:
    return "/".join(url.split("/")[:3])


def suggestion(code):
    if code == "404":
        return "make sure the URL is spelled correctly, and that the resource exists."
    elif code == "403":
        return "make sure the resource is publically available.  If this is intentional, ignore this error."
    elif code == "405":
        return "double check that the URL is spelled correctly, as the page only allows certain non-GET requests, so it won't appear properly in a browser."
    elif code == "557":
        return "give the website an up-to-date SSL certificate, since it currently does not have one."
    elif code == "5":
        return "make sure you are using an up to date version of python. you are likely using python3.8 with a minor version 2 or lower while on windows, this has some bugs in async code that are fixed in the later releases"
    return "figure out what kind of error this is, because we do not know."


def error_output(error, source, target, timestamp):
    if error == "557":
        error = "fault with the site's SSL certificate"
    elif error == "5":
        error = "fault relating to your computer's OS"
    else:
        #error += " error"
        pass
    return f"""*****************\nWe found an error in {source}, in the link to
        {target}\n\n
        Getting the link returned a {error}. Try to {suggestion(error)}\n\n
        Last checked at {timestamp}"""


def init(args):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS errors 
                (source TEXT NOT NULL, 
                subdomain TEXT NOT NULL,
                target TEXT NOT NULL,
                error TEXT,
                updated_at TEXT,
                CONSTRAINT prim_key PRIMARY KEY (source, target) ON CONFLICT REPLACE
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS subdomains (
                domain TEXT NOT NULL, 
                should_search BOOLEAN NOT NULL CHECK (should_search IN (0,1)),
                PRIMARY KEY (domain) ON CONFLICT IGNORE
                ) """)
    con.commit()


def find(args):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    print(f"expanding {args.name}")
    domains = google_domain_search(args.name)
    subdomains = [domain.split('/')[2] for domain in domains]
    print("about to put them in the database",subdomains)
    cur.executemany("INSERT INTO subdomains VALUES (?,?)",
                    [(i, 1) for i in subdomains])
    con.commit()
    print("Should have inserted the subdomains now, boss!")


def reset(args):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    cur.execute("""DROP TABLE IF EXISTS subdomains""")
    cur.execute("""DROP TABLE IF EXISTS errors""")
    cur.execute("""CREATE TABLE IF NOT EXISTS errors 
                (source TEXT NOT NULL, 
                subdomain TEXT NOT NULL,
                target TEXT NOT NULL,
                error TEXT,
                updated_at TEXT,
                CONSTRAINT prim_key PRIMARY KEY (source, target) ON CONFLICT REPLACE
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS subdomains (
                domain TEXT NOT NULL, 
                should_search BOOLEAN NOT NULL CHECK (should_search IN (0,1)),
                PRIMARY KEY (domain) ON CONFLICT IGNORE
                ) """)
    con.commit()


def add_subdomain(args):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    print("adding subdomain now")
    cur.executemany("""INSERT INTO subdomains VALUES (?, 1)""", (args.name,))
    con.commit()


def remove_subdomain(args):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    print("removing subdomain now")
    cur.executemany("""DELETE FROM subdomains WHERE domain=?""", (args.name,))
    con.commit()


def enable_subdomain(args):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    print("Enabling")
    if "all" in args.name:
        cur.execute("UPDATE subdomains SET should_search = 1")
    else:

        cur.executemany(
            """UPDATE subdomains SET should_search = 1 WHERE domain = ?;""",
            (args.name,))
    con.commit()


def disable_subdomain(args):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    print("Disabling")
    if "all" in args.name:
        cur.execute("UPDATE subdomains SET should_search = 0")
    else:
        cur.executemany(
            """UPDATE subdomains SET should_search = 0 WHERE domain = ?;""", (args.name,))
    con.commit()


def display_info(args):
    with sqlite3.connect(DATABASE_NAME) as con:
      cur = con.cursor()
      code, subdomain = args.code, args.subdomain
      if args.code and args.subdomain:
          for error, source, target, timestamp in cur.execute("""SELECT error, source, target, updated_at FROM errors WHERE error=? AND subdomain LIKE ? ORDER BY subdomain""",(args.code,"%"+args.subdomain+"%",)).fetchall():
              output = error_output(error, source, target, timestamp)
              print(output)
              logging.error(output)

      elif args.code:
          for error, source, target, timestamp in cur.execute("SELECT error, source, target, updated_at FROM errors WHERE error=? ORDER BY subdomain",(args.code,)).fetchall():
              output = error_output(error, source, target, timestamp)
              print(output)
              logging.error(output)

      elif args.subdomain:
          for error, source, target, timestamp in cur.execute("""SELECT error, source, target, updated_at FROM errors WHERE subdomain LIKE ? ORDER BY subdomain""",("%"+args.subdomain+"%",)).fetchall():
              output = error_output(error, source, target, timestamp)
              print(output)
              logging.error(output)

      else:
          for error, source, target, timestamp in cur.execute("SELECT error, source, target, updated_at FROM errors ORDER BY subdomain").fetchall():
              output = error_output(error, source, target, timestamp)
              print(output)
              logging.error(output)


def subdomains(args):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    for name, search in cur.execute("SELECT * FROM subdomains").fetchall():
        print(f"{name}: " + ("ACTIVE" if str(search) == "1" else "DISABLED"))


parser = argparse.ArgumentParser(description="The Arachomb link checker")
subparsers = parser.add_subparsers()

subcommand_add = subparsers.add_parser('add')
subcommand_add.add_argument('name', nargs="+", type=str)
subcommand_add.set_defaults(func=add_subdomain)

subcommand_remove = subparsers.add_parser('remove')
subcommand_remove.add_argument('name', nargs="+", type=str)
subcommand_remove.set_defaults(func=remove_subdomain)

subcommand_enable = subparsers.add_parser('enable')
subcommand_enable.add_argument('name', nargs="+", type=str)
subcommand_enable.set_defaults(func=enable_subdomain)

subcommand_disable = subparsers.add_parser('disable')
subcommand_disable.add_argument('name', nargs="+", type=str)
subcommand_disable.set_defaults(func=disable_subdomain)

subcommand_init = subparsers.add_parser('init')
subcommand_init.set_defaults(func=init)

subcommand_find = subparsers.add_parser('find')
subcommand_find.add_argument('name', nargs="?", default="uia.no", type=str)
subcommand_find.set_defaults(func=find)

subcommand_reset = subparsers.add_parser('reset')
subcommand_reset.set_defaults(func=reset)

subcommand_subdomains = subparsers.add_parser('subdomains')
subcommand_subdomains.set_defaults(func=subdomains)

subcommand_print_errors = subparsers.add_parser("print_errors")
subcommand_print_errors.add_argument("-c","--code", nargs="?", type=int,help="filter errors by the given error code")
subcommand_print_errors.add_argument("-s","--subdomain", nargs="?", type=str,help="filter errors by the given subdomain")
subcommand_print_errors.set_defaults(func=display_info)


args = parser.parse_args()
if args.func:
    args.func(args)
    # something else?
# else?  There was another branch to this, but I forget what he did here
