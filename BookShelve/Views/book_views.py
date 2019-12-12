from BookShelve.Services import book_service
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

# +
class BooksView(APIView): ## See book catalog for all users

    permission_classes = (AllowAny, )

    def get(self, request = None):
        books = book_service.get_all_books()
        return Response( {"books" : books} )


class GetSingleBookView(APIView): 

    permission_classes = (AllowAny,) 
    def get (self, request ):
        book = book_service.get_book(request.data)
        return Response( {"singlebook" : book} )


class AddBookView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            message = book_service.add_book(request)
        except Exception as e:
            return Response(e)

        return Response(message)


class ChangeBookView(APIView): 
     permission_classes = (IsAuthenticated,)

     def post(self, request):
        try:
            book_service.change_books(request)
        except Exception as e:
            return Response(e)


        return Response("Books were added to your basket")


class SearchSimilarBooksView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        
        try:
            books = book_service.get_similar_books(request)
        except Exception as e:
            print(e)
            return Response("error")

        return Response({"books": books})