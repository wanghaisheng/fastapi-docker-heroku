from supabase import create_client, Client
import os
from dotenv import load_dotenv



# 加载文件
load_dotenv(".env")
supabase_url = os.environ.get('supabase_url')
# supabase_url = 'https://bwrzzupfhzjzvuglmpwx.supabase.co'

print(supabase_url)
supabase_apikey = os.environ.get('supabase_apikey')
print(supabase_apikey)
dbsession: Client = create_client(supabase_url, supabase_apikey)

