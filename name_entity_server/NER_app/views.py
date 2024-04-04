from django.shortcuts import render
from django.http import HttpResponse
from .NER import playground


def nerUI(request):
    return render(request, 'nerUI.html')


def resultView(request):
    input_query = request.POST.get("input-query", "<blank>")

    # Add your name entity processing here!!!
    output_query = input_query + playground.foo()

    return HttpResponse("Your Result:\n" + output_query)