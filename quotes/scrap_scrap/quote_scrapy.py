import json
import re
from typing import Any, Optional

from bs4 import BeautifulSoup
import requests


URL = 'https://quotes.toscrape.com/'  # to settings.py?


def author_about(href):
    """Filter for specific(re) seach."""
    return href and re.compile('/author/').search(href)


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
   

def start_scrap(url: str = URL):  # http://quotes.toscrape.com/
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
