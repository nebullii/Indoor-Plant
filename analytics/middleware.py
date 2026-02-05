from django.db import connection
from django.db.utils import OperationalError, ProgrammingError
from .models import SiteVisit
from .models import PageView

class LogSiteVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key

            if not SiteVisit.objects.filter(session_key=session_key).exists():
                SiteVisit.objects.create(
                    session_key=session_key,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
        except (OperationalError, ProgrammingError):
            # Tables don't exist yet - skip analytics during initial deployment
            pass
        return self.get_response(request)

class LogPageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key

            PageView.objects.create(
                session_key=session_key,
                path=request.path,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        except (OperationalError, ProgrammingError):
            # Tables don't exist yet - skip analytics during initial deployment
            pass
        return self.get_response(request) 