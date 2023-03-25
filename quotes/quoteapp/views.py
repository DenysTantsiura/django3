import itertools

from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AuthorForm, QuoteForm
from .models import Author, Quote


# Create your views here.
def main(request):
    all_quotes = Quote.objects.all()  # get all objects(quotes) from DB
    # https://docs.djangoproject.com/en/4.1/topics/pagination/
    paginator = Paginator(all_quotes, 10)
    # A dictionary-like object containing all given HTTP GET parameters. 
    # https://docs.djangoproject.com/en/4.1/ref/request-response/
    # https://stackoverflow.com/questions/3500859/django-request-get
    page_number = request.GET.get('page', 1)  # number of page
    quotes = paginator.get_page(page_number)
    return render(request, 'quoteapp/index.html', context={"title": "By Den from Web 9 Group!", 
                                                           'quotes': quotes, 
                                                           })

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
    author = get_object_or_404(Author, author_id=author_id_fs)
    return render(request, 'quoteapp/about_author.html', context={'title': 'By Den from Web 9 Group!',
                                                                  'author': author,
                                                                  })  # {'author': author}


def about_quote(request, quote_id_fs):
    quote = get_object_or_404(Quote, quote_id=quote_id_fs)
    return render(request, 'quoteapp/about_quote.html', context={'title': 'By Den from Web 9 Group!',
                                                                  'quote': quote,
                                                                  })  # {'quote': quote})


def search_by_tag(request, tag_fs=''):
    # https://docs.djangoproject.com/en/4.1/ref/models/querysets/
    quotes = Quote.objects.filter(tags__icontains=tag_fs)
    # quotes = Quote.objects.all()
    title = f'Search by "{tag_fs}"'
    return render(request, 'quoteapp/the_search_result.html', {'quotes': quotes, 
                                                               'title': title,
                                                               })

@login_required
def remove_quote(request, quote_id_fs):
    Quote.objects.get(pk=quote_id_fs).delete()
    return redirect(to='quoteapp:main')


@login_required
def remove_author(request, author_id_fs):
    Author.objects.get(pk=author_id_fs).delete()
    return redirect(to='quoteapp:main')


def top_10(request):  # !!!
    tags = Quote.objects.values_list('tags', flat=True)
    tags_list = list(itertools.chain.from_iterable(tags))  # TypeError: 'int' object is not iterable
    tags_set = set(tags_list)
    result = []
    for tag in tags_set:
        count = tags_list.count(tag)
        result.append([tag, count])
    tags = sorted(result, key=lambda x: x[1], reverse=True)[:10]
    print(tags)
    return render(request, 'quoteapp/top_10.html', {'tags': tags})


@login_required
def edit_author(request, author_id_fs):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        born_date = request.POST.get('born_date')
        born_location = request.POST.get('born_location')
        description = request.POST.get('description')
        # ??? author_id
        Author.objects.filter(pk=author_id_fs, user=request.user).update(fullname=fullname, 
                                                                         born_date=born_date, 
                                                                         born_location=born_location,
                                                                         description=description,
                                                                         )
        return redirect(to="quoteapp:main")

    author = Author.objects.filter(pk=author_id_fs, user=request.user).first()
    return render(request, "quoteapp/edit_author.html",
                  context={"title": "By Den from Web 9 Group!", 
                           "author": author, 
                           })


@login_required
def edit_quote(request, quote_id_fs):
    if request.method == 'POST':
        quote = request.POST.get('quote')
        author = request.POST.get('author')
        tags = request.POST.get('tags')

        Quote.objects.filter(pk=quote_id_fs, user=request.user).update(quote=quote, 
                                                                       author=author, 
                                                                       tags=tags
                                                                       )  # !? tags json from str?
        return redirect(to="quoteapp:main")

    quote = Quote.objects.filter(pk=quote_id_fs, user=request.user).first()
    return render(request, "quoteapp/edit_quote.html",
                  context={"title": "By Den from Web 9 Group!", 
                           "quote": quote, 
                           })


def tags_list_to_str(tags):
    return tags[0] if len(tags) == 1 else ', '.join(tags)


def tags_str_to_list(tags):
    if isinstance(tags, str):
        return [tag.strip() for tag in tags.split(',')]
    return tags


'''
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
