import json
from typing import Any

from mongodatabase.models import Author as MongoAuthor
from mongodatabase.models import Quote as MongoQuote
import mongodatabase.connect  # excessive?


def save_to_json(file: str, json_data: list, encoding: str = 'utf-8') -> None:
    """Save to json-file."""
    with open(file, 'w', encoding=encoding) as fh:  # try-except!
        json.dump(json_data, fh)


def read_json_file(file_path: str, encoding: str = 'utf-8') -> Any:
    """Read data from json-file, and return data."""
    with open(file_path, 'r', encoding=encoding) as file:
        data = json.load(file)

    return data


def download_data_from_mongodb():
    authors = MongoAuthor.objects()
    authors_in_json = []
    for author in authors:
        authors_in_json.append(author.to_mongo().to_dict())

    quotes = MongoQuote.objects()
    quotes_in_json = []
    for quote in quotes:
        quotes_in_json.append(quote.to_mongo().to_dict())

    '''...
    'fullname': 'J.M. Barrie'},
    {'_id': ObjectId('6410119e7a8b7335dd2f84c0'),
    'born_date': 'October 14, 1894',
    'born_location': 'in Cambridge, Massachusetts, The United States',
    'description': 'Edward Estlin C...
    '''

    return quotes_in_json, authors_in_json 


def upload_authors_to_the_database(file: str) -> None:
    """Upload authors from json-file to database."""
    authors = read_json_file(file)
    [MongoAuthor(
        fullname=author['fullname'],
        born_date=author['born_date'],
        born_location=author['born_location'],
        description=author['description']
        ).save()
        for author in authors]


def upload_quotes_to_the_database(file: str) -> None:
    """Upload quotes from json-file to database."""
    quotes = read_json_file(file)
    for quote in quotes: 
        author = MongoAuthor.objects(fullname=quote['author']).first()
        if author and author.id:  #
            MongoQuote(
                tags=quote['tags'],
                author=author.id,
                quote=quote['quote']
                ).save()

        else:
            print(f'\nAuthor "{quote["author"]}" is unknown!\n')


if __name__ == '__main__':
    quotes_in_json, authors_in_json = download_data_from_mongodb()
    save_to_json('jsons_files/authors.json', authors_in_json) if authors_in_json else None
    save_to_json('jsons_files/quotes.json', quotes_in_json) if quotes_in_json else None

    # to download json-files to Cloud-database:
    if not MongoQuote.objects():
        upload_authors_to_the_database('../jsons_files/authors.json')
        upload_quotes_to_the_database('../jsons_files/quotes.json')
