from BookShelve.Services import book_service
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser


class BooksView(APIView): 
    '''
    Get all books
    required none 
    for all users
    '''

    permission_classes = (AllowAny, )

    def get(self, request = None):
        books = book_service.get_all_books()
        return Response(  books , status = 200 )


class GetSingleBookView(APIView): 
    ''' Get single book
        required book_id
        for all users 
        '''
    permission_classes = (AllowAny,) 
    def get (self, request ):
        book = book_service.get_book(request)
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
        except Exception as e:
            return Response(e, status = 500)

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
        except Exception as e:
            return Response(str(e) ,status = 500)

        return Response(ordered_books, status = 200)

     def post(self, request):
        '''
        add book to user basket
        required  book_id, amount
        for clients
        '''
        try:
            book_service.choose_book(request)
        except Exception as e:
            return Response(str(e), status = 500)


        return Response("Books were added to your basket", status = 201)

     def delete(self, request):
        '''
        delete book from your basket
        required  book_id
        for clients
        '''
        try:
            book_service.delete_book(request)
        except Exception as e:
            return Response(str(e), status = 500)

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
        except Exception as e:
            return Response(str(e),status = 400)

        return Response( books, status = 200)


class MakeOrderView(APIView):
    '''
        sell books have been choosen by user
        for client
    '''
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        
        user_order = book_service.sell_user_order(request)

        return Response(user_order, status = 200)
