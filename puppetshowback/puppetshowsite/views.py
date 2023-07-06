from django.views import View
from django.shortcuts import redirect
from . import settings


class RedirectToMainPageView(View):
    def get(self, request):
        return redirect(settings.FRONTEND)
