from BookShelve.models import Book, UserBasket
from BookShelve.serializer import  (BookSerializer, BookChangeSerializer, )
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


def get_book(request):

    book = Book.objects.get(id = request.data['book_id'])
    serializer = BookSerializer(book,many = False)
    return serializer.data

def get_all_books():

    books = Book.objects.all()
    serializer = BookSerializer(books, many = True)
    return serializer.data


# User Basket
def choose_book(request):

     user_id = required_permission(request, "BookShelve.add_userbasket")                      ## Check group permission
     serializer_request = BookChangeSerializer(data = request.data,many = False)
     if serializer_request.is_valid(raise_exception = True) :
        book_info = Book.objects.get(id = serializer_request.data['book_id'])
        
        if book_info.amount_in_storage < serializer_request.data['amount']:
            raise Exception("Not enought book in the storage")

        print(serializer_request.data)
        Book.objects.filter(id = serializer_request.data['book_id'])\
                .update(amount_in_storage = F('amount_in_storage') - serializer_request.data['amount'] )
        UserBasket.objects.create(book_id = serializer_request.data['book_id'], 
                                  user_id = user_id, 
                                  amount =  serializer_request.data['amount'] )

def delete_book(request):
    user_id = required_permission(request, "BookShelve.delete_userbasket")

    ordered_books = UserBasket.objects.filter(user_id = user_id , book_id = int(request.data ['book_id']))
    summary_amount = 0
    for item in ordered_books:
        summary_amount += item.amount

    Book.objects.filter(id = int(request.data ['book_id']))\
                .update(amount_in_storage = F('amount_in_storage') + summary_amount )
    UserBasket.objects.filter(user_id = user_id , book_id = int(request.data ['book_id']) ).delete()
    return 

def get_ordered_books(request):
    user_id = required_permission(request, "BookShelve.view_userbasket")

    ordered_book = UserBasket.objects.filter(user_id = user_id )
    user_books = {}

    for item in ordered_book:
        book = Book.objects.get(id = item.book_id)
        if book.title in user_books:
            user_books[book.title] += item.amount
        else:
            user_books[book.title] = item.amount

    return user_books



# Search
def get_similar_books(request):

    books = Book.objects.filter(title__icontains= str(request.data['title']))
    serializer = BookSerializer(books, many = True)
    return serializer.data

# 
def sell_user_order(request):

    user_id = required_permission(request, "BookShelve.change_userbasket")             #Check group permission

    ordered_books = UserBasket.objects.filter(user_id = user_id)

    user_order = {}
    for item in ordered_books:
        book = Book.objects.get(id = item.book_id)
        if book.title in user_order:
            user_order[book.title] += item.amount

        else:
            user_order[book.title] = item.amount

    UserBasket.objects.filter(user_id = user_id).delete()


    return user_order 

