from django.urls import path
from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls.static import static

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
if settings.DEBUG:
    # ✅ runserver가 STATIC_ROOT도 서빙하게 함
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)