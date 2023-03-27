from collections import Counter
from datetime import datetime
import itertools
from pprint import pprint

from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
import pymongo  # pymongo is a driver
from pymongo.server_api import ServerApi

from .forms import AuthorForm, QuoteForm
from .models import Author, Tag, Quote
from mongodatabase.unseed import download_data_from_mongodb
from quotes.authentication import get_password
from scrap_scrap.quote_scrapy import start_scrap  #, upload_authors_to_the_database, upload_quotes_to_the_database


MONGO_KEY = 'mongo_key.txt'  # to settings.py?


# Create your views here.
def main(request):
    all_quotes = Quote.objects.all()  # get all objects(quotes) from DB
    
    if len(all_quotes) < 9:# == len(Quote.objects.none()):
        migrate_db_from_mongo()
    
    # https://docs.djangoproject.com/en/4.1/topics/pagination/
    paginator = Paginator(all_quotes, 10)
    # A dictionary-like object containing all given HTTP GET parameters. 
    # https://docs.djangoproject.com/en/4.1/ref/request-response/
    # https://stackoverflow.com/questions/3500859/django-request-get
    page_number = request.GET.get('page', 1)  # number of page
    quotes = paginator.get_page(page_number)
    tags = get_top_tags()

    return render(request, 'quoteapp/index.html', context={"tittle": "By Den from Web 9 Group!", 
                                                           'quotes': quotes, 
                                                           'tags': tags,
                                                           })


def connect_to_mongodb():
    """Connect to  cloud database Atlas MongoDB (quoters_book)."""
    mongodb_password = get_password(MONGO_KEY)
    #  full driver connection from Database Deployments:  (mongodb+srv:)
    client = pymongo.MongoClient(
        host=f'mongodb+srv://tdv:{mongodb_password}@cluster0.7ylfcax.mongodb.net/?retryWrites=true&w=majority',
        server_api=ServerApi('1'))
    
    dbnames: list[str] = client.list_database_names()  # client.list_database_names()
    # print(f"all{dbnames}======================================")
    if 'quoters_book' in dbnames:
        print("It's there!======================================")
        return True
    # if client['quoters_book']:
    #     print("It's there!========================================")
    #     return True

    # client.quoters_book  # we refer to a non-existent database quoters_book and it is automatically created


def migrate_db_from_mongo():
    if connect_to_mongodb():
        quotes_in_json, authors_in_json = download_data_from_mongodb()

        # write to postgress:

        help_dict = {}
        print(f'@'*55)
        for author in authors_in_json:
            # print(f'........{author}........')
            new_author = Author()
            new_author.fullname = author['fullname']
            new_author.born_date = datetime.strptime(author['born_date'], '%B %d, %Y').strftime('%Y-%m-%d')  # author['born_date']  # !! October 14, 1894   to 1894-10-14
            new_author.born_location = author['born_location']
            new_author.description = author['description']
            # print(f"AID:\t{author['_id']}")
            # new_author.id = author['_id']
            try:
                help_dict[author['_id']] = Author.objects.get(fullname=author['fullname']).id
                new_author.save()
                help_dict[author['_id']] = Author.objects.get(fullname=author['fullname']).id  # new_author.id  # latest_question_list = Quote.objects.get(fullname=author['fullname']).id
            except:
                print(f'Error with {new_author.id}')  # None # print('.')

        print(help_dict)
        # [print(quote['author']) for quote in quotes_in_json if quote['author'] in help_dict]
        print(f'@'*55)
        for quote1 in quotes_in_json:
            # print(f'........{author}........')
            new_quote = Quote()
            new_quote.quote = quote1['quote']
            # new_quote.author = Author.objects.get(id=help_dict[quote1['author']]).id  # quote1['author']
            new_quote.author = Author.objects.get(id=help_dict[quote1['author']])
            print(new_quote.author)
            # new_quote.tags = quote1['tags']  # !!!!!
            print(quote1['tags'])
            list_tag_for_save = []
            for tag in quote1['tags']:
                # new_tage = Tag(tittle=tag)
                new_tage = Tag()
                new_tage.tittle = tag
                try:
                    new_tage.save()
                except:
                    print(f'Tag {Tag.objects.get(tittle=tag)} is already exist!!!___________________')# None
                print(f'~~~~~~~~~~~~~~~~~~~{Tag.objects.get(tittle=tag)}')
                list_tag_for_save.append(Tag.objects.get(tittle=tag)) if Tag.objects.get(tittle=tag) else None
            try:
                # https://stackoverflow.com/questions/4959499/how-to-add-multiple-objects-to-manytomany-relationship-at-once-in-django
                # https://docs.djangoproject.com/en/4.1/topics/db/examples/many_to_many/
                new_quote.save()
                new_quote.tags.add(*list_tag_for_save)
            except:
                None # print('.')
    else:
        print('----------NO CONNECT WITH MONGO-----------')

def read_json_file(file_path: str, encoding: str = 'utf-8') -> Any:
    """Read data from json-file, and return data."""
    with open(file_path, 'r', encoding=encoding) as file:
        data = json.load(file)

    return data


def upload_authors_to_the_database(file: str) -> None:
    """Upload authors from json-file to database."""
    authors = read_json_file(file)
    [Author(
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
        author = Author.objects(fullname=quote['author']).first()
        if author and author.id:  #
            Quote(
                tags=quote['tags'],
                author=author.id,
                quote=quote['quote']
                ).save()

        else:
            print(f'\nAuthor "{quote["author"]}" is unknown!\n')


def scrap_quotes(request):
    print('0-'*98)
    # scrap to json-files
    start_scrap()
    # filling database from json-files 
    # Filling the database - uploading json files to the cloud database:
    if not Quote.objects.all():  # Quote.objects():
        upload_authors_to_the_database('jsons_files/authors.json')
        upload_quotes_to_the_database('jsons_files/quotes.json')

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
    return render(request, 'quoteapp/upload_author.html', context={'title': 'By Den from Web 9 Group!', 
                                                                   'form': form,
                                                                   })


@login_required
def upload_quote(request):
    form = QuoteForm()
    if request.method == 'POST':
        form = QuoteForm(request.POST)  # request.POST, request.FILES, instance=Quote() 
        if form.is_valid():
            # quote = form.save(commit=False)
            # quote.user = request.user
            # quote.save()
            # quote = form.save(commit=False)
            # quote.tags = tags_str_to_list(quote.tags)  # form.tags
            # quote.save()
            form.save()
            return redirect(to='quoteapp:main')

    # request.method == 'POST' OR not form.is_valid() - просто виконуємо рендер шаблону:
    return render(request, 'quoteapp/upload_quote.html', context={'title': 'By Den from Web 9 Group!', 
                                                                  'form': form,
                                                                  })


def about_author(request, author_id_fs):
    author = get_object_or_404(Author, id=author_id_fs)
    return render(request, 'quoteapp/about_author.html', context={'title': 'By Den from Web 9 Group!',
                                                                  'author': author,
                                                                  })  # {'author': author}


def about_quote(request, quote_id_fs):
    quote = get_object_or_404(Quote, id=quote_id_fs)
    return render(request, 'quoteapp/about_quote.html', context={'title': 'By Den from Web 9 Group!',
                                                                  'quote': quote,
                                                                  })  # {'quote': quote})


def search_by_tag(request, tag_fs=''):
    # https://docs.djangoproject.com/en/4.1/ref/models/querysets/
    # quotes = Quote.objects.filter(tags__tittle__icontains=tag_fs)  # .get(...)
    quotes = Quote.objects.filter(tags__tittle=tag_fs)   
    tittle = f'Search by "{tag_fs}"'
    return render(request, 'quoteapp/the_search_result.html', {'quotes': quotes, 
                                                               'tittle': tittle,
                                                               })


@login_required
def remove_quote(request, quote_id_fs):
    Quote.objects.get(pk=quote_id_fs).delete()
    return redirect(to='quoteapp:main')


@login_required
def remove_author(request, author_id_fs):
    Author.objects.get(pk=author_id_fs).delete()
    return redirect(to='quoteapp:main')


def get_top_tags(top_count: int = 10) -> list:
    # https://docs.djangoproject.com/en/4.1/ref/models/querysets/
    # https://stackoverflow.com/questions/13070461/get-indices-of-the-top-n-values-of-a-list    
    tags = list(Quote.objects.values_list('tags', flat=True))
    # https://stackoverflow.com/questions/65201807/get-the-most-bought-top-10-items-as-a-list
    # https://www.geeksforgeeks.org/python-find-most-frequent-element-in-a-list/
    # https://docs.python.org/3/library/collections.html
    occurence_count = Counter(tags)
    top_tags = occurence_count.most_common(top_count)
    # https://stackoverflow.com/questions/9304908/how-can-i-filter-a-django-query-with-a-list-of-values
    # tags = Tag.objects.filter(tags__id__in=top_10_tags) 
    # # https://stackoverflow.com/questions/4411049/how-can-i-find-the-union-of-two-django-querysets  
        # tags = Tag.objects.filter(id=top_10_tags[0][0])
        # for tag in top_10_tags[1:]:
        #     tags = tags.union(Tag.objects.filter(id=tag[0]))

    tags = []
    for tag in top_tags:
        tags.append((Tag.objects.get(id=tag[0]),tag[1]))
                    
    return tags


def top_10(request):  # !!!
    
    tags = get_top_tags()

    return render(request, 'quoteapp/top_10.html', {'tags': tags})


# def search_by_top(request, tag_fs=''):
#     # https://docs.djangoproject.com/en/4.1/ref/models/querysets/
#     # quotes = Quote.objects.filter(tags__icontains=tag_fs)
#     quotes = Quote.objects.filter(tags__id__in=tag_fs)  # .get(...)
#     # quotes = Quote.objects.all()
#     title = f'Search by "{tag_fs}"'
#     return render(request, 'quoteapp/top_10.html', {'quotes': quotes, 
#                                                                'title': title,
#                                                                })


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
        return redirect(to="quoteapp:main")

    author = Author.objects.filter(pk=author_id_fs).first()
    return render(request, "quoteapp/edit_author.html",
                  context={"title": "By Den from Web 9 Group!", 
                           "author": author, 
                           })


@login_required
def edit_quote(request, quote_id_fs):
    form = QuoteForm()
    # https://stackoverflow.com/questions/604266/django-set-default-form-values
    if request.method == 'POST':
        form = QuoteForm(request.POST)  # request.POST, request.FILES, instance=Quote() 
        # if form.is_valid():
        #     form.save()
        #     return redirect(to='quoteapp:main')
        # quote = request.POST.get('quote')
        # author = request.POST.get('author')
        # tags = request.POST.get('tags')


        if form.is_valid():
            print('0-'*98)
            Quote.objects.get(pk=quote_id_fs).delete()
            form.save()
            return redirect(to='quoteapp:main')

            quote_form = form.save(commit=False)
            id = quote_id_fs
            quote = quote_form.quote
            author = quote_form.author
            tags = quote_form.tags
            # needs to have a value for field "id" before this many-to-many relationship can be used!!!!
            tags = [i.id for i in quote_form.tags.all()]

            Quote.objects.filter(pk=quote_id_fs).update(quote=quote, 
                                                    author=author, 
                                                    # tags=tags,
                                                    id=id,
                                                    )  # !? tags json from str?


            return redirect(to="quoteapp:main")

    # return render(request, 'quoteapp/upload_quote.html', context={'title': 'By Den from Web 9 Group!', 
    #                                                               'form': form,
    #                                                               })
    quote = Quote.objects.filter(pk=quote_id_fs).first()  # , user=request.user
    form = QuoteForm(initial={"quote": quote, 'author': quote.author, 'tags': [i.id for i in quote.tags.all()]}) 
    return render(request, "quoteapp/edit_quote.html",
                  context={"title": "By Den from Web 9 Group!", 
                           "quote": quote, 
                           'form': form,
                           })
'''
model2_inst = model2.objects.get(id=objectid)
form = model2_form(instance=model2_inst)
'''


def tags_list_to_str(tags):
    return tags[0] if len(tags) == 1 else ', '.join(tags)


def tags_str_to_list(tags):
    if isinstance(tags, str):
        return [tag.strip() for tag in tags.split(',')]
    return tags


'''


def get_object(self, id):
    try:
        return Comment.objects.get(pk=id)
    except Comment.DoesNotExist:
        return False



@login_required
def quotes(request):
    quotes = Quote.objects.filter(user=request.user).all()
    return render(request, 'quoteapp/quotes.html',
                  context={"title": "By Den from Web 9 Group!", "quotes": quotes, "media": settings.MEDIA_URL})  # !!?


@login_required
def remove(request, pic_id):
    picture = Quote.objects.filter(pk=pic_id, user=request.user)
    try:
        # os.unlink(os.path.join(settings.MEDIA_ROOT, str(picture.first().path)))
        pass
    except OSError as e:
        print(e)
    picture.delete()
    return redirect(to="quoteapp:quotes")


@login_required
def edit(request, pic_id):
    if request.method == 'POST':
        quote = request.POST.get('quote')
        author = request.POST.get('author')
        tags = request.POST.get('tags')
        # ??? pic_id
        Quote.objects.filter(pk=pic_id, user=request.user).update(quote=quote, author=author, tags=tags)  # !? tags json from str?
        return redirect(to="quoteapp:quotes")

    picture = Quote.objects.filter(pk=pic_id, user=request.user).first()
    return render(request, "quoteapp/edit.html",
                  context={"title": "By Den from Web 9 Group!", "quote": quote, "media": settings.MEDIA_URL})  # ?? media ?

# --------------------------------------------------------------

def tags_list_to_str(tags):
    return tags[0] if len(tags) == 1 else ', '.join(tags)
'''
