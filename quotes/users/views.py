from django.contrib import messages
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse_lazy

from .forms import RegisterForm


# Create your views here.
class RegisterView(View):
    form_class = RegisterForm
    template_name = "users/signup.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(to="quoteapp:main")
        return super(RegisterView, self).dispatch(request, * args, ** kwargs)

    def get(self, request):
        return render(request, self.template_name, {"form": self.form_class})

    def post(self, request):
        form = self.form_class(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            messages.success(request, f'Congratulations {username}! Your account has been successfully created.')
            return redirect(to="users:login")  # ? signin

        return render(request, self.template_name, {"form": form})


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    """Клас-представлення для скидання паролю користувача Django. 
    Він наслідується від PasswordResetView з django.contrib.auth.views 
    та SuccessMessageMixin з django.contrib.messages.views.
    Клас SuccessMessageMixin надає можливість показувати повідомлення про успішне виконання 
    дії в користувацькому інтерфейсі. Клас PasswordResetView є класом-представленням, 
    який вже реалізує функціональність скидання паролю.
    """
    # ім’я шаблону, який буде використовуватися для сторінки скидання паролю
    template_name = 'users/password_reset.html'

    # ім’я шаблону, який буде використовуватися для листа про скидання паролю
    email_template_name = 'users/password_reset_email.html'

    # ім’я шаблону, який буде використовуватися для HTML-версії листа про скидання паролю
    html_email_template_name = 'users/password_reset_email.html'

    # URL-адреса для перенаправлення після успішного надсилання листа про скидання паролю
    success_url = reverse_lazy('users:password_reset_done')

    # повідомлення, яке буде показано користувачеві після успішного надсилання листа про скидання паролю
    success_message = "An email with instructions to reset your password has been sent to %(email)s."

    # ім’я шаблону, який буде використовуватися для теми листа про скидання паролю
    subject_template_name = 'users/password_reset_subject.txt'
