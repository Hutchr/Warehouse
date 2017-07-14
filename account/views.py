from django.shortcuts import render
from django.contrib import auth
from django.template.context_processors  import csrf
from django.shortcuts import HttpResponse, HttpResponseRedirect, redirect
from .forms import *


# Create your views here.

def log_in(request):
    next = request.GET.get('next')
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user:
            log_in(request,user)
            if next:
                return redirect('next')
            else:
                return HttpResponseRedirect('/')


    context={
        'form':form,
    }
    context.update(csrf(request))
    return render(request, 'log_in.html', context)



def create_user(request):
    username = request.POST['username']
    password= request.POST['password']
    email =request.POST['email']
    user_auth = auth.authenticate(username=username,password=password)
    if user_auth is not None:
        auth.login(request,user_auth)
        return HttpResponseRedirect(request,'logged_in.html')
    else:
        return render(request,'invalid_log.html')



def auth_view(request):
    username = request.POST['username']
    password= request.POST['password']

    user = auth.authenticate(username=username,password=password)
    if user:
        auth.login(request,user)
        return HttpResponseRedirect('/accounts/logged_in/')
    else:
        return render(request,'invalid_log.html')

def logged_in(request):
    context = {
        'full_name':request.user.username
    }
    return render(request,'logged_in.html',context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



