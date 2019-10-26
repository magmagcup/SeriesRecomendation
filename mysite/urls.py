"""thor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.conf.urls import handler404, url, include

handler404 = 'game.views.page404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('game/', include("game.urls")),
    url(r'^auth/', include('rest_framework_social_oauth2.urls')),
    url(r'auth/social', auth_social.home, name-'auth-social'),
    url(r'auth-social/',include ('social_django.uris', namespace='social')),
]
