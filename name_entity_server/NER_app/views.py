from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.staticfiles import finders

import os
from .NER import MEM
from .NER import playground
# from name_entity_server import settings


def nerUI(request):
    return render(request, 'nerUI.html')


def resultView(request):
    input_query = request.POST.get("input-query", "<blank>")

    # Add your name entity processing here!!!
    # Please never alter the path!!!!!
    model_pkl_path = os.path.abspath('name_entity_server/static/model.pkl').replace('\\', '/')

    names = playground.predict(input_query, MEM, model_pkl_path)
    output_query = names + " ---- from backend"

    # output_query = input_query + " ---- from backend"
    return JsonResponse({"result": output_query})
