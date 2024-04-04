from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from .NER import playground


def nerUI(request):
    return render(request, 'nerUI.html')


def resultView(request):
    input_query = request.POST.get("input-query", "<blank>")

    # Add your name entity processing here!!!
    output_query = input_query

    return JsonResponse({"result": output_query})
