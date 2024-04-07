from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.staticfiles import finders

from .NER import MEM
from .NER import playground

def nerUI(request):
    return render(request, 'nerUI.html')


def resultView(request):
    input_query = request.POST.get("input-query", "<blank>")

    # Add your name entity processing here!!!

    # model_pkl_path = finders.find('static/model.pkl')
    # names = playground.predict(input_query, MEM)
    # output_query = names + " ---- from backend"

    output_query = input_query + " ---- from backend"
    return JsonResponse({"result": output_query})
