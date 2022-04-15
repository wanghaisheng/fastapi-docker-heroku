import advertools as adv
import pandas as pd
# bbc_sitemap = adv.sitemap_to_df('http://www.cettire.com/robots.txt', recursive=False)
# print(bbc_sitemap.head(10))


adv.crawl('https://dogsexdolls.com', 'my_output_file.jl', follow_links=True)
crawl_df = pd.read_json('my_output_file.jl', lines=True)
print(crawl_df['url'].tolist())