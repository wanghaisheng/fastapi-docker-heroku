import asyncio

import gspread_asyncio

# from google-auth package
from google.oauth2.service_account import Credentials 

# First, set up a callback function that fetches our credentials off the disk.
# gspread_asyncio needs this to re-authenticate when credentials expire.

def get_creds():
    # To obtain a service account JSON file, follow these steps:
    # https://gspread.readthedocs.io/en/latest/oauth2.html#for-bots-using-service-account
    creds = Credentials.from_service_account_file("serviceacct_spreadsheet.json")
    scoped = creds.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])
    return scoped

# Create an AsyncioGspreadClientManager object which
# will give us access to the Spreadsheet API.

agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)

# Here's an example of how you use the API:

async def example(agcm):
    # Always authorize first.
    # If you have a long-running program call authorize() repeatedly.
    agc = await agcm.authorize()

    ss = await agc.create("Test Spreadsheet")
    print("Spreadsheet URL: https://docs.google.com/spreadsheets/d/{0}".format(ss.id))
    print("Open the URL in your browser to see gspread_asyncio in action!")

    # Allow anyone with the URL to write to this spreadsheet.
    await agc.insert_permission(ss.id, None, perm_type="anyone", role="writer")

    # Create a new spreadsheet but also grab a reference to the default one.
    ws = await ss.add_worksheet("My Test Worksheet", 10, 5)
    zero_ws = await ss.get_worksheet(0)

    # Write some stuff to both spreadsheets.
    for row in range(1, 11):
        for col in range(1, 6):
            val = "{0}/{1}".format(row, col)
            await ws.update_cell(row, col, val + " ws")
            await zero_ws.update_cell(row, col, val + " zero ws")
    print("All done!")

# Turn on debugging if you're new to asyncio!
asyncio.run(example(agcm), debug=True)