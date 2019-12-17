from BookShelve.Services import book_service
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from BookShelve.check_permission import required_permission
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
            book_id = int(request.data['book_id'])
            book = book_service.get_book(book_id)
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
            required_permission(request, "BookShelve.add_book")                             ## Check group permission
            message = book_service.add_book(request.data)
        except NotEnought :
            return Response("Not enought books in the storage", status = 400)
        except KeyError as e:
            return Response("Argument not provide {}".format(str(e)))

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
            user_id = required_permission(request, "BookShelve.view_userbasket")
            ordered_books = book_service.get_ordered_books(user_id)
        except Empty:
            return Response("User basket is empty" ,status = 405)

        return Response(ordered_books, status = 200)

     def post(self, request):
        '''
        add book to user basket
        required  book_id, amount
        for clients
        '''
        try:
            user_id = required_permission(request, "BookShelve.add_userbasket")                      ## Check group permission
            book_service.choose_book(user_id, request.data)
        except NotExist:
            return Response("Not have such book", status = 404)
        except NotEnought:
            return Response("Not enought books on storage", status = 403)
        except KeyError as e :
            return Response("Arguments not provided or wrong {}".format(str(e)), status = 400)

        return Response("Books were added to your basket", status = 201)

     def delete(self, request):
        '''
        delete book from your basket
        required  book_id
        for clients
        '''
        try:
            user_id = required_permission(request, "BookShelve.delete_userbasket")
            book_service.delete_book(user_id, int(request.data['book_id']))
        except KeyError as e :
            return Response("were not provided  {}".format(str(e)), status = 400)
        except ValueError:
            return Response("invalid arguments", status = 400)
        except NotFound:
            return Response("User basket is empty or this book is not in user basket", status = 400)

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
            title = request.data['title']
            books = book_service.get_similar_books(title)
        except NotFound:
            return Response("No book in this request",status = 404)
        except KeyError as e:
            return Response("Argument not provide {}".format(str(e)), status = 400)

        return Response( books, status = 200)


class MakeOrderView(APIView):
    '''
        sell books have been choosen by user
        for client
    '''
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            user_id = required_permission(request, "BookShelve.change_userbasket")             #Check group permission
            user_order = book_service.sell_user_order(user_id)
        except Empty:
            return Response("Basket is empty ", status = 404)
        return Response(user_order, status = 200)


class BookCoverView(APIView):

    def get(self,request):
        pass

    def post(self, request):
        pass