"""
URL configuration for DiaryProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
# Import Django admin and include function
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static  # To serve media files in development
from django.conf import settings

import users.views

# Define project-level URL routes
urlpatterns = [
    path('admin/', admin.site.urls),
    # Django admin
    path('ckeditor/', include('ckeditor_uploader.urls')),  # CKEditor upload support

    path('users/', include('users.urls', namespace='users')),  # Auth and profile

    path('diary/', include('diary.urls',namespace='diary')),
    path('', include('pages.urls', namespace='pages')),
    path('set-language/<str:lang_code>/', users.views.set_language, name='set_language'),

]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)