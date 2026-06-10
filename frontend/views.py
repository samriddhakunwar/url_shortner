from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from shortener.models import ShortURL
from shortener.services import create_short_url

from .forms import CreateURLForm, EditURLForm, LoginForm, RegisterForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('frontend:dashboard')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
        )
        if user:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'frontend/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('frontend:dashboard')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Account created. You can log in now.")
        return redirect('frontend:login')

    return render(request, 'frontend/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('frontend:login')


@login_required
def dashboard(request):
    urls = ShortURL.objects.filter(user=request.user)
    total = urls.count()
    total_clicks = sum(u.click_count for u in urls)
    active = sum(1 for u in urls if not u.is_expired)
    expired = total - active
    recent = urls[:5]

    # top performing link
    top = urls.order_by('-click_count').first()

    return render(request, 'frontend/dashboard.html', {
        'total': total,
        'total_clicks': total_clicks,
        'active': active,
        'expired': expired,
        'recent': recent,
        'top': top,
    })


@login_required
def create_url(request):
    form = CreateURLForm(request.POST or None)
    created = None

    if request.method == 'POST' and form.is_valid():
        try:
            obj = create_short_url(
                user=request.user,
                original_url=form.cleaned_data['original_url'],
                custom_alias=form.cleaned_data.get('custom_alias') or None,
                expires_at=form.cleaned_data.get('expires_at'),
            )
            created = obj
            messages.success(request, "Short URL created.")
            form = CreateURLForm()  # reset form
        except ValueError as e:
            messages.error(request, str(e))

    return render(request, 'frontend/create_url.html', {
        'form': form,
        'created': created,
    })


@login_required
def url_list(request):
    urls = ShortURL.objects.filter(user=request.user)
    return render(request, 'frontend/url_list.html', {'urls': urls})


@login_required
def edit_url(request, pk):
    obj = get_object_or_404(ShortURL, pk=pk, user=request.user)

    if request.method == 'POST':
        form = EditURLForm(request.POST)
        if form.is_valid():
            obj.original_url = form.cleaned_data['original_url']
            obj.expires_at = form.cleaned_data.get('expires_at')
            obj.save()
            messages.success(request, "URL updated.")
            return redirect('frontend:url_list')
    else:
        initial = {
            'original_url': obj.original_url,
            'expires_at': obj.expires_at,
        }
        form = EditURLForm(initial=initial)

    return render(request, 'frontend/edit_url.html', {
        'form': form,
        'obj': obj,
    })


@login_required
def delete_url(request, pk):
    obj = get_object_or_404(ShortURL, pk=pk, user=request.user)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "URL deleted.")
    return redirect('frontend:url_list')


@login_required
def analytics(request):
    urls = ShortURL.objects.filter(user=request.user).order_by('-click_count')
    total_clicks = sum(u.click_count for u in urls)
    active = sum(1 for u in urls if not u.is_expired)
    best = urls.first()

    return render(request, 'frontend/analytics.html', {
        'urls': urls,
        'total_clicks': total_clicks,
        'total_urls': urls.count(),
        'active_count': active,
        'best_clicks': best.click_count if best else 0,
    })
