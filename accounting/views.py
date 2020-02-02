import json

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from paging.models import Page
from .forms import SignUpForm
from .models import Token, create_new_token, Account


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.objects.filter(username=username).first()

        if user is not None:
            if user.is_active:
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return render(request, 'home.html')
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
    token = Token.objects.filter(username=username, code=code).first()
    if token is not None:
        user = User.objects.filter(username=username).first()
        user.is_active = True
        user.save()

        account = Account(user=user)
        account.user = user
        account.save()

        personal_page = Page(personal_page=True, title=user.username + ' page', creator=account,
                             id=account.user.username)
        personal_page.save()

        token.delete()
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
            token = create_new_token(username=user.username)
            token.save()
            data = {
                'user': user,
                'domain': current_site.domain,
                'token': token.code,
            }
            message = render_to_string('accounting/activation_page.html', data)
            text_content = strip_tags(message)
            to_email = form.cleaned_data.get('email')
            # send_mail(mail_subject, text_content, 'joorabnakhi@gmail.com', [to_email])
            return render(request, 'accounting/activation_page.html', data)

        else:
            return render(request, 'accounting/signup.html', {'form': form, 'errors': json.dumps(form.errors)})
    else:
        form = SignUpForm()
        return render(request, 'accounting/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


def edit_view(request):
    return render(request, 'accounting/edit2.html')
