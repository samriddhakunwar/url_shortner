"""
frontend/views.py
-----------------
Simple TemplateView subclasses for each frontend page.
All data is fetched client-side via JavaScript calls to the DRF API.
No server-side authentication is enforced here — auth is handled
by JWT tokens stored in the browser (checked in JavaScript on load).
"""

from django.views.generic import TemplateView


class LoginPageView(TemplateView):
    """Renders the login form page."""
    template_name = 'frontend/login.html'


class RegisterPageView(TemplateView):
    """Renders the user registration form page."""
    template_name = 'frontend/register.html'


class DashboardView(TemplateView):
    """Renders the main dashboard with stats and recent URLs."""
    template_name = 'frontend/dashboard.html'


class CreateURLView(TemplateView):
    """Renders the create short URL form page."""
    template_name = 'frontend/create_url.html'


class URLListView(TemplateView):
    """Renders the full URL management table page."""
    template_name = 'frontend/url_list.html'


class EditURLView(TemplateView):
    """Renders the edit URL form page. The URL ID is passed via JS from the URL path."""
    template_name = 'frontend/edit_url.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the PK to the template so JS can fetch the right URL
        context['url_id'] = kwargs.get('pk')
        return context


class AnalyticsView(TemplateView):
    """Renders the analytics overview page."""
    template_name = 'frontend/analytics.html'
