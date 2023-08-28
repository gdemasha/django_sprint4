from django.shortcuts import render
from django.views.generic import TemplateView


class About(TemplateView):
    """CBV для страницы 'О проекте'."""
    template_name = 'pages/about.html'


class Rules(TemplateView):
    """CBV для страницы 'Наши правила'."""
    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """Кастомная страница для ошибки 404."""
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Кастомная страница для ошибки 500."""
    return render(request, 'pages/500.html', status=500)


def csrf_failure(request, reason=''):
    """Кастомная страница для ошибки 403."""
    return render(request, 'pages/403csrf.html', status=403)
