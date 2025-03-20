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

from app.services.mongo_service import get_uploaded_chunks, update_uploaded_chunks

nltk.download('stopwords')
nltk.download('punkt')

# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger la clé API OpenAI depuis les variables d'environnement
openai_api_key = os.getenv("OPENAI_API_KEY")

MAX_HISTORY_LENGTH = 10000

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




async def generate_response(query: str, documents: list, history: str, folder_chunks: list, conversation_id: str) -> str:
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
        # si conerstaion_id est fourni, récupérer les chunks existants depuis MongoDB
    if conversation_id:
        # Récupérer les chunks existants depuis MongoDB
        existing_chunks = await get_uploaded_chunks(conversation_id)

        # Si aucun chunk n'existe, ajouter les nouveaux chunks
        if not existing_chunks:
            new_chunks = [chunk["chunk"] for chunk in folder_chunks if "chunk" in chunk]
            if new_chunks:
                await update_uploaded_chunks(conversation_id, new_chunks)
                logger.info(f"Nouveaux chunks ajoutés à la conversation {conversation_id}")
        else:
            logger.info(f"Chunks existants pour la conversation {conversation_id}")

        folder_chunks.extend(existing_chunks or [])


    # if folder_chunks:
    #     new_chunks = [chunk["chunk"] for chunk in folder_chunks]
    #     await update_uploaded_chunks(conversation_id, new_chunks)
    #     folder_chunks.extend(new_chunks)



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
    print("\n")

    logger.info(f"Conversation ID: {conversation_id}")
    #Afficher un pas de ligne
    
    # Retourner la réponse générée
    return response_text