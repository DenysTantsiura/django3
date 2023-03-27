from django.urls import path

from . import views


app_name = 'quoteapp'  # визначає префікс для маршруту в атрибуті action форми з ім'ям маршруту

urlpatterns = [
    # name= ім'я маршруту, щоб працювала зв'язка атрибуту action="{% url 'webapp:name' %}" форми з ім'ям маршруту
    path('', views.main, name='main'),  # 'root'
    path('scrap_quotes/', views.scrap_quotes, name='scrap_quotes'),
    path('upload_author/', views.upload_author, name='upload_author'),
    path('upload_quote/', views.upload_quote, name='upload_quote'),
    path('about_author/<int:author_id_fs>/', views.about_author, name='about_author'),
    path('about_quote/<int:quote_id_fs>/', views.about_quote, name='about_quote'),
    path('quoteapp/search_by_tag/<str:tag_fs>/', views.search_by_tag, name='search_by_tag'),
    path('quoteapp/remove_quote/<int:quote_id_fs>/', views.remove_quote, name='remove_quote'),
    path('quoteapp/remove_author/<int:author_id_fs>/', views.remove_author, name='remove_author'),
    path('quoteapp/edit_quote/<int:quote_id_fs>', views.edit_quote, name='edit_quote'),
    path('quoteapp/edit_author/<int:author_id_fs>', views.edit_author, name='edit_author'),
    path('quoteapp/top_10/', views.top_10, name='top_10'),
]  
