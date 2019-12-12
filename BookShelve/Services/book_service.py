from BookShelve.models import Book, UserBasket
from BookShelve.serializer import  (BookSerializer, BookChangeSerializer, SearchBooksSerializer)
from BookShelve.Services import token_service
from django.db.models import F
from BookShelve.check_permission import required_permission


def add_book(request):
    serializer = BookSerializer(data = request.data)
    
    required_permission(request, "BookShelve.add_book")                             ## Check group permission

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
        raise Exception("Invalid data")

def get_book(data):

    book = Book.objects.get(title = data['title'] , author = data['author'])
    serializer = BookSerializer(book,many = False)
    return serializer.data

def get_all_books():

    books = Book.objects.all()
    serializer = BookSerializer(books, many = True)
    return serializer.data

def change_books(request):

     required_permission(request, "BookShelve.add_userbasket")                      ## Check group permission
     serializer_request = BookChangeSerializer(data = request.data,many = False)
     if serializer_request.is_valid(raise_exception = True) :
        book_info = Book.objects.get(id = serializer_request.data['book_id'])
        #token_data = token_service.DecodeToken(token_service.ReturnAccessToken())
        if book_info.amount_in_storage < serializer_request.data['amount']:
            raise Exception("Not enought book in the storage")
        print(serializer_request.data)
        UserBasket.objects.create(book_id = serializer_request.data['book_id'], 
                                  user_id = serializer_request.data['user_id'], 
                                  amount =  serializer_request.data['amount'] )

def get_similar_books(request):

    serializer = SearchBooksSerializer(request.data)

    books = Book.objects.filter(title__icontains=serializer.data['title'])
    serializer = BookSerializer(books, many = True)
    return serializer.data

