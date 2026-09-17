import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import google.generativeai as genai
import json # Biblioteca nova para ler o cofre

st.title("Meu Agente Financeiro 🤖")

try:
    # 1. Puxando as chaves do "Cofre" do Streamlit de forma segura
    CHAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=CHAVE_GEMINI)
    modelo_ia = genai.GenerativeModel('gemini-3.6-flash')

    # 2. Lendo o JSON do Google também pelo Cofre
    escopos = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credenciais_dict = json.loads(st.secrets["GCP_CREDENCIAIS"])
    credenciais = Credentials.from_service_account_info(credenciais_dict, scopes=escopos)
    cliente = gspread.authorize(credenciais)

    # 3. Conexão com a planilha
    planilha = cliente.open("Cópia de 🦅 PlannerFin Sheets  v7.1 - Seu Nome")
    aba_home = planilha.worksheet("Home")
    dados_brutos = aba_home.get_all_values()
    df = pd.DataFrame(dados_brutos)
    
    st.success("Planilha conectada com sucesso!")
    
    with st.expander("Ver dados brutos da planilha"):
        st.dataframe(df)

    # 4. Estrutura do Chat
    st.subheader("Converse com seu Consultor")
    
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = []

    for msg in st.session_state.mensagens:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    pergunta = st.chat_input("Pergunte algo sobre suas finanças...")

    if pergunta:
        with st.chat_message("user"):
            st.markdown(pergunta)
        st.session_state.mensagens.append({"role": "user", "content": pergunta})

        dados_em_texto = df.to_csv(index=False)
        instrucao_sistema = f"""
        Você é um consultor financeiro especialista e está ajudando o Thiago a analisar as finanças dele.
        Abaixo estão os dados financeiros atuais extraídos da planilha de controle:
        
        {dados_em_texto}
        
        Responda à seguinte pergunta de forma clara, amigável e direta, baseando-se estritamente nos números acima:
        {pergunta}
        """

        resposta = modelo_ia.generate_content(instrucao_sistema)
        
        with st.chat_message("assistant"):
            st.markdown(resposta.text)
        st.session_state.mensagens.append({"role": "assistant", "content": resposta.text})

except Exception as e:
    st.error(f"Ocorreu um erro: {e}")