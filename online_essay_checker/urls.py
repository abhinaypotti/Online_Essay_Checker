from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('index', views.index,name = 'index'),
    path('profile',views.profile, name='profile'),
    path('check',views.check,name='check'),
    path('',views.signIn),
    path('postsignIn/', views.postsignIn), 
    path('signUp/', views.signUp, name="signup"), 
    path('logout/', views.logout, name="log"), 
    path('postsignUp/', views.postsignUp),
    path('about',views.about,name='about'),
    path('upload_files',views.upload_files,name="upload_files"),
    path('synlink',views.synlinks,name='syn_link'),
    path('templates/user_profile.html',views.profile,name="user_profile")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)