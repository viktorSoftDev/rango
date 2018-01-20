from django.shortcuts import render
from django.http import HttpResponse

def index(request):
##### Keeping these comments as a note to myself what's going on..
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}

    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier
    # Note that teh first parameter is the template we wish to use
    return render(request, 'rango/index.html', context=context_dict)


def about(request):
    context_dict = {'mymessage': "This tutorial has been put together by Viktor Eriksson"}
    return render(request, 'rango/about.html', context=context_dict)
