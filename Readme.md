# CISC3003 Project 3 Name Entity Recognition
## Tips for running this project
### 1. Prerequisites
- Python 3.12 is **Mandatory!** Running in lower versions of Python, even in 3.11, may cause issues like 
`cannot import name 'LokyProcess'`. It is a thread-level issue which is probably caused by a version error and can't be fixed.
- PyCharm is the recommended IDE.
- All the packages installed, including `Django`, `nltk` should be the **latest**. The latest `Django` package should be 5.0.4.

### 2. Packages
&emsp; Now, under python environment 3.12, make sure you installed `Django` package for the backend, 
along with other packages, including: 

- `geonamescache`, for country and city names.
- `nltk`, for corpuses.
- `scikit-learn`, for MaxEnt modeling.

&emsp; If you still have some missing packages, you will be informed which one is missing as soon as you start the server
and you can simply add it using either `pip`, PyCharm Package manager, or 
`nltk.download('corporaname')`, for those missing `ntlk` corporas.

### 3. Run the server
&emsp; Now, if you are quite sure you have no packages left, please `cd name_entity_server` (First one) in console, and run `python -m manage runserver`. If you meet an error, try one of the following.

- `python manage.py runserver`
- `python manage runserver`

&emsp; In fact, you can just follow the indication of the error in the console. It is most likely caused by the PATH in 
your computer, if you use Windows. Here are some tips for running the server.
- As soon as you start the server, the required corporas will be automatically downloaded in
[\_\_init\_\_.py](./name_entity_server/NER_app/__init__.py).
- The console may just remained stucked after you run `python -m manage runserver` without any indications. This is because that 
[\_\_init\_\_.py](./name_entity_server/NER_app/__init__.py) is trying to download the corporas, and the internet was not good
so the downloading process is hanged. In that case, if you are sure that there's no need to download the corporas, please 
adjust `DO_NLTK_DOWNLOAD` to `False` in [\_\_init\_\_.py](./name_entity_server/NER_app/__init__.py).

- If you use Mac computers, you're not recommended to perform `nltk.download()` manually since you may face an SSL 
certificate error. In [\_\_init\_\_.py](./name_entity_server/NER_app/__init__.py), the issue is resolved by exceptions catching. 
If you have to download it manually, please make sure that no SSL errors would occur in your environment. For more 
information, please visit this issue https://github.com/python/cpython/issues/73666.

### 4. Use the webpage
&emsp; If the server is successfully started, you will see this
```console
    Django version 5.0.4, using settings 'name_entity_server.settings'
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CTRL-BREAK.
```
Click on the link to the `localhost` or `127.0.0.1` and it will direct you to the webpage. Quit server with CTRL + C, if
you don't have any custom keyboard interrupts.

## Inspect this project
&emsp; Due to the file layout requirements of `Django`, here are some modifications in the file layouts. Below is the
project directory tree and the indications of what is where.
```console
CISC3025-Name-Entity/
|- name_entity_server/          --> Server directory                                           
   |- name_entity_server/       --> Default app of this server                     
   |- NER_app/                  --> Custom app of server, in this case, the NER app
      |- migrations/                                                               
      |- NER/                   --> Project Main Directory, i.e. from moodle download                              
         |- data                                                                   
         |- __init__.py         --> For pre-downloading nltk corporas              
         |- MEM.py              --> MaxEnt Model                                   
         |- playground.py       --> Prediction function, connect model with backend
         |- run.py                                                                 
      |- templates/                                                                
         |- nerUI.html          --> Webpage UI                                     
      |- __init__.py                                                               
      |- views.py               --> Defines the JSON response of backend           
   |- __init__.py                                                                  
   |- manage.py                 --> To start server                                
```
1. The core project file `NER` lies in this directory [CISC3025-Name-Entity/name_entity_server/NER_app/NER](./name_entity_server/NER_app/NER)
2. The model `.pkl` file is dumped into a different place: [CISC3025-Name-Entity/name_entity_server/name_entity_server/static](./name_entity_server/name_entity_server/static)
3. The Web Page `HTML` lies in this directory [CISC3025-Name-Entity/name_entity_server/NER_app/templates/nerUI.html](./name_entity_server/NER_app/templates/nerUI.html)