# CISC3003 Project 3 Name Entity Recognition
## Run this project
1. Make sure you installed Django package
2. Please `cd name_entity_server`, and run `python -m manage.py runserver`
3. You will see this
```console
    Django version 5.0.4, using settings 'name_entity_server.settings'
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CTRL-BREAK.
```
4. Click on the link and it will direct you to the webpage.

## View this project
&emsp; Due to the file layout requirements of `Django`, here are some modifications where the files lie.
1. The core project file `NER` lies in this directory [CISC3025-Name-Entity/name_entity_server/NER_app/NER](./name_entity_server/NER_app/NER)
2. The model `.pkl` file is dumped into a different place: [CISC3025-Name-Entity/name_entity_server/name_entity_server/static](./name_entity_server/name_entity_server/static)