import os
import streamlit as st
#from langchain_community.chat_models.openai import ChatOpenAI
#from langchain.schema import SystemMessage, HumanMessage
from datetime import datetime
import re
from collections import OrderedDict

import requests
import json

API_KEY = "AIzaSyDjRfAVjbrnH4ssIh8T9BqnrL0dMp2q2bw"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-exp-03-25:generateContent?key={API_KEY}"
#URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"


# Configurar a API Key do Gemini (substitua pela sua chave)
#client = genai.Client(api_key="AIzaSyDjRfAVjbrnH4ssIh8T9BqnrL0dMp2q2bw")


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

def nitro_chat_old(prompt, context):
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

def nitro_chat_(prompt, context):
   
    system_message = """
        ## Inicio do contexto
        {}
        ## Fim do contexto
        
        Você é um assistente técnico especializado em nitrosaminas e legislação farmacêutica.
        Sua tarefa é auxiliar na elaboração de justificativas técnicas claras, embasadas e concisas
        para relatórios, considerando o contexto e referências fornecidas.
                                   
        Instruções:
        - Você está dando continuidade para um texto de racional técnico.
        - Use o mesmo idioma da instrução dada pelo usuário.
        - Priorize o contexto fornecido para elaborar as justificativas.
        - Utilize as referências como suporte, citando-as diretamente na resposta quando necessário, e estruture ajustando a numeração e criando uma seção referências ao final do texto. 
        - Seja claro, objetivo e técnico em suas respostas.
        - Não use a expressão "com base no contexto fornecido", visto que está fazendo um documento oficial.
        - Gere a resposta em HTML.
                                   
        Sugestões:
        - Estruture a resposta de forma lógica e coesa.
        - Faça o texto breve em forma de parágrafos, não gere tópicos nem títulos.   
        - Sempre deixe siglas como NDMA, NDEA e outras em letras maiúsculas.
        
        ## Inicio do prompt
        {}
        ## Fim do prompt
    """

    fullprompt = system_message.format(context,prompt)
    print(fullprompt)
    # Enviar a requisição ao modelo
    response = client.models.generate_content(model="gemini-2.0-flash-lite",
                                              contents=fullprompt,
                                              #http_client=httpx.Client(verify=False)
                                              )   

    # Limpar a formatação do código HTML, se necessário
    conteudo = response.text.replace('```html', '').replace('```', '')
    print(conteudo)
    return conteudo

def nitro_chat(prompt, context,temperatura=0.5):
    # Formatar a mensagem no mesmo estilo do modelo original
    system_message = """
        ## Inicio do contexto
        {}
        ## Fim do contexto
        
        Você é um assistente técnico especializado em nitrosaminas e legislação farmacêutica.
        Sua tarefa é auxiliar na elaboração de justificativas técnicas claras, embasadas e concisas
        para relatórios, considerando o contexto e referências fornecidas.
                                   
        Instruções:
        - Você está dando continuidade para um texto de racional técnico.
        - Use o mesmo idioma da instrução dada pelo usuário.
        - Priorize o contexto fornecido para elaborar as justificativas.
        - Utilize as referências como suporte, citando-as diretamente na resposta quando necessário, e estruture ajustando a numeração e criando uma seção referências ao final do texto. 
        - Seja claro, objetivo e técnico em suas respostas.
        - Não use a expressão "com base no contexto fornecido", visto que está fazendo um documento oficial.
        - Gere a resposta em HTML.
        - Mantenha as citações vindas no contexto como (1),(2),(3)...(n) por exemplo. Não deduza citações no corpo do texto baseado no nome dos autores.
        - Caso tenha mais de uma citação juntas, como: (5) (6) NÃO junte-as (5,6) deixe sempre separadas na forma como é passada no texto.
        - As citações sempre serão numeros inteiros dentro de parentesis como (1), (2),... etc. Não considere como citação casos como (sp2) (3,15) ou conteudo que nao seja somente numeros inteiros dentro do parentesis.
        - Faça o texto breve em forma de parágrafos, não gere tópicos nem títulos.  
        - No contexto pode ter trechos que possuem a mesma referencia, mas está com citações diferentes, nestes casos não duplique a citação da referencia e padronize a citação.
        - Reescreva as citações trocando o numero (1) pelo (8) e dando sequencia as numerações, como (2) pra (9), (3) pra (10). Após isso, troque o caracter parenteses da citação e, apenas da citação, para colchetes, por exemplo (8) vira [8], (9) vira [9] etc
        - A seção de referências sempre gere da seguinte forma:
            <h2>Referências</h2>
            <p>[8] texto da Referencia 8.</p>
            <p>[9] texto da Referencia 9.</p>
            ... etc.          
        - Caso tenha refêrencias duplicadas ou que sejam a mesma referencia porém com texto um pouco diferente, remova-as deixando sempre a primeira ocorrência, De forma que no texto contenha somente a numeração da primeira referencia da duplicação.
        Sugestões:
        - Estruture a resposta de forma lógica e coesa.         
        - Sempre deixe siglas como NDMA, NDEA e outras em letras maiúsculas.
        
        ## Inicio do prompt
        {}
        ## Fim do prompt
    """
    print(f'###### CONTEXTO \n {context}')
    # Gerar o prompt final formatado
    fullprompt = system_message.format(context, prompt)
    print("Enviando para API:\n", fullprompt)

    # Construir a requisição para a API REST do Gemini
    headers = {"Content-Type": "application/json"}

    data = {
        "contents": [{"parts": [{"text": fullprompt}]}],
        "generationConfig": {
            "temperature": temperatura  # Adicionando temperatura
        }
    }
    
    # Fazer a requisição POST para a API
    response = requests.post(URL, headers=headers, data=json.dumps(data),verify=False)

    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        resposta_texto = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        
        # Remover formatação HTML se necessário
        conteudo = resposta_texto.replace('```html', '').replace('```', '')
        conteudo = conteudo.replace("<p><b>Conclusão:</b></p>","")
        
        print("Resposta da API:\n", conteudo)
        return conteudo
    else:
        print("Erro na API:", response.status_code, response.text)
        return None

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
    #referencias_texto = re.findall(r'\((\d+)\)', html)
    #referencias_texto = re.findall(r'\((\d)\)', html)
    # for i, ref in enumerate(referencias_texto, start=inicio):
    #     html = re.sub(rf'\({ref}\)', f'[{i}]', html, count=1)

    # # Ajustar referências no tópico "Referências"
    
    # # Tratar referências em listas <ul><li>
    html = re.sub(r'<ul>|</ul>', '', html)  # Remove as tags <ul> e </ul>
    referencias_lista = re.findall(r'<li>(.*?)</li>', html, re.DOTALL)
    for i, referencia in enumerate(referencias_lista, start=inicio):
        
        referencia_ajustada = f'<p>[{i}] {referencia.strip()}</p>'
        html = html.replace(f'<li>{referencia}</li>', referencia_ajustada)

    # # Tratar referências como parágrafos <p> no formato "1."
    referencias_paragrafos = re.findall(r'<p>(\d+)\.(.*?)</p>', html, re.DOTALL)
    for i, (numero, conteudo) in enumerate(referencias_paragrafos, start=inicio):
        referencia_ajustada = f'<p>[{i}] {conteudo.strip()}</p>'
        html = re.sub(rf'<p>{numero}\..*?</p>', referencia_ajustada, html, count=1)

    html = html.replace('<strong>',"").replace("</strong>","")
    print(f'### Referência arrumada\n\n{html}')
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
    
