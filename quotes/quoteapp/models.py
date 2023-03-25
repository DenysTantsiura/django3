import json
from datetime import date

from django.contrib.postgres.fields import ArrayField
from django.db import models


# Create your models here.
class Author(models.Model):
    # author_id = models.AutoField(primary_key=True, null=False)
    fullname = models.CharField(max_length=30, null=False, unique=True)
    # born_date = models.CharField(max_length=20, null=False)  # models.DateTimeField(auto_now_add=False)
    born_date = models.DateField()
    born_location = models.CharField(max_length=25, null=False)
    description = models.CharField(max_length=2000, null=False)  # or TextField()?

    # https://stackoverflow.com/questions/25205228/django-autofield-with-primary-key-vs-default-pk
    @property
    def author_id(self):
       return self.id

    def __str__(self):
        return f'{self.fullname}'
    
    # class Meta:
    #     managed = False
    #     db_table = 'author'


class Tag(models.Model):
    tittle = models.CharField(max_length=15, unique=True)

    def __str__(self) -> str:
        return f"{self.tittle}"


class Quote(models.Model):
    # quote_id = models.AutoField(primary_key=True, null=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, default=1)  # Many-to-one relationships
    quote = models.CharField(max_length=2000, null=False, unique=True)  # or TextField()?
    # tags = models.CharField(max_length=200) # or ArrayField(models.TextField(max_length=200))
    # https://stackoverflow.com/questions/44630642/is-it-possible-to-store-an-array-in-django-model
    # tags = models.JSONField()  # set limits ?  # 
    # tags = ArrayField(models.TextField(max_length=200), size=8, blank=False)  # , default=list ??; size is an optional argument
    tags = models.ManyToManyField('Tag', blank=False, related_name='quotes') # models.ForeignKey(Tag, on_delete=models.CASCADE)
    # !!!
    def __str__(self):
        return f'{self.quote}'
    
    # https://stackoverflow.com/questions/25205228/django-autofield-with-primary-key-vs-default-pk
    @property
    def quote_id(self):
       return self.id

    # def set_tags(self, tag_list):
    #     self.tags = json.dumps(tag_list)

    # def get_tags(self):
    #     return json.loads(self.tags)
    