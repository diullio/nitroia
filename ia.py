import os
import streamlit as st
from langchain_community.chat_models.openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from datetime import datetime
import re

# Acessar a chave da API a partir do Streamlit Secrets Manager
openai_api_key = st.secrets["openai"]["api_key"]
os.environ["OPENAI_API_KEY"] = openai_api_key

def load_selected_files(selected_files):
    """
    Lê arquivos `.txt` da pasta atual com base em uma lista de nomes de arquivos selecionados,
    e retorna uma string concatenada com os conteúdos, separando-os por títulos baseados nos nomes dos arquivos.

    Args:
        selected_files (list): Lista de nomes de arquivos selecionados (com extensão `.txt`).

    Returns:
        str: Conteúdo concatenado dos arquivos com títulos formatados.
    """
    all_text = ""  # Armazenar o conteúdo concatenado

    racionais_directory = os.path.join(os.getcwd(), "racionais")

    for filename in selected_files:
        if filename.endswith(".txt"):  # Verifica se o arquivo é `.txt`
            path_txt = os.path.join(racionais_directory, filename)  # Caminho completo do arquivo
            try:
                # Lê o conteúdo do arquivo
                with open(path_txt, 'r', encoding='utf-8') as file:
                    content = file.read()

                # Adiciona um título baseado no nome do arquivo
                title = f"{filename.upper()}:"
                all_text += title + ":" + content + "    "
            except Exception as e:
                print(f"Erro ao processar o arquivo {filename}: {e}")
    
    return all_text

def nitro_chat(prompt, context):
    #Inicializar o modelo
    llm = ChatOpenAI(temperature=0.5, model='gpt-4o-mini-2024-07-18')
    system_message = SystemMessage(content="""
        Você é um assistente técnico especializado em nitrosaminas e legislação farmacêutica.
        Sua tarefa é auxiliar na elaboração de justificativas técnicas claras, embasadas e concisas
        para relatórios, considerando o contexto e referências fornecidas.
                                   
        Instruções:
        - Você está dando continuidade para um texto de racional técnico.
        - Use o mesmo idioma da instrução dada pelo usuário.
        - Priorize o contexto fornecido para elaborar as justificativas.
        - Utilize as referências como suporte, citando-as diretamente na resposta quando necessário, e estruture ajustando a numeração e criando uma seção referências ao final do texto. 
        - Seja claro, objetivo e técnico em suas respostas.
        - Não use a expressão com base no contexto fornecido visto que esta fazendo um documento oficial.
        - Gere a resposta em HTML.
                                   
        Sugestões:
        - Estruture a resposta de forma lógica e coesa.
        - Faça o texto breve em forma de parágrafos, não gere tópicos nem títulos.   	
	""")
    
	###
    user_message = HumanMessage(content=f"Contexto e Referências:: {context}\n{prompt}")
	
    messages_to_send = [system_message, user_message]
    
    response = llm(messages_to_send)
    
    conteudo = response.content.replace('```html', '')
    conteudo = conteudo.replace('```', '')
    return conteudo

def renumerar_referencias(texto, inicio=8):
    """
    Ajusta a numeração das referências em um texto para começar de um número específico.

    Args:
        texto (str): O texto contendo as referências numeradas.
        inicio (int): O número inicial para a renumeração das referências.

    Returns:
        str: Texto com as referências renumeradas.
    """
    # Encontrar todas as referências numeradas no padrão (1), (2), etc.
    referencias = re.findall(r'\((\d+)\)', texto)

    # Substituir cada referência com a nova numeração a partir do número inicial
    for i, ref in enumerate(referencias, start=inicio):
        texto = re.sub(rf'\({ref}\)', f'({i})', texto, count=1)
    
    return texto