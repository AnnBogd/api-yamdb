from django.views.generic import TemplateView


class SignupPageView(TemplateView):
    """Отображает страницу самостоятельной регистрации."""

    template_name = 'signup.html'
