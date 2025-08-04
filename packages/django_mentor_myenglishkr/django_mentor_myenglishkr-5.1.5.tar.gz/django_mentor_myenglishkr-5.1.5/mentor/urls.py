from django.urls import path
from django.contrib.sitemaps.views import sitemap
from . import views

from .sitemaps import StaticViewSitemap

app_name = 'mentor'

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('', views.mentor_home, name='home'),
    path('<str:lang>/', views.mentor_home, name='home'),

    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap", ),

    path('terms_of_use/', views.mentor_terms, name='terms'),
    path('privacy_policy/', views.mentor_privacy, name='privacy'),
]
