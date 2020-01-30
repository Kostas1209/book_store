from BookShelve.models import Book, UserBasket
from BookShelve.serializer import  (BookSerializer, BookChangeSerializer, BookSerializerWithId )
from BookShelve.Services import token_service
from django.db.models import F
from django.core.mail import send_mail
from BookShelve.check_permission import required_permission
from BookShelve.exceptions import *
import BookShelve.Services.cache_service as cache
from celery import shared_task
import time


def add_book(data):
    serializer = BookSerializer(data = data)
    
    #required_permission(request, "BookShelve.add_book")                             ## Check group permission

    if serializer.is_valid(raise_exception = True):

        if len(Book.objects.filter(title = serializer.data['title'] ,
                             author =  serializer.data['author']) ) > 0 :
            print(serializer.data)

            Book.objects.filter(title = str(serializer.data['title']), author =  str(serializer.data['author']))\
                .update(amount_in_storage = F('amount_in_storage') + int(serializer.data['amount_in_storage']) )
            return "Book exists , another were added to storage"

        else:
            Book.objects.create( title = serializer.data['title'], 
                               amount_in_storage = serializer.data['amount_in_storage'],
                                author = serializer.data['author'], price = serializer.data['price'])
            return "Books were added to storage"

    else:
        raise SerializerNonValid


def get_book(book_id):

    CACHE_DATA_NAME = "book_{}".format(book_id)

    if cache.is_in_cache(CACHE_DATA_NAME):
        return cache.get_from_cache(CACHE_DATA_NAME)

    try:
        book = Book.objects.get(id = book_id)
    except ValueError:
        raise ValueError
    except Exception:
        raise NotExist
    serializer = BookSerializerWithId(book,many = False)
    cache.save_to_cache(CACHE_DATA_NAME,serializer.data)
    print("Get from database")

    return serializer.data

def get_all_books():
    
    CACHE_DATA_NAME = "books"

    if cache.is_in_cache(CACHE_DATA_NAME):
        return cache.get_from_cache(CACHE_DATA_NAME)
    
    books = Book.objects.all()
    if len(books) == 0:
        raise NotExist
    serializer = BookSerializerWithId(books, many = True)
    cache.save_to_cache(CACHE_DATA_NAME,serializer.data)
    print("Get from database")

    return serializer.data


# User Basket
@shared_task
def choose_book(user_id, data):

     #user_id = required_permission(request, "BookShelve.add_userbasket")                      ## Check group permission
     serializer_request = BookChangeSerializer(data = data,many = False)
     if serializer_request.is_valid(raise_exception = True) :
        try:
            book_info = Book.objects.get(id = serializer_request.data['book_id'])
        except KeyError as e:
            raise KeyError(str(e))
        if book_info.amount_in_storage < serializer_request.data['amount']:
            raise NotEnought

        Book.objects.filter(id = serializer_request.data['book_id'])\
                .update(amount_in_storage = F('amount_in_storage') - serializer_request.data['amount'] )
        UserBasket.objects.create(book_id = serializer_request.data['book_id'], 
                                  user_id = user_id, 
                                  amount =  serializer_request.data['amount'] )

def delete_book(user_id, book_id):
    #user_id = required_permission(request, "BookShelve.delete_userbasket")
    #try:
    ordered_books = UserBasket.objects.filter(user_id = int(user_id) , book_id = int(book_id))
    if len(ordered_books) == 0:
        raise NotFound
    #except KeyError as e:
    #    raise KeyError(str(e))
    summary_amount = 0
    for item in ordered_books:
        summary_amount += item.amount

    Book.objects.filter(id = int(book_id))\
                .update(amount_in_storage = F('amount_in_storage') + summary_amount )
    UserBasket.objects.filter(user_id = int(user_id) , book_id = int(book_id) ).delete()
    return 

def get_ordered_books(user_id):
    #user_id = required_permission(request, "BookShelve.view_userbasket")

    ordered_book = UserBasket.objects.filter(user_id = int(user_id) )
    if len(ordered_book) == 0:
        raise Empty
    user_books = {}

    for item in ordered_book:
        book = Book.objects.get(id = item.book_id)
        if book.title in user_books:
            user_books[book.title] += item.amount
        else:
            user_books[book.title] = item.amount

    return user_books



# Search
def get_similar_books(title):

    books = Book.objects.filter(title__icontains = str(title))
    if len(books) == 0:
        raise NotFound
    serializer = BookSerializer(books, many = True)
    return serializer.data

# 
def sell_user_order(user_books ):

    #user_id = required_permission(request, "BookShelve.change_userbasket")             #Check group permission
    if not user_books:
        raise Empty
    for item in user_books:
        book = Book.objects.get(id = int(item['id']))
        if book.amount_in_storage < int(item['amount']) :
            raise NotEnought

    for item in user_books:
        Book.objects.filter(id = int(item['id']))\
                .update(amount_in_storage = F('amount_in_storage') - int(item['amount']) )
        cache.delete_from_cache("book_{}".format(item['id']))   #delete  cache info about buy books

    make_delay(5)
    cache.delete_from_cache("books") #delete cache info about all books 


    return 

def user_post_save():
        send_mail(
            'Verify your QuickPublisher account',
            'Follow this link to verify your account: '
                'http://localhost:8000/api/books_catalog',
            'registrxdvv@gmail.com',
            ['fig445354545@gmail.com'],
            fail_silently=False,
        )


@shared_task
def make_delay(seconds : int ):

    print("Try toconnect...")
    time.sleep(seconds)
    print("Sent message")
 
