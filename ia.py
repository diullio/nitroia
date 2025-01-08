import os
import streamlit as st
from langchain_community.chat_models.openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.callbacks import get_openai_callback
from datetime import datetime

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
        - Faça uma breve introdução sobre o tema.
        - Use o mesmo idioma da instrução dada pelo usuário.
        - Priorize o contexto fornecido para elaborar as justificativas.
        - Utilize as referências como suporte, citando-as diretamente na resposta quando necessário, e estruture ajustando a numeração e criando uma seção referências ao final do texto.
        - Seja claro, objetivo e técnico em suas respostas.
        - Não use a expressão com base no contexto fornecido visto que esta fazendo um documento oficial.
        - Gere a resposta em HTML.
                                   
        Sugestões:
        - Estruture a resposta de forma lógica e coesa.
        - Se necessário, divida a resposta em tópicos ou parágrafos.            	
	""")
    
	###
    user_message = HumanMessage(content=f"Contexto e Referências:: {context}\n{prompt}")
	
    messages_to_send = [system_message, user_message]
    
    with get_openai_callback() as callback:
        response = llm(messages_to_send)
        custo = callback.total_cost
    
    conteudo = response.content.replace('```html', '')
    conteudo = conteudo.replace('```', '')
    return conteudo, custo

# Função para gerar HTML formal
def create_html_rational(product_name, content):
    """
    Cria um HTML estilizado para o racional.
    """
    date_today = datetime.now().strftime("%d/%m/%Y")
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Racional</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 20px;
                font-size: 12pt;
            }}
            .header {{
                background-color: #f2f2f2;
                padding: 20px;
                border: 1px solid #ddd;
                margin-bottom: 20px;
            }}
            h1 {{
                text-align: center;
                font-size: 14pt;
                margin-bottom: 10px;
            }}
            .header table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .header table th, .header table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            .content {{
                margin-top: 20px;
            }}
            .content h2 {{
                color: #333;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <table>
                <tr>
                    <th>Produto</th>
                    <td>{product_name}</td>
                </tr>
                <tr>
                    <th>Data</th>
                    <td>{date_today}</td>
                </tr>
            </table>
        </div>
        <div class="content">
            {content}
        </div>
    </body>
    </html>
    """
    return html_content

