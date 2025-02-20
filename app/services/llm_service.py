import os
import logging
from langchain_openai import ChatOpenAI, OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage 


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Charger la clé API OpenAI depuis les variables d'environnement
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialiser le modèle OpenAI
llm = ChatOpenAI(
    temperature=0.7,
    model_name="gpt-3.5-turbo",
    api_key=openai_api_key)

async def ask_question(query: str) -> str:
    """
    Pose une question au LLM et obtient une réponse.
    
    :param query: La question à poser.
    :return: La réponse générée par le LLM.
    """
    # Créer les messages avec un message système initial
    messages = [
        SystemMessage(content="Vous êtes un assistant utile et concis."),
        HumanMessage(content=query)
    ]
    
    # Loguer la requête envoyée au LLM
    logger.info(f"Envoyer au LLM: {query}")
    
    # Générer la réponse
    response = await llm.agenerate([messages])
    response_text = response.generations[0][0].text
    
    # Loguer la réponse reçue du LLM
    logger.info(f"Réponse du LLM: {response_text}")
    
    return response_text

def generate_response(query: str, documents: list):
    """
    Génère une réponse à partir du LLM en utilisant la requête et les documents fournis.
    
    :param query: La requête de l'utilisateur.
    :param documents: Les documents à utiliser pour générer la réponse.
    :return: La réponse générée par le LLM.
    """
    # Créer un template de prompt
    prompt_template = ChatPromptTemplate.from_template(
        "Question: {query}\n\nContext: {context}\n\nAnswer:"
    )
    
    # Charger la chaîne de question-réponse
    qa_chain = LLMChain(llm=llm, prompt=prompt_template)

    # Préparer le contexte à partir des documents
    context = "\n\n".join([doc["content"] for doc in documents])
    
    if not context:
        raise ValueError("Le contexte est vide. Assurez-vous que les documents contiennent des données.")
    
    
    # Générer la réponse
    response = qa_chain.run({"query": query, "context": context})
    
    return response 