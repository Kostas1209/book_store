"""book_store URL Configuration

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
from django.urls import path, include

from .Views import book_views, user_views

urlpatterns = [
    path('book_catalog/', book_views.BooksView.as_view() ), # +
    path('single_book/', book_views.GetSingleBookView.as_view() ),  #+
    path('add_book/', book_views.AddBookView.as_view() ), 
    path('registr/', user_views.RegistrUserView.as_view() ), # +
    path('login/', user_views.LoginView.as_view()), # +
    path('refresh/',user_views.RefreshAccessTokenView.as_view() ), # ?
    path('user_basket/', book_views.UserBasketView.as_view()),   # delete    
    path('search/', book_views.SearchSimilarBooksView.as_view()), # +
    path('sell_books/', book_views.MakeOrderView.as_view()), # +
    path('user_info/', user_views.UserInfoView.as_view()), # +
    path('user_avatar/', user_views.UserAvatarView.as_view()), # That is a problem
    path('logout/', user_views.LogoutView.as_view()), # + need to make autorefresh
    path('book_comments/', book_views.BookCommentsView.as_view())

]
