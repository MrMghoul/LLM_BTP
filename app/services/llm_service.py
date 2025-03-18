import os
import logging
from langchain_openai import ChatOpenAI, OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('punkt')

# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger la clé API OpenAI depuis les variables d'environnement
openai_api_key = os.getenv("OPENAI_API_KEY")

MAX_HISTORY_LENGTH = 100

# Initialiser le modèle OpenAI
llm = ChatOpenAI(
    temperature=0.7,
    model_name="gpt-3.5-turbo",
    api_key=openai_api_key)

def remove_stopwords(text):
    stop_words = set(stopwords.words('french'))
    word_tokens = word_tokenize(text)
    filtered_tokens = [word for word in word_tokens if word.lower() not in stop_words]
    return filtered_tokens

async def ask_question(query: str, history: str) -> str:
    """
    Pose une question au LLM et obtient une réponse.
    
    :param query: La question à poser.
    :return: La réponse générée par le LLM.
    """
    # Créer les messages avec un message système initial
    messages = [
        SystemMessage(content="Vous êtes un assistant utile et concis."),
        SystemMessage(content=history),
        HumanMessage(content=query)
    ]
    
    # Loguer la requête envoyée au LLM
    logger.info(f"Envoyer au LLM: {messages}")
    
    # Générer la réponse
    response = await llm.agenerate([messages])
    response_text = response.generations[0][0].text
    
    # Loguer la réponse reçue du LLM
    logger.info(f"Réponse du LLM: {response_text}")
    
    return response_text

async def summarize_history(history: str) -> str:
    """
    Génère un résumé de l'historique pour réduire sa taille.
    
    :param history: L'historique des messages précédents.
    :return: Un résumé de l'historique.
    """
    messages = [
        SystemMessage(content="Vous êtes un assistant qui résume des textes en gardant les information les plus importante."),
        HumanMessage(content=f"Résumé cet historique: {history}")
    ]
    
    logger.info(f"Envoyer au LLM pour résumé: {messages}")
    
    response = await llm.agenerate([messages])
    summary = response.generations[0][0].text
    
    logger.info(f"Résumé de l'historique: {summary}")
    
    return summary

async def generate_response(query: str, documents: list, history: str, folder_chunks: list) -> str:
    """
    Génère une réponse à partir du LLM en utilisant la requête, les documents fournis et les chunks de fichier.
    
    :param query: La requête de l'utilisateur.
    :param documents: Les documents à utiliser pour générer la réponse.
    :param history: L'historique des messages précédents.
    :param folder_chunks: Les chunks de fichier à inclure dans les messages.
    :return: La réponse générée par le LLM.
    """

    if len(history) > MAX_HISTORY_LENGTH:
        #history = history[-MAX_HISTORY_LENGTH:]
        history = await summarize_history(history)

    context = "\n\n".join([doc["content"] for doc in documents])
    metadata = "\n\n".join([str(doc["file_name"]) for doc in documents])
    page = "\n\n".join([str(doc["page"]) for doc in documents])

    history_sw = remove_stopwords(history)
    query_sw = remove_stopwords(query)

    history_token = ' '.join(history_sw)
    query_token = ' '.join(query_sw)

    if not context:
        raise ValueError("Le contexte est vide. Assurez-vous que les documents contiennent des données.")
    
    messages = [
        SystemMessage(content="Vous êtes un assistant utile et concis."),
        SystemMessage(content=f"Voici l'historique de la conversation: {history}"),
        SystemMessage(content=f"Voici les documents en rapport avec la demande de l'utilisateur: {context}"),
        SystemMessage(content=f"Le nom des fichiers: {metadata}"),
        SystemMessage(content=f"Pages: {page}"),
        SystemMessage(content=f"Voici le document uploadé: {folder_chunks}"),
        SystemMessage(content=f"Voici la demande de l'utilisateur: {query}"),
    ]

    # Ajouter les chunks de fichier comme un nouveau message système
    if folder_chunks:
        folder_content = "\n\n".join([chunk["chunk"] for chunk in folder_chunks])
        messages.append(SystemMessage(content=f"Folder: {folder_content}"))

    messages.append(HumanMessage(content=query))

    # Loguer les messages envoyés au LLM
    logger.info(f"Envoyer au LLM: {messages}")
    print('/n/n')
    logger.info(f"Contexte: {context}")
    print('/n/n')
    logger.info(f"Métadonnées: {metadata}")
    print('/n/n')
    logger.info(f"Pages: {page}")
    print('/n/n')
    logger.info(f"History: {history}")
    print('/n/n')
    logger.info(f"folder_chunks: {folder_chunks}")
    print('/n/n')
    logger.info(f"Query: {query_sw}")
    print('/n/n')
    
    # Générer la réponse
    response = await llm.agenerate([messages])
    response_text = response.generations[0][0].text

    logger.info(f"Réponse du LLM: {response_text}")
    
    return response_text