from django.urls import path
from .views import ScraperView

urlpatterns = [
    path('buscador/', ScraperView.as_view(), name='scraper_buscador'),
]