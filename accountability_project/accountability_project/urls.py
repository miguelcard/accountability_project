"""accountability_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from Models.users.views import Login, Logout
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('Models.users.api.urls')),
    path('groups/', include('Models.groups.api.urls')),
    path('scoreboards/', include('Models.scoreboards.api.urls')),
    path('habits/', include('Models.habits.api.urls')),
    path('login/', Login.as_view(), name = 'login'),
    path('logout/', Logout.as_view(), name = 'logout')
]
