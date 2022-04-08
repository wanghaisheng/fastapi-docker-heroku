import advertools as adv

bbc_sitemap = adv.sitemap_to_df('http://www.cettire.com/robots.txt', recursive=False)
print(bbc_sitemap.head(10))
