import os
import streamlit as st
from jinja2 import Environment, FileSystemLoader
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.callbacks import get_openai_callback
from datetime import datetime


os.environ["OPENAI_API_KEY"] = st.secrets["openai"]["api_key"]

#Ashworth
def localizar_ppb(amina, nitrito, temperatura, pH):
    # Lê o arquivo CSV
    dados = pd.read_csv('tabela.csv')

    # Filtro para encontrar o valor correto
    resultado = dados[
        (dados["amina"] == amina) &
        (dados["nitrito"] == nitrito) &
        (dados["temperatura"] == temperatura) &
        (dados["pH"] == pH)
    ]

    # Verifica se o filtro encontrou resultados
    if resultado.empty:
        return "Combinação inválida"
    
    # Retorna o valor do ppb encontrado
    return resultado["ppb"].values[0]

# Função para gerar o Arquivo da Predição
def gerar_html(produto, quadro_1, texto_modelo):   
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Anexo Predição - {produto}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #333;
                margin: 0;
                padding: 0;
                background-color: #f9f9f9;
            }}
            .container {{
                width: 90%;
                max-width: 800px;
                margin: 30px auto;
                background: #fff;
                border-radius: 8px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            .header {{
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .content {{
                padding: 20px;
                line-height: 1.8;
                font-size: 16px;
            }}
            .content p {{
                text-align: justify;
                text-indent: 1.5cm;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: #d3d3d3; /* Cinza claro */
                color: #333;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            tr:hover {{
                background-color: #f1f1f1;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">Relatório de Predição de Nitrosaminas</div>
            <div class="content">
                <p>{texto_modelo}</p>
                <h3>Quadro 1 - Valores Informados</h3>
                {quadro_1}
            </div>
        </div>
    </body>
    </html>
    """
    return html

# Quadro 1 em HTML - Ashworth
def criar_quadro(ph, pka, nitrito, amina, temperatura, dose, limite):
    return f"""
    <table border="1">
        <thead>
            <tr>
                <th>pH</th>
                <th>pKa</th>
                <th>Níveis de Nitrito</th>
                <th>Quantidade de Amina</th>
                <th>Temperatura</th>
                <th>Dose Máxima (mg/dia)</th>
                <th>Limite de Nitrosamina (ng/dia) [1]</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>{ph}</td>
                <td>{pka}</td>
                <td>{nitrito}</td>
                <td>{amina}</td>
                <td>{temperatura}°C</td>
                <td>{dose}</td>
                <td>{limite}</td>
            </tr>
        </tbody>
    </table>
    """

# Função para criar o texto de saída
def criar_texto(ph, pka, nitrito, amina, temperatura, valor_tabela, nitrosamina, ifa, limite, dose):
    valor_calculado = float(limite) / float(dose)
    percentual = (valor_tabela / (valor_calculado )) * 100
    risco = "baixo" if percentual < 10 else "alto"
    especificacao_texto = (
        "abaixo de 10% da especificação" if percentual < 10 else "acima de 10% da especificação"
    )
    return f"""
    No quadro 1 deste Anexo, foram inseridos valores de pH ({ph}), pKa ({pka}), níveis de nitrito ({nitrito}), quantidade de amina ({amina}) e temperatura do processo ({temperatura}°C), obtendo a quantidade de {valor_tabela} ppb formada. Conforme predição teórica de Ashworth e colaboradores, a formação de {nitrosamina} está {especificacao_texto} ({valor_calculado:.2e} ppm). Desta forma, o risco para a formação de {nitrosamina} no IFA {ifa} é {risco}.
    
    [1] I. W. Ashworth, O. Dirat, A. Teasdale, and M. Whiting, “Potential for the Formation of N-Nitrosamines during the Manufacture of Active Pharmaceutical Ingredients: An Assessment of the Risk Posed by Trace Nitrite in Water,” Org Process Res Dev, vol. 24, no. 9, pp. 1629–1646, Sep. 2020, doi: 10.1021/acs.oprd.0c00224.
    """

def int_to_roman(n):
    roman_numerals = {
        1: 'I', 4: 'IV', 5: 'V', 9: 'IX', 10: 'X', 40: 'XL', 50: 'L', 90: 'XC',
        100: 'C', 400: 'CD', 500: 'D', 900: 'CM', 1000: 'M'
    }
    result = ''
    for value, numeral in sorted(roman_numerals.items(), reverse=True):
        while n >= value:
            result += numeral
            n -= value
    return result

#Funcao para gerar analise de risco
def html_AR(dados, produto, dados_anexos, elaborador):
    env = Environment(loader=FileSystemLoader('.'))
    # Registrar o filtro 'romanize'
    env.filters['romanize'] = int_to_roman

    num_range = list(range(1, len(dados) + 1))
    # Adiciona a variável 'predicao' para cada dado
    for i, dado in enumerate(dados):
        if dado["nitrosamina"]:  # Verifica se há nitrosamina
            dado["predicao"] = len(dados) + 2 + i  # PA e indice

    template = env.get_template("ar_model.html")
    try:
        html = template.render(
            dados=dados,
            produto=produto,
            num_range=num_range,
            dados_anexos=dados_anexos,
            elaborador=elaborador
        )
        return html
    except Exception as e:
        print("Erro ao renderizar template:", e)
        raise

##### IA

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

    for filename in selected_files:
        if filename.endswith(".txt"):  # Verifica se o arquivo é `.txt`
            path_txt = os.path.join(os.getcwd(), filename)  # Caminho completo do arquivo
            try:
                # Lê o conteúdo do arquivo
                with open(path_txt, 'r', encoding='utf-8') as file:
                    content = file.read()

                # Adiciona um título baseado no nome do arquivo
                title = f"\n{filename.upper()}:"
                all_text += title + "\n" + content + "\n\n"
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
        - Use o mesmo idioma da instrução dada pelo usuário.
        - Priorize o contexto fornecido para elaborar as justificativas.
        - Utilize as referências como suporte, citando-as diretamente na resposta quando necessário, e estruture ajustando a numeração e criando uma seção referências ao final do texto.
        - Seja claro, objetivo e técnico em suas respostas.
                                   
        Sugestões:
        - Estruture a resposta de forma lógica e coesa.
        - Se necessário, divida a resposta em tópicos ou parágrafos.            	
	""")
    
	###
    user_message = HumanMessage(content=f"""
        {prompt}

        Contexto e Referências:
        {context}
    """)
	
    messages_to_send = [system_message, user_message]
    
    with get_openai_callback() as callback:
        response = llm(messages_to_send)
        custo = callback.total_cost
        
    return response.content, custo

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
            }}
            .header {{
                background-color: #f2f2f2;
                padding: 20px;
                border: 1px solid #ddd;
                margin-bottom: 20px;
            }}
            .header h1 {{
                text-align: center;
                font-size: 24px;
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
            <h1>Justificativa Técnica</h1>
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
            <h2>Racional:</h2>
            <p>{content.replace('\n', '<br>')}</p>
        </div>
    </body>
    </html>
    """
    return html_content

