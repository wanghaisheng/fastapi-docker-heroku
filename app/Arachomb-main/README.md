# Arachomb
Arachomb is a tool for automatic and customizable checking of a website's links and linked content.

# Installation
First, you need Python >=3.8 installed.  Clone this repository, then in the tool's folder, run 
`python -m venv venv` then `source venv/Scripts/activate` if you're on windows, otherwise run 
`source venv/bin/activate`.  Run `pip install -r requirements.txt` to install the necessary packages.
Finally, run `python cli.py -i`, `python crawler.py`, and lastly `python cli.py`.

# Filtering
The CLI tool supports filtering found errors by HTTP error code and in which subdomain they were found.
Use the `--error [error code]` and `--subdomain [subdomain]` flags to only get errors matching those filters.
