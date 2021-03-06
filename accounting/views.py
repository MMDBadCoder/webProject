import json
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from confirming.models import ConfirmRequest
from tokenManager.models import TokenManager
from following.models import Follow
from paging.models import Page
from searchengine.models import DocIndex
from .forms import SignUpForm
from .models import Account


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        q = User.objects.filter(username=username)

        if q.exists():
            user = q.get()
            if user.is_active:
                user = authenticate(request, username=username, password=password)
                if user:
                    login(request, user)
                    return redirect('homeservice:home')
                else:
                    errors = {
                        'password': 'incorrect password'
                    }
            else:
                errors = {
                    'authentication': 'check your email to activate your account!'
                }
        else:
            errors = {
                'invalid_user': "Invalid login details given"
            }
    else:
        errors = {}
    return render(request, 'accounting/login.html', {'errors': json.dumps(errors)})


def activate(request, username, code):
    token = TokenManager.objects.filter(username=username, code=code, type='activate').first()
    if token is not None:
        user = User.objects.filter(username=username).first()
        user.is_active = True
        user.save()

        account = Account(user=user)
        account.user = user
        account.name = str(user.username)
        account.save()

        personal_page = Page(personal_page=True, title=user.username + ' page', creator=account,
                             page_id=account.user.username)
        personal_page.save()
        personal_page.admins.add(account)
        personal_page.save()

        token.delete()

        DocIndex.add_doc(username, username, 'user')

        return render(request, 'accounting/activate_done.html')
    else:
        errors = {
            'token': 'invalid token code for activation'
        }
        return render(request, 'accounting/login.html', {'errors': json.dumps(errors)})


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            token = TokenManager.create_new_token(username=user.username, type='activate')
            token.save()
            data = {
                'user': user,
                'domain': current_site.domain,
                'token': token.code,
            }
            message = render_to_string('accounting/activation_page.html', data)
            print(message)
            text_content = strip_tags(message)
            to_email = form.cleaned_data.get('email')
            send_mail(mail_subject, text_content, 'joorabnakhi@gmail.com', [to_email])

            return render(request, 'accounting/activation_sent.html')
        else:
            return render(request, 'accounting/signup.html', {'form': form, 'errors': json.dumps(form.errors)})
    else:
        form = SignUpForm()
        return render(request, 'accounting/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/home')


def get_profile_page(request, owner):
    setting = request.user == owner
    followed = False
    if request.user.is_authenticated:
        if Follow.objects.filter(followed=owner.account, follower=request.user.account):
            followed = True
    followers = Follow.objects.filter(followed=owner.account)
    followings = Follow.objects.filter(follower=owner.account)
    page = Page.objects.filter(creator=owner.account, personal_page=True).get()
    can_view = page.can_view(request.user)
    is_owner = request.user == owner
    confirm_requests = []
    if is_owner:
        confirm_requests = ConfirmRequest.objects.filter(channel=page)
    data = {'owner': owner, 'setting': setting, 'followed': followed, 'followers': followers,
            'followings': followings, 'can_view': can_view, 'is_owner': is_owner, 'confirm_requests': confirm_requests}
    return render(request, 'accounting/profile.html', data)


@login_required
def my_profile(request):
    return get_profile_page(request, request.user)


def profile_view(request, username):
    owner = User.objects.filter(username=username).first()
    if owner:
        return get_profile_page(request, owner)
    else:
        return HttpResponse(status=404)


@login_required
def edit_profile(request):
    public = Page.objects.filter(creator=request.user.account, personal_page=True).get().public
    errors = []
    if request.POST:
        if request.FILES:
            try:
                request.user.account.profile_photo = request.FILES.get('profile_photo')
                request.user.account.save()
            except:
                errors.append('cant load image!')
        try:
            username = request.POST.get('username')
            name = request.POST.get('name')
            email = request.POST.get('email')
            location = request.POST.get('location')
            bio = request.POST.get('bio')
            public = str(request.POST.get('public')) == 'on'
        except:
            errors.append('bad format of data')
        if username:
            if str(request.user.username) != str(username):
                if User.objects.filter(username=username):
                    errors.append('this username is token by others ...')
                else:
                    page = Page.objects.get(page_id=request.user.username)
                    page.page_id = username
                    page.save()
                    request.user.username = username
                    request.user.save()

        if location and bio and email and name:
            account = request.user.account
            account.bio = bio
            request.user.email = email
            account.location = location
            account.name = name
            account.save()
            request.user.save()
            page = Page.objects.filter(creator=account, personal_page=True).get()
            page.public = public
            page.save()

        DocIndex.add_doc(bio, request.user.username, 'user')
        DocIndex.add_doc(name, request.user.username, 'user')
        DocIndex.add_doc(username, request.user.username, 'user')
        DocIndex.add_doc(location, request.user.username, 'user')

        request.user.save()
        request.user.account.save()
    return render(request, 'accounting/profile_edit.html', {'errors': json.dumps(errors), 'public': public})


def forget_password_view(request):
    if request.POST:
        username = request.POST.get('username')
        if not User.objects.filter(username=username).exists():
            return HttpResponse(status=404)
        user = User.objects.get(username=username)
        token = TokenManager.create_new_token(username, 'reset')
        token.save()
        mail_subject = 'forget password'
        text = 'http://localhost:8000/accounting/reset/' + token.code
        send_mail(mail_subject, text, 'joorabnakhi@gmail.com', [user.email])
        return redirect('accounting:login')
    return render(request, 'accounting/forgot_password.html')


def reset_password_view(request, code):
    if request.POST:
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if str(pass1) != str(pass2):
            return redirect('accounting:reset-password', code)
        if not TokenManager.objects.filter(code=code).exists():
            return HttpResponse(status=404)
        token = TokenManager.objects.get(code=code, type='reset')
        user = User.objects.filter(username='s').get()
        user.set_password(pass1)
        user.save()
        token.delete()
        return redirect('accounting:login')

    return render(request, 'accounting/reset_password.html', {'token': code})
