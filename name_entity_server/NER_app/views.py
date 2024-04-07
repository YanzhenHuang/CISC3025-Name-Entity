from django.shortcuts import render
from django.http import JsonResponse

import os
from .NER import MEM
from .NER import playground


def nerUI(request):
    return render(request, 'nerUI.html')


def resultView(request):
    input_query = request.POST.get("input-query", "<blank>")

    # Add your name entity processing here!!!
    # Please never alter the path!!!!!
    model_pkl_path = os.path.abspath('name_entity_server/static/model_s.pkl').replace('\\', '/')

    # Get modified name string
    names, labels = playground.predict(input_query, MEM, model_pkl_path)
    output_query = names + " <br> " + labels

    # output_query = input_query + " ---- from backend"
    return JsonResponse({"result": output_query})
