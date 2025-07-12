import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="MedSim Pro MVP", layout="wide")

# Barra lateral de configuração
st.sidebar.header("Configuração")

# Entrada da chave da OpenAI (corrigida)
api_key = st.sidebar.text_input("🔑 Sua chave OpenAI", type="password")

# Inicializa cliente da OpenAI somente se chave for informada
if api_key:
    client = OpenAI(api_key=api_key)

# Seleção de caso clínico
st.sidebar.write("Escolha o caso clínico:")
caso = st.sidebar.selectbox("", ["Úlcera por AINE (HDA leve)", "HDA grave com instabilidade"])

# Casos clínicos simulados
VL = {
    "Úlcera por AINE (HDA leve)": {
        "prompt_init": (
            "Você é um paciente com hematêmese leve tipo 'borra de café'. "
            "Tem 55 anos e tomou 5 a 6 comprimidos de ibuprofeno ao dia por cinco dias. "
            "Responda perguntas como um paciente ansioso, mas coerente."
        )
    },
    "HDA grave com instabilidade": {
        "prompt_init": (
            "Você é um paciente com hematêmese volumosa e instável hemodinamicamente. "
            "Tem 68 anos, pressão 75/50, pulso 120. "
            "Responda de modo confuso e ansioso."
        )
    }
}

# Estado da conversa
if "messages" not in st.session_state:
    st.session_state.messages = []
if "feedback" not in st.session_state:
    st.session_state.feedback = ""

# Função para chamar a IA
def chamar_ia(msg, system_prompt):
    msgs = [{"role": "system", "content": system_prompt}]
    msgs += [{"role": m["role"], "content": m["text"]} for m in st.session_state.messages]
    msgs.append({"role": "user", "content": msg})
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=msgs
    )
    return response.choices[0].message.content

# Layout
st.title("🎓 MedSim Pro MVP")
col1, col2 = st.columns([2,1])

with col1:
    st.header("Interação com o paciente")
    user_input = st.text_input("Faça sua pergunta ou conduta:")
    if st.button("Enviar"):
        if not api_key:
            st.error("Por favor, insira sua chave da OpenAI na barra lateral.")
        else:
            sys_promp = VL[caso]["prompt_init"]
            resposta = chamar_ia(user_input, sys_promp)
            st.session_state.messages.append({"role":"user","text":user_input})
            st.session_state.messages.append({"role":"assistant","text":resposta})
            # Avaliação simples automática
            fb = ""
            texto = user_input.lower()
            if "omeprazol" in texto or "inibidor" in texto:
                fb += "✓ Indicou omeprazol (boa conduta).\n"
            if "endoscopia" in texto or "eda" in texto:
                fb += "✓ Solicitou endoscopia (EDA).\n"
            if "ringer" in texto or "reposição" in texto:
                fb += "✓ Iniciou reposição volêmica.\n"
            st.session_state.feedback = fb or "📌 Tente incluir exame ou conduta apropriada."

with col2:
    st.header("Respostas do paciente")
    for m in st.session_state.messages:
        if m["role"] == "assistant":
            st.markdown(f"**Paciente:** {m['text']}")
    st.markdown("---")
    st.subheader("Feedback / Pontuação")
    st.info(st.session_state.feedback)
