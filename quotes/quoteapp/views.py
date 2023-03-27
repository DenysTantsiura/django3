from collections import Counter
from datetime import datetime
import json
# import re
from typing import Any

from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
import pymongo  # pymongo is a driver
from pymongo.server_api import ServerApi

from .forms import AuthorForm, QuoteForm
from .models import Author, Tag, Quote
from mongodatabase.unseed import download_data_from_mongodb
from scrap_scrap.quote_scrapy import start_scrap
from quotes.authentication import get_password


MONGO_KEY = 'mongo_key.txt'  # to settings.py?


# Create your views here.
def main(request):
    all_quotes = Quote.objects.all()  # get all objects(quotes) from DB

    # FOR MIGRATE FROM MONGO:
    # if len(all_quotes) < 9:# == len(Quote.objects.none()):
    #     migrate_db_from_mongo()
    
    # https://docs.djangoproject.com/en/4.1/topics/pagination/
    paginator = Paginator(all_quotes, 10)
    # A dictionary-like object containing all given HTTP GET parameters. 
    # https://docs.djangoproject.com/en/4.1/ref/request-response/
    # https://stackoverflow.com/questions/3500859/django-request-get
    page_number = request.GET.get('page', 1)  # number of page
    quotes = paginator.get_page(page_number)
    tags = get_top_tags()

    return render(request, 'quoteapp/index.html', context={'tittle': 'By Den from Web 9 Group!',
                                                           'quotes': quotes, 
                                                           'tags': tags,
                                                           })


def connect_to_mongodb():
    """Connect to  cloud database Atlas MongoDB (quoters_book)."""
    mongodb_password = get_password(MONGO_KEY)
    #  full driver connection from Database Deployments:
    client = pymongo.MongoClient(
        host=f'mongodb+srv://tdv:{mongodb_password}@cluster0.7ylfcax.mongodb.net/?retryWrites=true&w=majority',
        server_api=ServerApi('1'))
    
    dbnames: list[str] = client.list_database_names()  # client.list_database_names()
    if 'quoters_book' in dbnames:
        return True


def migrate_db_from_mongo():
    if connect_to_mongodb():
        quotes_in_json, authors_in_json = download_data_from_mongodb()

        # write to Postgres:
        help_dict = {}
        for author in authors_in_json:
            new_author = Author()
            new_author.fullname = author['fullname']
            # October 14, 1894   to 1894-10-14:
            new_author.born_date = datetime.strptime(author['born_date'], '%B %d, %Y').strftime('%Y-%m-%d')
            new_author.born_location = author['born_location']
            new_author.description = author['description']
            try:
                help_dict[author['_id']] = Author.objects.get(fullname=author['fullname']).id
                new_author.save()
                # new_author.id  # latest_quest_list = Quote.objects.get(fullname=author['fullname']).id
                help_dict[author['_id']] = Author.objects.get(fullname=author['fullname']).id

            except Exception as err:
                print(f'Error with {new_author.id}\n{err}')  # None # print('.')

        for quote1 in quotes_in_json:
            new_quote = Quote()
            new_quote.quote = quote1['quote']
            new_quote.author = Author.objects.get(id=help_dict[quote1['author']])  # .id
            list_tag_for_save = []
            for tag in quote1['tags']:
                new_tage = Tag()
                new_tage.tittle = tag
                try:
                    new_tage.save()

                except Exception as err:
                    print(f'~~~~~~~ Tag {Tag.objects.get(tittle=tag)} is already exist!\n{err}')  # None

                list_tag_for_save.append(Tag.objects.get(tittle=tag)) if Tag.objects.get(tittle=tag) else None
            try:
                # https://stackoverflow.com/questions/4959499/how-to-add-multiple-objects-to-manytomany-relationship-at-once-in-django
                # https://docs.djangoproject.com/en/4.1/topics/db/examples/many_to_many/
                new_quote.save()
                new_quote.tags.add(*list_tag_for_save)

            except Exception as err:  # ! ...
                print(f'~~~~~~~ Can`t save Quote!\n{err}')  # None
    else:
        print('----------NO CONNECT WITH MONGO-----------')


def read_json_file(file_path: str, encoding: str = 'utf-8') -> Any:
    """Read data from json-file, and return data."""
    with open(file_path, 'r', encoding=encoding) as file:
        data = json.load(file)

    return data


def upload_to_the_database(file_a: str, file_q: str) -> None:
    """Upload from json-files to database."""
    authors_in_json = read_json_file(file_a)
    for author in authors_in_json:
        new_author = Author()
        new_author.fullname = author['fullname']
        #  October 14, 1894   to 1894-10-14:
        new_author.born_date = datetime.strptime(author['born_date'], '%B %d, %Y').strftime('%Y-%m-%d')
        new_author.born_location = author['born_location']
        new_author.description = author['description']
        try:
            new_author.save()

        except Exception as err:
            print(f'Error with {new_author.id},\n{err}')  # None # print('.')
    
    quotes_in_json = read_json_file(file_q)
    for quote1 in quotes_in_json:
        new_quote = Quote()
        new_quote.quote = quote1['quote']
        # Author.objects.get(id=help_dict[quote1['author']])
        new_quote.author = Author.objects.get(fullname=quote1['author'])
        list_tag_for_save = []
        for tag in quote1['tags']:
            # new_tage = Tag(tittle=tag)
            new_tage = Tag()
            new_tage.tittle = tag
            try:
                new_tage.save()

            except Exception as err:
                print(f'~~~~~~~ Tag {Tag.objects.get(tittle=tag)} is already exist!\n{err}')  # None

            list_tag_for_save.append(Tag.objects.get(tittle=tag)) if Tag.objects.get(tittle=tag) else None
        try:
            # https://stackoverflow.com/questions/4959499/how-to-add-multiple-objects-to-manytomany-relationship-at-once-in-django
            # https://docs.djangoproject.com/en/4.1/topics/db/examples/many_to_many/
            new_quote.save()
            new_quote.tags.add(*list_tag_for_save)

        except Exception as err:  # ! ...
            print(f'~~~~~~~ Can`t save Quote!\n{err}')  # None


def scrap_quotes(request):  # _
    """Scrap to json-files and fill empty database."""

    # Filling the database - uploading json files to the cloud database:
    if not Quote.objects.all():  # Quote.objects():
        # scrap to json-files
        start_scrap()
        upload_to_the_database('jsons_files/authors.json', 'jsons_files/quotes.json')

    return redirect(to='quoteapp:main')


@login_required
def upload_author(request):
    form = AuthorForm()
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect(to='quoteapp:main')
        
    # request.method == 'POST' OR not form.is_valid() - просто виконуємо рендер шаблону:
    return render(request, 'quoteapp/upload_author.html',
                  context={'title': 'By Den from Web 9 Group!',
                           'form': form,
                           })


@login_required
def upload_quote(request):
    form = QuoteForm()
    if request.method == 'POST':
        form = QuoteForm(request.POST)  # request.POST, request.FILES, instance=Quote() 
        if form.is_valid():
            form.save()
            return redirect(to='quoteapp:main')

    # request.method == 'POST' OR not form.is_valid() - просто виконуємо рендер шаблону:
    return render(request, 'quoteapp/upload_quote.html',
                  context={'title': 'By Den from Web 9 Group!',
                           'form': form,
                           })


def about_author(request, author_id_fs):
    author = get_object_or_404(Author, id=author_id_fs)
    return render(request, 'quoteapp/about_author.html',
                  context={'title': 'By Den from Web 9 Group!',
                           'author': author,
                           })  # {'author': author}


def about_quote(request, quote_id_fs):
    quote = get_object_or_404(Quote, id=quote_id_fs)
    return render(request, 'quoteapp/about_quote.html',
                  context={'title': 'By Den from Web 9 Group!',
                           'quote': quote,
                           })  # {'quote': quote})


def search_by_tag(request, tag_fs=''):
    # https://docs.djangoproject.com/en/4.1/ref/models/querysets/
    # quotes = Quote.objects.filter(tags__tittle__icontains=tag_fs)  # .get(...)
    quotes = Quote.objects.filter(tags__tittle=tag_fs)   
    tittle = f'Search by "{tag_fs}"'
    return render(request, 'quoteapp/the_search_result.html',
                  context={'quotes': quotes,
                           'tittle': tittle,
                           })


@login_required
def remove_quote(request, quote_id_fs):  # _, quote_id_fs
    Quote.objects.get(pk=quote_id_fs).delete()
    return redirect(to='quoteapp:main')


@login_required
def remove_author(request, author_id_fs):  # _, author_id_fs
    Author.objects.get(pk=author_id_fs).delete()
    return redirect(to='quoteapp:main')


def get_top_tags(top_count: int = 10) -> list:
    # https://docs.djangoproject.com/en/4.1/ref/models/querysets/
    # https://stackoverflow.com/questions/13070461/get-indices-of-the-top-n-values-of-a-list    
    tags = list(Quote.objects.values_list('tags', flat=True))
    # https://stackoverflow.com/questions/65201807/get-the-most-bought-top-10-items-as-a-list
    # https://www.geeksforgeeks.org/python-find-most-frequent-element-in-a-list/
    # https://docs.python.org/3/library/collections.html
    number_of_cases = Counter(tags)
    top_tags = number_of_cases.most_common(top_count)
    # https://stackoverflow.com/questions/9304908/how-can-i-filter-a-django-query-with-a-list-of-values
    # tags = Tag.objects.filter(tags__id__in=top_10_tags) 
    # # https://stackoverflow.com/questions/4411049/how-can-i-find-the-union-of-two-django-querysets  

    # tags = []
    # for tag in top_tags:
    #     tags.append((Tag.objects.get(id=tag[0]), tag[1]))
    tags = [(Tag.objects.get(id=tag[0]), tag[1]) for tag in top_tags]
                    
    return tags


def top_10(request):
    
    tags = get_top_tags()

    return render(request, 'quoteapp/top_10.html', {'tags': tags})


@login_required
def edit_author(request, author_id_fs):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        born_date = request.POST.get('born_date')
        born_location = request.POST.get('born_location')
        description = request.POST.get('description')

        Author.objects.filter(pk=author_id_fs).update(fullname=fullname,
                                                      born_date=born_date,
                                                      born_location=born_location,
                                                      description=description,
                                                      )
        return redirect(to='quoteapp:main')

    author = Author.objects.filter(pk=author_id_fs).first()
    return render(request, 'quoteapp/edit_author.html',
                  context={'title': 'By Den from Web 9 Group!',
                           'author': author,
                           })


@login_required
def edit_quote(request, quote_id_fs):
    # form = QuoteForm()
    # https://stackoverflow.com/questions/604266/django-set-default-form-values
    if request.method == 'POST':
        form = QuoteForm(request.POST)  # request.POST, request.FILES, instance=Quote() 

        if form.is_valid():
            Quote.objects.get(pk=quote_id_fs).delete()
            form.save()

            return redirect(to='quoteapp:main')

    quote = Quote.objects.filter(pk=quote_id_fs).first()  # , user=request.user
    form = QuoteForm(initial={'quote': quote, 'author': quote.author, 'tags': [i.id for i in quote.tags.all()]})
    return render(request, 'quoteapp/edit_quote.html',
                  context={'title': 'By Den from Web 9 Group!',
                           'quote': quote,
                           'form': form,
                           })


'''
def tags_list_to_str(tags):
    return tags[0] if len(tags) == 1 else ', '.join(tags)


def tags_str_to_list(tags):
    if isinstance(tags, str):
        return [tag.strip() for tag in tags.split(',')]
    return tags
'''
