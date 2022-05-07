from sqlalchemy import (
    Column, 
    Integer,
    String,
    Boolean,
    TIMESTAMP
)
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Shops(Base):
    __tablename__ = 'shops'
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(String, nullable=False )
    ecommerce_platform = Column(String, nullable=False )
    built_with_tech_stacks = Column(String, nullable=False )
    walk_through_video_ytb_url =Column(String, nullable=False )
    walk_through_video_tiktok_url =Column(String, nullable=False )
    walk_through_video_bili_url =Column(String, nullable=False )
    urls_list =Column(String, nullable=False )
    urls_googlesheet =Column(String, nullable=False )
    urls_s3 =Column(String, nullable=False )
    urls_github =Column(String, nullable=False )
    walk_through_video_other_url =Column(String, nullable=False )
    logo = Column(String, nullable=False)
    monthly_traffic = Column(String, nullable=False)
    alexa_url_info_rank = Column(String, nullable=False )
    product_count = Column(String, nullable=False )
    collection_count = Column(String, nullable=False )
    inserted_at = Column(TIMESTAMP(timezone=False), nullable=False, default=datetime.now)    
    updated_at = Column(TIMESTAMP(timezone=False), nullable=False, default=datetime.now)    
    domain_register_date = Column(String, nullable=False )
    first_backlink_date = Column(String, nullable=False )
    backlink_count = Column(String, nullable=False )
    dead_or_alive = Column(Boolean, nullable=False )
    company_name = Column(String, nullable=False )
    ecommerce_categories = Column(String, nullable=False )
    blog_count = Column(String, nullable=False )
    page_count = Column(String, nullable=False )
    other_count = Column(String, nullable=False )
    amazon_shop = Column(String, nullable=False )
    amazon_brands = Column(String, nullable=False )
    etsy_shop = Column(String, nullable=False )
    walmart_shop = Column(String, nullable=False )
    subdomains = Column(String, nullable=False )


class Shop_sitemaps(Base):
    __tablename__ = 'shop_sitemaps'
    id = Column(Integer, primary_key=True, autoincrement=True)
    loc = Column(String, nullable=False )
    shopid = Column(String, nullable=False )
    sitemapindexurl = Column(String, nullable=False )
    domain =Column(String, nullable=False )
    lastmod =Column(String, nullable=False )
    etag =Column(String, nullable=False )
    sitemap_last_modified =Column(String, nullable=False )
    sitemap_size_mb = Column(String, nullable=False)
    crawl_time = Column(String, nullable=False)
    inserted_at = Column(TIMESTAMP(timezone=False), nullable=False, default=datetime.now)    
    updated_at = Column(TIMESTAMP(timezone=False), nullable=False, default=datetime.now)    
