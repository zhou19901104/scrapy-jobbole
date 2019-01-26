# -*- coding: utf-8 -*-
import scrapy
import re
import datetime

from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader # 自定义loader继承自ItemLoader
from ArticleSpider.utils.common import get_md5
# from scrapy.loader import ItemLoader



class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1、获取文章列表中的文章url，scrapy下载后并进行字段解析
        2、获取下一页的url并交给scrapy下载
        :param response: 
        :return: 
        """
        # 解析列表中的所有文章url
        # post_urls = response.css("#archive div.floated-thumb .post-thumb a::attr(href)").extract()
        post_nodes = response.css("#archive div.floated-thumb .post-thumb a")

        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first()
            # yield Request(url=parse.urljoin(response.url, post_url)) 根据下载的url,组成连接地址
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url}, callback=self.parse_detail)

        # 提取下一页，并交给scrapy下载
        next_urls = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_urls:
            yield Request(url=parse.urljoin(response.url, next_urls), callback=self.parse)


    def parse_detail(self, response):

        article_item = JobBoleArticleItem()

        # 封面图
        front_image_url = response.meta.get('front_image_url', '')
        """
        # 标题
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]
        # 创建时间
        create_date = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract()[0].strip().replace(" ·", "")
        # 点赞数
        praise_nums = int(response.xpath("//span[contains(@class, 'vote-post-up')]/h10/text()").extract()[0])
        # 收藏
        fav_nums = response.xpath("//span[contains(@class, 'bookmark-btn')]/text()").extract()[0]
        match_re = re.match(r".*?(\d+).*", fav_nums)
        if match_re:
            fav_nums = int(match_re.group(1))
        else:
            fav_nums = 0
        # 评论数
        comment_nums = response.xpath("//a[@href='#article-comment']/span/text()").extract()[0]
        match_re = re.match(r".*?(\d+).*", comment_nums)
        if match_re:
            comment_nums = int(match_re.group(1))
        else:
            comment_nums = 0
        # 标签
        tag_list =  response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract()
        tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        tags = ",".join(tag_list)
        # 内容
        content = response.xpath("//div[@class='entry']").extract()[0]
        
        article_item['title'] = title
        article_item['url'] = response.url
        article_item['url_object_id'] = get_md5(response.url)
        try:
            create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
        except Exception as e:
            # 获取当前日期
            create_date = datetime.datetime.now().date()
        article_item['create_date'] = create_date
        article_item['praise_nums'] = praise_nums
        # scrapy自动下载图片需要传列表
        article_item['front_image_url'] = [front_image_url]
        article_item['fav_nums'] = fav_nums
        article_item['comment_nums'] = comment_nums
        article_item['tags'] = tags
        article_item['content'] = content
        """

        """
        配置css、xpath、valur提取规则，简洁方便
        """
        # 通过item loader加载item
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        # item_loader.add_xpath()
        # item_loader.add_value()
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_css("create_date", ".entry-meta-hide-on-mobile::text")
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("content", "div.entry")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_value("front_image_url", [front_image_url])

        # 解析规则
        article_item = item_loader.load_item()

        # 传递到pipelines中去
        yield article_item

        """
        # 通过css提取字段
        title = response.css(".entry-header h1::text").extract()[0]
        create_date = response.css(".entry-meta-hide-on-mobile::text").extract()[0].strip().replace(" ·", "")
        praise_nums = response.css(".vote-post-up h10::text").extract()[0]
        fav_nums = response.css(".bookmark-btn::text").extract()[0]
        match_re = re.match(r".*?(\d+).*", fav_nums)
        if match_re:
            fav_nums = match_re.group(1)
        comment_nums = response.css("a[href='#article-comment'] span::text").extract()[0]
        match_re = re.match(r".*?(\d+).*", comment_nums)
        if match_re:
            comment_nums = match_re.group(1)
        content = response.css("div.entry").extract()[0]
        tag_list = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        tags = ",".join(tag_list)
        """
