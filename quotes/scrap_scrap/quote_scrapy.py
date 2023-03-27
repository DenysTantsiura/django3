import json
import re
from typing import Any, Optional

# import scrapy
# from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
# import pymongo  # pymongo is a driver
# from pymongo.server_api import ServerApi
import requests


URL = 'https://quotes.toscrape.com/'  # to settings.py?

# allowed_domains = ["quotes.toscrape.com"]
# start_urls = ["http://quotes.toscrape.com/"]


# class GetAuthorsSpider(scrapy.Spider):
#     name = "get_authors"
#     # https://docs.scrapy.org/en/latest/topics/settings.html
#     # custom_settings= {"FEED_URI": "../jsons_files/authors.json",}  # custom_settings = {'SOME_SETTING': 'some value',}
#     # https://docs.scrapy.org/en/2.4/topics/feed-exports.html
#     # https://stackoverflow.com/questions/65112996/how-to-enable-overwriting-output-files-in-scrapy-settings-py
#     custom_settings = {
#                        "FEEDS": {
#                                 "jsons_files/authors.json": {
#                                                                 "format": "json",
#                                                                 'encoding': 'utf8',
#                                                                 "overwrite": True,
#                                                                 }
#                                 }
#                         }
    

#     def parse(self, response, *_):  # async?
#         # https://docs.scrapy.org/en/latest/topics/selectors.html
#         links_to_about_author = response.xpath('//a[contains(@href, "/author/")]/@href').getall()  # a(href)
#         # ! 1 by 1: /following-sibling::a
#         # links_to_about_author=response.xpath('//div[@class="quote"]/span/small[@class="author"]/following-sibling::a')
#         # print(f'\n{links_to_about_author=}\n')
#         for about_author_next_page in links_to_about_author:
#             # https://docs.scrapy.org/en/latest/topics/request-response.html?highlight=follow#scrapy.http.TextResponse.follow
#             # https://docs.scrapy.org/en/latest/intro/tutorial.html#response-follow-example
#             yield response.follow(about_author_next_page, callback=self.parse_author)  # await?

#         # if exist link to next page:
#         if (next_link := response.xpath("//li[@class='next']/a/@href").get()):
#             # https://docs.scrapy.org/en/2.4/topics/request-response.html?highlight=scrapy.Request#scrapy.http.Request
#             yield scrapy.Request(self.start_urls[0][:-1]+next_link, callback=self.parse)

#     # static?
#     def parse_author(self, response, *_):  # async?
#         fullname = response.xpath(  # .replace('-', ' ')  for p6 Alexandre Dumas-fils
#             "/html//div[@class='author-details']/h3[@class='author-title']/text()").get().strip().replace('-', ' ')
#         born_date = response.xpath(
#             "/html//div[@class='author-details']/p/span[@class='author-born-date']/text()").get().strip()
#         born_location = response.xpath(
#             "/html//div[@class='author-details']/p/span[@class='author-born-location']/text()").get().strip()
#         description = response.xpath(
#             "/html//div[@class='author-details']/div[@class='author-description']/text()").get().strip()
#         yield {
#             "fullname": fullname,
#             "born_date": born_date,
#             "born_location": born_location,
#             "description": description,
#             }


# class GetQuotesSpider(scrapy.Spider):
#     name = "get_quotes"
#     # https://docs.scrapy.org/en/latest/topics/settings.html
#     # custom_settings = {"FEED_URI": "../jsons_files/quotes.json",}  # custom_settings = {'SOME_SETTING': 'some value',}
#     # https://docs.scrapy.org/en/2.4/topics/feed-exports.html
#     # https://stackoverflow.com/questions/65112996/how-to-enable-overwriting-output-files-in-scrapy-settings-py
#     custom_settings = {
#                        "FEEDS": {
#                                 "jsons_files/quotes.json": {
#                                                             "format": "json",
#                                                             'encoding': 'utf8',
#                                                             "overwrite": True,
#                                                             }
#                                 }
#                         }
    


#     def parse(self, response, *_):  # async?
#         for quote in response.xpath("/html//div[@class='quote']"):  # .css(...)  ...=from .select
#             yield {  # .get = new methods result in a more concise and readable code  .strip()
#                 "quote": quote.xpath("span[@class='text']/text()").get().strip(),
#                 # .extract = old methods (list)[0] it's only example
#                 "author": quote.xpath("span/small/text()").extract()[0].strip(),
#                 # отримати тільки текст з тегів= додати /text():
#                 "tags": quote.xpath("div[@class='tags']/a/text()").extract(),
#             }
#         # if exist link to next page:
#         if (next_link := response.xpath("//li[@class='next']/a/@href").get()):
#             # https://docs.scrapy.org/en/2.4/topics/request-response.html?highlight=scrapy.Request#scrapy.http.Request
#             # If the URL is invalid, a ValueError exception is raised. try-except? !!!:
#             yield scrapy.Request(self.start_urls[0][:-1] + next_link)


def author_about(href):
    """Filter for specific(re) seach."""
    return href and re.compile("/author/").search(href)


def gather_information(url: str) -> tuple[list, list]:
    """Gather information from one page by URL.
    Return content for two json-files."""
    if not (soup := get_soup_from_url(url)):  # (url, 'html.parser')
        return ([], [])
    
    quotes = [quote.text for quote in soup.find_all('span', class_='text')]  # .find_all('span', attrs={'class':'text'})
    fullnames = [name.text for name in soup.find_all('small', class_='author')]
    # generate list of right links to author's about:
    abouts = [URL.replace('https:', 'http:')+about['href'][1:]+'/'
              for about in soup.find_all(href=author_about)]   # ('a', href=True)
    tags = [tag.find_all('a', class_='tag') for tag in soup.find_all('div', class_='tags')]
    tags = [[el.text for el in tag] for tag in tags]

    # grab author's about data to lists
    born_date = []
    born_location = []
    description = []

    for about in abouts:
        if not (soup_about := get_soup_from_url(about)):  # (about, 'html.parser')
            continue

        born_date.append(soup_about.find('span', class_='author-born-date').text)
        born_location.append(soup_about.find('span', class_='author-born-location').text)
        description.append(soup_about.find('div', class_='author-description').text)

    quotes_in_json = [{'tags': tags[el],
                       'author': fullnames[el],
                       'quote': quotes[el],
                       }
                      for el in range(len(quotes))]

    authors_in_json = [{'fullname': fullnames[el],
                        'born_date': born_date[el],
                        'born_location': born_location[el],
                        'description': description[el],
                        } 
                       for el in range(len(fullnames))] 
    
    return quotes_in_json, authors_in_json


# let's convert the response from the server into lxml format
def get_soup_from_url(url: str, parser: str = 'lxml') -> Optional[BeautifulSoup]:
    """Return instance of BeautifulSoup class."""
    response = requests.get(url)  # response.text: str;  response.content: bytes 
    if response.status_code == 200:
        return BeautifulSoup(response.text, parser) if parser == 'lxml' else BeautifulSoup(response.content, parser)
   

def duplicate_remover(original_list: list[dict], new_list: list[dict]) -> list[dict]:
    """Remove same data of known autor by addition unknown authors."""
    duplicate = False
    for new_author in new_list:
        for author in original_list:
            if new_author.get('description', 0) == author.get('description', 1):
                duplicate = True
                break
        original_list.append(new_author) if not duplicate else (duplicate := False)
    
    return original_list


def start_scrap(url: str=URL):  # http://quotes.toscrape.com/
    # Scrapping
    # process = CrawlerProcess()
    # process.crawl(GetQuotesSpider)
    # process.crawl(GetAuthorsSpider)
    # process.start()  # the script will block here until the crawling is finished
    quotes_in_json, new_authors = gather_information(url)
    authors_in_json = duplicate_remover([], new_authors)
    next_page = 2
    new_quotes = quotes_in_json

    while new_quotes:  # if data on page exist
        url_next = f'{URL}/page/{next_page}/'  # http://quotes.toscrape.com/page/10/
        # print(url_next)
        new_quotes, new_authors = gather_information(url_next)
        if not new_quotes:  # break if no data on page
            print(f'No information on page #{next_page}\n')
            break
        
        quotes_in_json.extend(new_quotes)
        duplicate_remover(authors_in_json, new_authors)  # authors_in_json = ...
        next_page += 1

    # write if exist
    save_to_json('jsons_files/authors.json', authors_in_json) if authors_in_json else None
    save_to_json('jsons_files/quotes.json', quotes_in_json) if quotes_in_json else None


def save_to_json(file: str, json_data: list, encoding: str = 'utf-8') -> None:
    """Save to json-file."""
    with open(file, 'w', encoding=encoding) as fh:  # try-except!
        json.dump(json_data, fh)






# def upload_authors_to_the_database():
#     return


# def upload_quotes_to_the_database():
#     return
