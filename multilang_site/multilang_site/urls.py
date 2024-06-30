"""
URL configuration for multilang_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog
from django.contrib import admin
from django.urls import include, path
from main.views import article_views, assistant_views

urlpatterns = [path('i18n/', include("django.conf.urls.i18n")),
               path("jsi18n/", JavaScriptCatalog.as_view(),
                    name="javascript-catalog")]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', article_views.base),
    path('articles/', article_views.ArticlesView.as_view(), name="articles"),
    path('article/', article_views.article),
    path("chat/", assistant_views.chat_window),
    path('search/', article_views.search)
)
