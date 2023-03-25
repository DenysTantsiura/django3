from django.forms import ( 
                          CharField,
                          DateField,
                          ModelChoiceField,
                          ModelForm,
                          TextInput,
                          )

from .models import Author, Quote


class AuthorForm(ModelForm):

    fullname = CharField(min_length=3, max_length=30, required=True, widget=TextInput())
    # !!!! date!?? error_messages={'invalid': 'Enter date by format "dd.mm.YYYY"'}):
    born_date = DateField(input_formats=['%d.%m.%Y'], required=True, widget=TextInput())  
    born_location = CharField(min_length=3, max_length=25, required=True, widget=TextInput())
    description = CharField(min_length=10, max_length=2000, required=True, widget=TextInput())
    
    class Meta:
        model = Author
        fields = ['fullname', 'born_date', 'born_location', 'description']


class QuoteForm(ModelForm):

    quote = CharField(min_length=10, max_length=2000, required=True, widget=TextInput(attrs={"class": "form-control"}))
    # author = CharField(min_length=10, max_length=2000, required=True, widget=TextInput(attrs={"class": "form-control"}))  # ! id? by model ?
    author = ModelChoiceField(queryset=Author.objects.all(), required=True)
    tags =  CharField(max_length=32, required=True, widget=TextInput(attrs={'placeholder': 'Enter tags separated by comma.'}))# list? json from string ?
    
    class Meta:
        model = Quote
        fields = ['quote', 'author', 'tags']

    def clean_tags(self):
        return [tag.strip() for tag in self.cleaned_data['tags'].split(',')]
    