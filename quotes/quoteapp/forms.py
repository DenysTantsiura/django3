from django.forms import ( 
                          CharField,
                          CheckboxSelectMultiple,
                          DateField,
                          ModelChoiceField,
                          ModelMultipleChoiceField,
                          ModelForm,
                          TextInput,
                          )

from .models import Author, Tag, Quote


class AuthorForm(ModelForm):

    fullname = CharField(min_length=3, max_length=30, required=True, widget=TextInput())
    # !!!! date!?? error_messages={'invalid': 'Enter date by format "dd.mm.YYYY"'}):
    born_date = DateField(input_formats=['%d.%m.%Y'], required=True, widget=TextInput())  
    born_location = CharField(min_length=3, max_length=220, required=True, widget=TextInput())
    description = CharField(min_length=10, max_length=4000, required=True, widget=TextInput())
    
    class Meta:
        model = Author
        fields = ['fullname', 'born_date', 'born_location', 'description']


# class TagForm(ModelForm):

#     tag = CharField(min_length=2, max_length=15, required=True, widget=TextInput())

#     class Meta:
#         model = Tag
#         fields = ['tag']


class QuoteForm(ModelForm):

    quote = CharField(min_length=10, max_length=2000, required=True, widget=TextInput(attrs={"class": "form-control"}))
    author = ModelChoiceField(queryset=Author.objects.all(), required=True)  # only 1 Author
    tags = ModelMultipleChoiceField(queryset=Tag.objects.all(), widget=CheckboxSelectMultiple)  # or Tag() # , required=True, widget=CheckboxSelectMultiple
    # tags.cleaned_data = {:,:,}
    # !!! customize field ?? modify
    # https://stackoverflow.com/questions/738301/how-to-modify-choices-of-modelmultiplechoicefield
    # https://cbi-analytics.nl/django-multiple-choice-form-how-to-use-a-modelmultiplechoicefield-function-based-views/
    # https://stackoverflow.com/questions/33997530/django-modelchoicefield-allow-objects-creation
    # tags = ModelMultipleChoiceField(queryset=None)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['tags'].queryset = Tag.objects.all() + Tag.objects.none()  # self.cleaned_data.get('tags', [])
    #     # https://www.programcreek.com/python/example/59672/django.forms.ModelMultipleChoiceField

    class Meta:
        model = Quote
        fields = ['quote', 'author', 'tags']

    # https://youtu.be/oNhNzH8FCIM?list=PLlWXhlUMyooaDkd39pknA1-Olj54HtpjX&t=1405
    # Django standart
    def clean_tags(self):
        return self.cleaned_data['tags'] # ! key 100% exist! for method clean_  .lower() ?
        # return [tag.strip() for tag in self.cleaned_data['tags'].split(',')]
 