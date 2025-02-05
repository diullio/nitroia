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

def load_sem_risco(selected_files):
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

                all_text = content
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
        - Sempre deixe siglas como NDMA, NDEA, e outras.. em letras maiúsculas.
	""")
    
	###
    user_message = HumanMessage(content=f"Contexto e Referências:: {context}\n{prompt}")
	
    messages_to_send = [system_message, user_message]
    
    response = llm(messages_to_send)
    
    conteudo = response.content.replace('```html', '')
    conteudo = conteudo.replace('```', '')
    return conteudo

def ajustar_referencias_html(html, inicio=8):
    """
    Ajusta a numeração e o formato das referências no HTML, alterando:
    - No texto: de "(1)" para "[1]".
    - No tópico "Referências": de diferentes formatos para "[n]".

    Args:
        html (str): O HTML contendo as referências numeradas.
        inicio (int): O número inicial para a renumeração das referências.

    Returns:
        str: HTML com as referências ajustadas.
    """
    # Ajustar as referências no texto (de "(1)" para "[1]")
    referencias_texto = re.findall(r'\((\d+)\)', html)
    for i, ref in enumerate(referencias_texto, start=inicio):
        html = re.sub(rf'\({ref}\)', f'[{i}]', html, count=1)

    # Ajustar referências no tópico "Referências"
    
    # Tratar referências em listas <ul><li>
    html = re.sub(r'<ul>|</ul>', '', html)  # Remove as tags <ul> e </ul>
    referencias_lista = re.findall(r'<li>(.*?)</li>', html, re.DOTALL)
    for i, referencia in enumerate(referencias_lista, start=inicio):
        referencia_ajustada = f'<p>[{i}] {referencia.strip()}</p>'
        html = html.replace(f'<li>{referencia}</li>', referencia_ajustada)

    # Tratar referências como parágrafos <p> no formato "1."
    referencias_paragrafos = re.findall(r'<p>(\d+)\.(.*?)</p>', html, re.DOTALL)
    for i, (numero, conteudo) in enumerate(referencias_paragrafos, start=inicio):
        referencia_ajustada = f'<p>[{i}] {conteudo.strip()}</p>'
        html = re.sub(rf'<p>{numero}\..*?</p>', referencia_ajustada, html, count=1)

    return html

def fragmentar_html_referencias(html):
    """
    Fragmenta o HTML em duas partes: o texto antes de "<p>Referências:</p>"
    e as referências após ele. Remove o elemento "<p>Referências:</p>".

    Args:
        html (str): O HTML contendo as referências.

    Returns:
        tuple: Uma tupla com duas strings:
            - Parte do texto antes de "<p>Referências:</p>".
            - Parte das referências após "<p>Referências:</p>".
    """
    # Dividir o HTML no ponto de "<p>Referências:</p>"
    padrao_referencias = r"<p>Referências:?</p>|Referências:?"

    partes = re.split(padrao_referencias, html, maxsplit=1, flags=re.IGNORECASE)
    
    # Verificar se o split resultou em duas partes
    if len(partes) == 2:
        texto_anterior = partes[0].strip()  # Parte antes de "Referências"
        referencias = partes[1].strip()    # Parte das referências
        return texto_anterior, referencias
    else:
        # Caso não exista "<p>Referências:</p>" no HTML
        return html.strip(), ""