from django.core.checks import messages
from rest_framework import response
from BookShelve.models import Book, UserBasket, Library, Comment, Author
from BookShelve.serializer import *
from BookShelve.Services import token_service, user_service
from django.db.models import F
from django.core.mail import send_mail
from BookShelve.check_permission import required_permission
from BookShelve.exceptions import *
import BookShelve.Services.cache_service as cache
from celery import shared_task
import time



AMOUNT_ITEMS_ON_PAGE = 5

def add_book(data):
    print(data)
    serializer = BookSerializer(data = data.book)
    
    #required_permission(request, "BookShelve.add_book")                             ## Check group permission

    if serializer.is_valid(raise_exception = True):
        found_books = Book.objects.filter(title = serializer.data['title'])
        books_in_library = Library.objects.filter(book_id = found_books.id, author_id = data.authors_ids[0])
        is_book_exists = len(books_in_library) > 0
        if is_book_exists:
            print(serializer.data)

            Book.objects.filter(title = str(serializer.data['title'])).update(amount_in_storage = F('amount_in_storage') + int(serializer.data['amount_in_storage']) )
            return "Book exists , another were added to storage"

        else:
            Book.objects.create( title = serializer.data['title'], 
                               amount_in_storage = serializer.data['amount_in_storage'], price = serializer.data['price'])
            return "Books were added to storage"

    else:
        raise SerializerNonValid


def get_book(book_id):

    CACHE_DATA_NAME = "book_{}".format(book_id)

    if cache.is_in_cache(CACHE_DATA_NAME):
        return cache.get_from_cache(CACHE_DATA_NAME)

    try:
        book = Book.objects.get(id = book_id)
        authors = []
        librarys = Library.objects.filter(book_id = book.id).values_list('author_id')
        authors_queryset = Author.objects.filter(pk__in=librarys) 
        authors = AuthorSerializer(authors_queryset,many=True).data
    except ValueError:
        raise ValueError
    except Exception:
        raise NotExist
    print("Get from database")

    return serialize_book(book, authors)

def serialize_book(book, authors):
    serialized_book = BookSerializer(book).data
    # serialized_author = AuthorSerializer(authors,many=True).data
    response = {}

    response["id"] = serialized_book["id"]
    response["price"] = serialized_book["price"]
    response['amount_in_storage'] = serialized_book["amount_in_storage"]
    response['title'] = serialized_book["title"]
    response['author'] = authors
    print(response)

    return response

def get_all_books():
    
    CACHE_DATA_NAME = "books"

    if cache.is_in_cache(CACHE_DATA_NAME):
        return cache.get_from_cache(CACHE_DATA_NAME)
    
    books = Book.objects.all()
    response_book = list()
    for book in books:
        authors = []
        librarys = Library.objects.filter(book_id = book.id).values_list('author_id')
        authors_queryset = Author.objects.filter(pk__in=librarys) 
        authors = AuthorSerializer(authors_queryset,many=True).data
        response_book.append(serialize_book(book, authors))
        

    if len(books) == 0:
        raise NotExist

    return response_book


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
    response_book = list()
    for book in books:
        authors = []
        librarys = Library.objects.filter(book_id = book.id).values_list('author_id')
        authors_queryset = Author.objects.filter(pk__in=librarys) 
        authors = AuthorSerializer(authors_queryset,many=True).data
        response_book.append(serialize_book(book, authors))
        

    if len(books) == 0:
        raise NotExist

    return response_book

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

# comments
def get_comments(book_id: str, page: int):
    def serialize_comment_with_user(comment, user):
        serialized_comment = CommentSerializer(comment).data

        response = {}

        response["id"] = serialized_comment["id"]
        response["user"] = user
        response["message"] = serialized_comment["message"]

        print(response)

        return response


    comments = Comment.objects.filter(book_id = book_id)
    # serialized_comments = CommentSerializer(comments, many=True)
    print(comments)
    response_comments = list()
    for comment in comments:
        print(comment)
        user = user_service.get_user_info(comment.user_id)
        response_comments.append(serialize_comment_with_user(comment, user))

    return response_comments

def add_comment(data, user_id):
    print(data)
    Comment.objects.create(message=data['message'],book_id=data['book_id'], user_id=user_id)


@shared_task
def make_delay(seconds : int ):

    print("Try toconnect...")
    time.sleep(seconds)
    print("Sent message")
 
