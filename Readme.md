# CISC3003 Project 3 Name Entity Recognition
## Tips for running this project
1. Python 3.12 is **Mandatory!** Running in lower versions of Python, even in 3.11, may cause issues like `cannot import name 'LokyProcess'`. It is a thread-level issue which is probably caused by a version error and can't be fixed.

2. Now, under python environment 3.12, make sure you installed `Django` package for the backend, along with other packages, including: 

- `nltk` corporas including `names`, `stopwords`, etc.
- `pycountry`, for country names
- `geonamescache`, for country and city names
- `scikit-learn`

There might be more dependent packages. When you start the server (I will illustrate below how to start a server), you will be informed which one is missing and you can simply add it using either `pip`, PyCharm Package manager, or `nltk.download('corporaname')`, for those missing `ntlk` corporas.

3. Now, if you are quite sure you have no packages left, please `cd name_entity_server` in console, and run `python -m manage.py runserver`. If you meet an error, try one of the following.

- `python -m manage runserver`
- `python manage.py runserver`
- `python manage runserver`

&emsp; In fact, you can just follow the indication of the error in the console. It is most likely caused by the PATH in your computer, if you use Windows.

5. If the server is successfully started, you will see this
```console
    Django version 5.0.4, using settings 'name_entity_server.settings'
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CTRL-BREAK.
```
Click on the link and it will direct you to the webpage. Quite server with CTRL + C.

## View this project
&emsp; Due to the file layout requirements of `Django`, here are some modifications where the files lie.
1. The core project file `NER` lies in this directory [CISC3025-Name-Entity/name_entity_server/NER_app/NER](./name_entity_server/NER_app/NER)
2. The model `.pkl` file is dumped into a different place: [CISC3025-Name-Entity/name_entity_server/name_entity_server/static](./name_entity_server/name_entity_server/static)
3. The Web Page `HTML` lies in this directory [CISC3025-Name-Entity/name_entity_server/NER_app/templates/nerUI.html](./name_entity_server/NER_app/templates/nerUI.html)