import book_store.forms
import account.forms
import account.views

class LoginView(account.views.LoginView):
    form_class = account.forms.LoginEmailForm

class SignupView(account.views.SignupView):

    form_class =  book_store.forms.SignupForm

    def generate_username(self, form):
        username = form.cleaned_data["email"]
        return username

    def after_signup(self, form):
        # do something
        super(SignupView, self).after_signup(form)