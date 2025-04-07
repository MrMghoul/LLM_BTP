import os
import logging
from langchain_openai import ChatOpenAI, OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
import nltk
print(nltk.data.path)
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from transformers import AutoModelForCausalLM, AutoTokenizer


from app.services.mongo_service import get_uploaded_chunks, update_uploaded_chunks

# Définir le chemin des données NLTK
nltk_data_path = "/root/nltk_data"
if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path)
nltk.data.path.append(nltk_data_path)

# Télécharger les ressources nécessaires
nltk.download('punkt', download_dir=nltk_data_path)
nltk.download('stopwords', download_dir=nltk_data_path)
nltk.download('punkt_tab')

#Biblioteque pour le traitement de texte stopwords
# nltk.download('stopwords')
# nltk.download('punkt')

# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger la clé API OpenAI depuis les variables d'environnement
openai_api_key = os.getenv("OPENAI_API_KEY")

""" Model Mistral """
# model_name = "mistralai/Mistral-7B"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name)

# Définir la longueur maximale de l'historique
MAX_HISTORY_LENGTH = 5000

# Initialiser le modèle OpenAI
llm = ChatOpenAI(
    temperature=0.7,
    model_name="gpt-3.5-turbo",
    api_key=openai_api_key)

# Fonction pour supprimer les stopwords d'un texte
def remove_stopwords(text):
    stop_words = set(stopwords.words('french'))
    word_tokens = word_tokenize(text)
    filtered_tokens = [word for word in word_tokens if word.lower() not in stop_words]
    return filtered_tokens

# Fonction pour poser une question avec le modèle Mistral (fonction test)
async def ask_question(query: str, history: str) -> str:
    """
    Pose une question au modèle Mistral et obtient une réponse.
    """
    # Construire le prompt en combinant l'historique et la question
    prompt = f"Historique:\n{history}\n\nQuestion:\n{query}\n\nRéponse:"
    
    # Loguer le prompt envoyé au modèle
    logger.info(f"Envoyer au modèle Mistral: {prompt}")
    
    # # Générer une réponse avec Mistral
    # inputs = tokenizer(prompt, return_tensors="pt").to("cuda")  # Assurez-vous que votre machine supporte CUDA
    # outputs = model.generate(inputs.input_ids, max_length=500, num_return_sequences=1, temperature=0.7)
    # response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Utiliser le modèle OpenAI pour générer la réponse
    messages = [
        SystemMessage(content="Vous êtes un assistant utile et concis."),
        HumanMessage(content=prompt)
    ]

    response = await llm.agenerate([messages])
    response_text = response.generations[0][0].text.strip()
    # Loguer la réponse reçue du modèle
    logger.info(f"Réponse du modèle Mistral: {response_text}")
    
    return response_text

# Fonction pour résumer l'historique
async def summarize_history(history: str) -> str:
    """
    Génère un résumé de l'historique pour réduire sa taille.
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



# Fonction pour générer une réponse à partir du LLM OpenAI (fonction principale)
async def generate_response(query: str, documents: list, history: str, folder_chunks: list, conversation_id: str) -> str:
    """
    Génère une réponse à partir du LLM en utilisant la requête, les documents fournis et les chunks de fichier.
    
    :parametre query: La requête de l'utilisateur.
    :parametre documents: Les documents à utiliser pour générer la réponse.
    :parametre history: L'historique des messages précédents.
    :parametre folder_chunks: Les chunks de fichier à inclure dans les messages.
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
    chunks_id = "\n\n".join([str(doc["chunk_id"]) for doc in documents])

    history_sw = remove_stopwords(history)
    query_sw = remove_stopwords(query)



    if not context:
        raise ValueError("Le contexte est vide. Assurez-vous que les documents contiennent des données.")
    
    # Créer le message structuré à envoyer au LLM
    messages = [
        SystemMessage(content="Vous êtes un assistant utile et concis."),
        SystemMessage(content=f"Voici l'historique de la conversation: {history}"),
        SystemMessage(content=f"Voici les documents en rapport avec la demande de l'utilisateur: {context}"),
        SystemMessage(content=f"Le nom des fichiers: {metadata}"),
        SystemMessage(content=f"Voici les Pages respectives des chunks: {page}"),
        SystemMessage(content=f"Voici les IDs respectifs des chunks: {chunks_id}"),
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
    logger.info(f"IDs des chunks: {chunks_id}")
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