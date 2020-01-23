from BookShelve.Services import book_service
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from BookShelve.check_permission import required_permission,check_group_permission
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from BookShelve.exceptions import *
from BookShelve.Services import token_service
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import OperationalError

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
        return Response( {"books" : books} , status = 200 )


class GetSingleBookView(APIView): 
    ''' Get single book
        required parametr book_id
        for all users 
        '''
    permission_classes = (AllowAny,) 

    def get(self, request ):
        try:
            book_id = int(request.GET.get("id","not receive argument"))
            book = book_service.get_book(book_id)
        except NotExist:
            return Response("Book does not exist", status = 404)
        except ValueError:
            return Response("wrong format of input data", status = 400)
        except KeyError as e:
            return Response("argument not provided {}".format(str(e)), status = 400)
        return Response({"book": book} , status = 200 )

 
class AddBookView(APIView):
    '''
    Add book to library
    required all info about book which is stored in storage
    for managers and admins users
    '''

    permission_classes = (IsAuthenticated,)

    @check_group_permission("BookShelve.add_book")
    def post(self, request):
        try:
            #required_permission(request, "BookShelve.add_book")                             ## Check group permission
            message = book_service.add_book(request.data)
        except NotEnought :
            return Response("Not enought books in the storage", status = 400)
        except KeyError as e:
            return Response("Argument not provide {}".format(str(e)),status = 400)

        return Response(message , status = 201)


class UserBasketView(APIView): 
     

     permission_classes = (IsAuthenticated,)

     @check_group_permission("BookShelve.view_userbasket")
     def get(self, request):
        '''
        get books from user basket
        required  none
        for clients
        '''
        try:
            #user_id = required_permission(request, "BookShelve.view_userbasket")
            token_info = token_service.DecodeToken(request.META['HTTP_AUTHORIZATION'][8:-1])
            ordered_books = book_service.get_ordered_books(token_info['user_id'])
        except Empty:
            return Response("User basket is empty" ,status = 405)

        return Response({"books":ordered_books} , status = 200)

     @check_group_permission("BookShelve.add_userbasket")
     def post(self, request):
        '''
        add book to user basket
        required  book_id, amount
        for clients
        '''
        try:
            #user_id = required_permission(request, "BookShelve.add_userbasket")                      ## Check group permission
            token_info = token_service.DecodeToken(request.META['HTTP_AUTHORIZATION'][8:-1])
            book_service.choose_book(token_info['user_id'], request.data)
        except ObjectDoesNotExist:
            return Response("Not have such book", status = 404)
        except NotEnought:
            return Response("Not enought books on storage", status = 403)
        except KeyError as e :
            return Response("Arguments not provided or wrong {}".format(str(e)), status = 400)

        return Response("Books were added to your basket", status = 201)
     
     @check_group_permission("BookShelve.delete_userbasket")
     def delete(self, request):
        '''
        delete book from your basket
        required  book_id
        for clients
        '''
        try:
            #user_id = required_permission(request, "BookShelve.delete_userbasket")
            token_info = token_service.DecodeToken(request.META['HTTP_AUTHORIZATION'][8:-1])
            book_service.delete_book(token_info['user_id'], int(request.data['book_id']))
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

    def post(self, request):
        
        try:
            title = request.data["title"]
            books = book_service.get_similar_books(title)
        except NotFound:
            return Response("No book in this request",status = 404)
        except KeyError as e:
            return Response("Argument not provide {}".format(str(e)), status = 400)
        except OperationalError:
            return Response("Not supporting language", status = 400)
        return Response( {"books" : books}, status = 200)


class MakeOrderView(APIView):
    '''
        sell books have been choosen by user
        for client
    '''
    permission_classes = (IsAuthenticated,)

    @check_group_permission("BookShelve.change_userbasket")
    def post(self, request):
        try:
            # user_id = required_permission(request, "BookShelve.change_userbasket")             #Check group permission
            #token_info = token_service.DecodeToken(request.META['HTTP_AUTHORIZATION'][8:-1])
            #user_order = book_service.sell_user_order(token_info['user_id'])
            book_service.sell_user_order(request.data['books'])
        except Empty:
            return Response("Basket is empty ", status = 404)
        except NotEnought:
            return Response("Not have such books", status = 400)
        return Response("success", status = 200)


class BookCoverView(APIView):

    def get(self,request):
        pass

    def post(self, request):
        pass