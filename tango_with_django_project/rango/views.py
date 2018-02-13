from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime


def show_category(request, category_name_slug):

    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context_dict)

def index(request):

##### Keeping these comments as a note to myself what's going on..
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    category_list = Category.objects.order_by('-likes')[:5]

    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list,
                    'pages': page_list}

    response = render(request, 'rango/index.html',context_dict)
    visitor_cookie_handler(request, response)
    return response




    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier
    # Note that teh first parameter is the template we wish to use
    return render(request, 'rango/index.html', context=context_dict)

def visitor_cookie_handler(request, response):
    visits_cookie = int(request.COOKIES.get('visits', '1'))

    last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).days > 0:
        visits = visits_cookie + 1
        return visits
        resoponse.set_cookie('last_visit', str(datetime.now()))
    else:
        response.set_cookie('last_visit', last_visit_cookie)

    response.set_cookie('visits', visits)
    return response



def about(request):
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED")
        request.session.delete_test_cookie()
    context_dict = {'mymessage': "This tutorial has been put together by Viktor Eriksson"}
    return render(request, 'rango/about.html', context=context_dict)

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print("Invalid login details: {0}, {1}").format(username, password)
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html', {})

def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

                profile.save()

                registered = True

            else:
                print(user_form.errors, profile_form.errors)
    else:
            user_form = UserForm()
            profile_form = UserProfileForm()

    return render(request, 'rango/register.html',
                    {'user_form': user_form,
                    'profile_form': profile_form,
                    'registered': registered})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)
    context_dict = {'form':form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)

@login_required
def add_category(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
