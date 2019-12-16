from BookShelve.Services import book_service
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from BookShelve.exceptions import *

class BooksView(APIView): 
    '''
    Get all books
    required none 
    for all users
    '''

    permission_classes = (AllowAny, )

    def get(self, request = None):
        try:
            books = book_service.get_all_books()
        except NotExist:
            return Response("Have not at now",status = 404)
        return Response(  books , status = 200 )


class GetSingleBookView(APIView): 
    ''' Get single book
        required book_id
        for all users 
        '''
    permission_classes = (AllowAny,) 
    def get (self, request ):
        try:
            book = book_service.get_book(request)
        except NotExist:
            return Response("Book does not exist", status = 404)
        except ValueError:
            return Response("wrong format of input data", status = 400)
        return Response(  book , status = 200 )

 
class AddBookView(APIView):
    '''
    Add book to library
    required all info about book which is stored in storage
    for managers and admins users
    '''

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            message = book_service.add_book(request)
        except NotEnought as e:
            return Response("Not enought books in the storage", status = 400)

        return Response(message , status = 201)


class UserBasketView(APIView): 
     

     permission_classes = (IsAuthenticated,)

     def get(self, request):
        '''
        get books from user basket
        required  none
        for clients
        '''
        try:
            ordered_books = book_service.get_ordered_books(request)
        except EmailIsExist:
            return Response("access is denied " ,status = 405)

        return Response(ordered_books, status = 200)

     def post(self, request):
        '''
        add book to user basket
        required  book_id, amount
        for clients
        '''
        try:
            book_service.choose_book(request)
        except NotExist:
            return Response("Not have such book", status = 404)
        except NotEnought:
            return Response("Not enought books on storage", status = 403)



        return Response("Books were added to your basket", status = 201)

     def delete(self, request):
        '''
        delete book from your basket
        required  book_id
        for clients
        '''
        try:
            book_service.delete_book(request)
        except EmailIsExist:
            return Response("error", status = 500)

        return Response("Book was delete from your basket", status = 200)


class SearchSimilarBooksView(APIView):
    '''
        search book by a title
        required title
        for all users
    '''

    permission_classes = (AllowAny,)

    def get(self, request):
        
        try:
            books = book_service.get_similar_books(request)
        except NotFound:
            return Response("No book in the storage",status = 404)

        return Response( books, status = 200)


class MakeOrderView(APIView):
    '''
        sell books have been choosen by user
        for client
    '''
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            user_order = book_service.sell_user_order(request)
        except NotFound:
            return Response("Basket is empty ", status = 404)
        return Response(user_order, status = 200)


class BookCoverView(APIView):

    def get(self,request):
        pass

    def post(self, request):
        pass