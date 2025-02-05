import os
import streamlit as st
import pandas as pd
from functions import localizar_ppb, gerar_html, criar_quadro, criar_texto, html_AR
from ia import load_selected_files, nitro_chat, ajustar_referencias_html, fragmentar_html_referencias, load_sem_risco

# Inicializa o estado global para armazenar dados
if "dados" not in st.session_state:
    st.session_state.dados = []

# Validação para garantir que o valor seja numérico
def validar_float(input_value):
    # Remove espaços extras e substitui vírgula por ponto
    input_value = input_value.replace(',', '.').strip()
    try:
        return float(input_value)
    except ValueError:
        return None
    
# Função principal
def main():
    st.title("Gerador de Avaliação de Risco (AR)")

    st.markdown(
    '<a href="https://products.aspose.app/words/pt/conversion" target="_blank">Para converter o documento gerado clique aqui</a>',
    unsafe_allow_html=True
)

    elaborador = st.text_input("Elaborador", key="elaborador")
    produto = st.text_input("Nome do Produto", key="produto")
    col1, col3 = st.columns([2, 2])

    if "dados" not in st.session_state:
        st.session_state.dados = []

    if "anexos" not in st.session_state:
        st.session_state.anexos = []    

    with col1:
        st.subheader("Informações do IFA")
        ifa = st.text_input("IFA", key="ifa")
        fabricante = st.text_input("Fabricante", key="fabricante")
        planta_fabril = st.text_input("Planta Fabril", key="planta_fabril")
        difa = st.text_input("DIFA (DMF)", key="difa")
        dose_maxima = st.text_input("Pontuação Dose Máxima", key="dose_maxima")
        duracao_trat = st.text_input("Pontuação Duração do Tratamento", key="duracao_trat")
        local_acao = st.text_input("Pontuação Local de Ação", key="local_acao")
        pop_pacientes = st.text_input("Pontuação População de Pacientes", key="pop_pacientes")
        
        # A validação de risco agora é sempre feita
        risco = st.number_input("Risco Global Calculado", min_value=0, key="risco")
        
    with col3:
        st.subheader("Predição de Ashworth")
        nitrosamina = st.text_input("Nitrosamina", key="nitrosamina")
        limite = st.text_input("Limite de Ingestão Diário (ng/dia)", key="limite")
        dose = st.text_input("Dose Máxima Diária (mg/dia)", key="dose")
        # Validação para garantir que o valor seja numérico
        limite = validar_float(limite)
        dose = validar_float(dose)
        ph = st.selectbox("Valor de pH", options=[3.15, 5, 7, 9], key="ph")
        pka = st.slider("pKa", min_value=9.5, max_value=14.0, step=0.1, value=9.5, key="pka")
        nitrito = st.selectbox("Níveis de Nitrito", options=["0.01 mg/L", "3 mg/L", "1 M"], key="nitrito")
        amina = st.selectbox("Quantidade de Amina", options=["1 mM", "1 M"], key="amina")
        temperatura = st.selectbox(
                "Temperatura (°C)", options=["25", "35", "45", "55", "25 (1 h)"], key="temperatura"
        )

        if st.button("Calcular Predição"):
            try:
                if limite is None or dose is None:
                    st.error("Por favor, insira um valor válido para os parâmetros.")
                valor_tabela = localizar_ppb(amina, nitrito, temperatura, ph)
                valor_tabela = float(valor_tabela)/1000
                if valor_tabela == "Combinação inválida":
                    st.error("A combinação selecionada não existe no artigo.")
                st.write(f"Limite: {limite} ng/dia, Dose: {dose} mg/dia, Valor Tabela: {valor_tabela} ppb")
                # Salvar os valores de risco, nitrosamina e risco_nitrosamina no session_state
                risco_nitrosamina = "baixo" if (limite / dose > valor_tabela) else "alto"
                quadro = criar_quadro(ph, pka, nitrito, amina, temperatura, dose, limite)
                texto = criar_texto(ph, pka, nitrito, amina, temperatura, valor_tabela, nitrosamina, ifa, limite, dose)
                html_anexo = gerar_html(ifa, quadro, texto)

                # Adicionar o anexo gerado à lista de anexos
                st.session_state.anexos.append({
                    "ifa": ifa,
                    "fabricante": fabricante,
                    "nitrosamina": nitrosamina,
                    "risco_nitrosamina": risco_nitrosamina
                })

                st.download_button(
                    "Baixar Anexo Predição",
                    data=html_anexo,
                    file_name=f"Anexo_Predicao_{ifa}.html",
                    mime="text/html",
                )
                
            except Exception as e:
                st.error(f"Erro no cálculo: {e}")

        # Botão para adicionar um novo IFA
    if st.button("Adicionar IFA"):
        if limite and dose:
            valor_tabela = localizar_ppb(amina, nitrito, temperatura, ph)
            valor_tabela = float(valor_tabela)/1000
            risco_nitrosamina = "baixo" if (limite / dose > valor_tabela) else "alto"
        else:
            nitrosamina = None
            risco_nitrosamina = None
        st.session_state.dados.append(
            {
                    "ifa": ifa,
                    "fabricante": fabricante,
                    "planta_fabril": planta_fabril,
                    "difa": difa,
                    "risco": risco,
                    "nitrosamina": nitrosamina if nitrosamina else None,  # No caso de não haver nitrosamina
                    "risco_nitrosamina": risco_nitrosamina if risco_nitrosamina else None,  # No caso de não haver risco nitrosamina
                    'dose_maxima': int(dose_maxima),
                    'duracao_trat': int(duracao_trat),
                    'local_acao': int(local_acao),
                    'pop_pacientes': int(pop_pacientes),
            }
        )
        st.success(f"IFA '{ifa}' adicionado com sucesso!")

    if st.session_state.dados:
        # Cria um DataFrame para exibir os dados em forma de tabela
        dados_df = pd.DataFrame(st.session_state.dados)
        st.dataframe(dados_df)

        ifa_para_remover = st.selectbox(
            "Selecione um IFA para remover",
            options=[ifa['ifa'] for ifa in st.session_state.dados],
            key="select_ifa_remover"
        )

        if st.button("Remover IFA Selecionado"):
            if ifa_para_remover:
                index_to_remove = next((index for index, ifa in enumerate(st.session_state.dados) if ifa['ifa'] == ifa_para_remover), None)
                if index_to_remove is not None:
                    st.session_state.dados.pop(index_to_remove)
                    st.success(f"IFA '{ifa_para_remover}' removido com sucesso!")
                else:
                    st.error(f"Erro ao tentar remover o IFA '{ifa_para_remover}'.")

    ## IA PARA RACIONAIS
    st.subheader('Gerador de Racional')
    # Obtém a lista de arquivos .txt na pasta atual
    risco_pa = st.text_input("Risco Global PA", key="risco_pa")
    
    # Valida e converte risco_pa para número
    if risco_pa.isdigit():
        risco_pa = int(risco_pa)
    else:
        st.error("Insira um valor numérico válido para o Risco Global PA.")

    racionais_directory = os.path.join(os.getcwd(), "racionais")
    files_in_directory = [f for f in os.listdir(racionais_directory) if f.endswith(".txt")]
    # Exibe checkboxes para cada arquivo
    selected_files = st.multiselect("Selecione os itens que deseja considerar:", files_in_directory)
    print(selected_files)
        

    if st.button("Gerar Avaliação de Risco"):
        if not produto or not st.session_state.dados or not risco_pa:
            st.error("Por favor, insira o nome do produto e adicione pelo menos um IFA.")
        else:
            if 'sem_risco' in selected_files:
                context = load_sem_risco(selected_files)
                ia_racional, referencia = context, ''
            elif selected_files:
                context = load_selected_files(selected_files)
                prompt = f'''Elabore um racional com base no contexto fornecido e referencie o texto. Ao final faça uma conclusão com base no racional abordado sem gerar um novo topico finalizando meu racional, considerando que para eu ter formação de nitrosaminas eu preciso ter Aminas, Nitrito e Meio reacional ácido, caso seja possivel mitigar com os racionais selecionados gere uma conclusão de risco baixo.
                '''
                ia_content = nitro_chat(prompt, context)
                ia_content_ref = ajustar_referencias_html(ia_content)
                ia_racional, referencia = fragmentar_html_referencias(ia_content_ref)  
            else:
                ia_racional, referencia = '', ''


            html = html_AR(st.session_state.dados, produto, st.session_state.anexos, elaborador, ia_racional, referencia, risco_pa, produto)
            st.download_button(
                label="Baixar Avaliação de Risco",
                data=html,
                file_name=f"Avaliacao_Risco_{produto}.html",
                mime="text/html",
            )

if __name__ == "__main__":
    main()
