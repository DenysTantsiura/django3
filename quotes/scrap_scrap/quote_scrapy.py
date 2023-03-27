import json
from typing import Any

import scrapy
from scrapy.crawler import CrawlerProcess


allowed_domains = ["quotes.toscrape.com"]
start_urls = ["http://quotes.toscrape.com/"]


class GetAuthorsSpider(scrapy.Spider):
    name = "get_authors"
    # https://docs.scrapy.org/en/latest/topics/settings.html
    # custom_settings= {"FEED_URI": "../jsons_files/authors.json",}  # custom_settings = {'SOME_SETTING': 'some value',}
    # https://docs.scrapy.org/en/2.4/topics/feed-exports.html
    # https://stackoverflow.com/questions/65112996/how-to-enable-overwriting-output-files-in-scrapy-settings-py
    custom_settings = {
                       "FEEDS": {
                                "jsons_files/authors.json": {
                                                                "format": "json",
                                                                'encoding': 'utf8',
                                                                "overwrite": True,
                                                                }
                                }
                        }
    

    def parse(self, response, *_):  # async?
        # https://docs.scrapy.org/en/latest/topics/selectors.html
        links_to_about_author = response.xpath('//a[contains(@href, "/author/")]/@href').getall()  # a(href)
        # ! 1 by 1: /following-sibling::a
        # links_to_about_author=response.xpath('//div[@class="quote"]/span/small[@class="author"]/following-sibling::a')
        # print(f'\n{links_to_about_author=}\n')
        for about_author_next_page in links_to_about_author:
            # https://docs.scrapy.org/en/latest/topics/request-response.html?highlight=follow#scrapy.http.TextResponse.follow
            # https://docs.scrapy.org/en/latest/intro/tutorial.html#response-follow-example
            yield response.follow(about_author_next_page, callback=self.parse_author)  # await?

        # if exist link to next page:
        if (next_link := response.xpath("//li[@class='next']/a/@href").get()):
            # https://docs.scrapy.org/en/2.4/topics/request-response.html?highlight=scrapy.Request#scrapy.http.Request
            yield scrapy.Request(self.start_urls[0][:-1]+next_link, callback=self.parse)

    # static?
    def parse_author(self, response, *_):  # async?
        fullname = response.xpath(  # .replace('-', ' ')  for p6 Alexandre Dumas-fils
            "/html//div[@class='author-details']/h3[@class='author-title']/text()").get().strip().replace('-', ' ')
        born_date = response.xpath(
            "/html//div[@class='author-details']/p/span[@class='author-born-date']/text()").get().strip()
        born_location = response.xpath(
            "/html//div[@class='author-details']/p/span[@class='author-born-location']/text()").get().strip()
        description = response.xpath(
            "/html//div[@class='author-details']/div[@class='author-description']/text()").get().strip()
        yield {
            "fullname": fullname,
            "born_date": born_date,
            "born_location": born_location,
            "description": description,
            }


class GetQuotesSpider(scrapy.Spider):
    name = "get_quotes"
    # https://docs.scrapy.org/en/latest/topics/settings.html
    # custom_settings = {"FEED_URI": "../jsons_files/quotes.json",}  # custom_settings = {'SOME_SETTING': 'some value',}
    # https://docs.scrapy.org/en/2.4/topics/feed-exports.html
    # https://stackoverflow.com/questions/65112996/how-to-enable-overwriting-output-files-in-scrapy-settings-py
    custom_settings = {
                       "FEEDS": {
                                "jsons_files/quotes.json": {
                                                            "format": "json",
                                                            'encoding': 'utf8',
                                                            "overwrite": True,
                                                            }
                                }
                        }
    


    def parse(self, response, *_):  # async?
        for quote in response.xpath("/html//div[@class='quote']"):  # .css(...)  ...=from .select
            yield {  # .get = new methods result in a more concise and readable code  .strip()
                "quote": quote.xpath("span[@class='text']/text()").get().strip(),
                # .extract = old methods (list)[0] it's only example
                "author": quote.xpath("span/small/text()").extract()[0].strip(),
                # отримати тільки текст з тегів= додати /text():
                "tags": quote.xpath("div[@class='tags']/a/text()").extract(),
            }
        # if exist link to next page:
        if (next_link := response.xpath("//li[@class='next']/a/@href").get()):
            # https://docs.scrapy.org/en/2.4/topics/request-response.html?highlight=scrapy.Request#scrapy.http.Request
            # If the URL is invalid, a ValueError exception is raised. try-except? !!!:
            yield scrapy.Request(self.start_urls[0][:-1] + next_link)


def start_scrap(url: str):  # http://quotes.toscrape.com/
    # Scrapping
    process = CrawlerProcess()
    process.crawl(GetQuotesSpider)
    process.crawl(GetAuthorsSpider)
    process.start()  # the script will block here until the crawling is finished




# def upload_authors_to_the_database():
#     return


# def upload_quotes_to_the_database():
#     return
