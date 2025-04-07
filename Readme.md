# LLM_Projet 

Ce projet est une application basée sur FastAPI et React qui permet d'interagir avec un modèle de langage (LLM) et de gérer des documents dans une base de données vectorielle (ChromaDB).

## Créer un fichier .env 
Le fichier .env est utilisé pour configurer les variables d'environnement nécessaires à l'application. Voici un exemple de contenu pour le fichier .env :

### MongoDB
```bash
MONGO_URI=mongodb://mongodb:27017
MONGO_DB_NAME=llm_project
MONGO_COLLECTION_NAME=documents
```
### OpenAI API Key
```bash
OPENAI_API_KEY=your_openai_api_key
```

### ChromaDB Path
```bash
CHROMA_PATH=./chroma_db
```
- MONGO_URI : L'URI de connexion à MongoDB.
- MONGO_DB_NAME : Le nom de la base de données MongoDB.
- MONGO_COLLECTION_NAME : Le nom de la collection MongoDB.
- OPENAI_API_KEY : Votre clé API OpenAI pour interagir avec le modèle GPT.
- CHROMA_PATH : Le chemin où les données de ChromaDB seront stockées.

## Lancer l'application
Utilisez la commande suivante pour démarrer les conteneurs Docker :
```bash
docker-compose up --build
```
Une fois les conteneurs démarrés, les services seront accessibles :

- Frontend : http://localhost:3000
- Swagger (documentation API) : http://localhost:8000/docs

PS : Le lancement de l'image du backend au début peut prendre du temps
PS : Il faut ajouter les document car la base de donnee chromadb est en local (gratuit, voir plus sur le rapport) sinon le chat ne marchera pas

## Ajouter des données dans ChromaDB
-  Ajouter un fichier unique
    - soit en utilisant swagger : 
        Vous pouvez ajouter un fichier unique à ChromaDB en utilisant l'endpoint /api/chroma/upload_document/

    - soit en utiliser le curl avec le terminal : 
        '''bash
            curl -X POST "http://127.0.0.1:8000/api/chroma/upload_document/" \
            -F "file=@/Users/I753051/Documents/LLM_BTP/file_path"
     '''

-  Ajouter un dossier complet
Pour ajouter tous les fichiers d'un dossier, utilisez l'endpoint /api/chroma/upload_folder/

#### Remarque si vous voulez ajouter un document ".doc" il faut decommenter la dependence pywin32 (sans docker). 

## Structure du Projet
- Backend : Situé dans le dossier app/, il contient les endpoints FastAPI et les services.
- Frontend : Situé dans le dossier frontend/, il contient l'application React.
- ChromaDB : Les données vectorielles sont stockées dans le dossier chroma_db/.

## Installation environnement via github (sans docker) :

Dans le LLM_projet : 
```bash
    python -m venv envllm 
    envllm\Scripts\activate
    pip install -r requirements.txt
```
lancer le Backend : 
```bash
    uvicorn app.main:app --reload
```
lancer le front : 
```bash
    # Aller sur le dossier frontend  et faite la commande suivante 
    npm start
```
swagger :
``` bash 
    http://127.0.0.1:8000/docs