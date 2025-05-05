import os, re, subprocess, time, uuid
import streamlit as st
import vertexai
from vertexai.preview.generative_models import GenerativeModel

# ───────────────────────────── 1) Configuração inicial
st.set_page_config(page_title="Gemini Chat", page_icon="🤖")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ".formal-purpose-354320-af3d391f5234.json"
PROJECT_ID = "formal-purpose-354320"
LOCATION   = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
MODEL_ID   = "gemini-2.0-flash"

vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel(MODEL_ID)

def limpar_ansi(texto):
    texto = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', texto)
    linhas = texto.splitlines()
    linhas_limpa = [linha for linha in linhas if linha.strip()]
    return "\n".join(linhas_limpa)

def estimar_tokens(texto):
    return len(texto) / 4  # Aproximação: 1 token ≈ 4 caracteres

def executar_codigos(texto, profundidade=0, max_profundidade=50000):
    if profundidade >= max_profundidade:
        st.warning("🔄 Limite máximo de ciclos de execução atingido!")
        return

    python_blocks = re.findall(r"```python\s+(.*?)```", texto, re.DOTALL | re.IGNORECASE)
    if not python_blocks:
        return

    codigo = "\n\n".join(python_blocks)
    script_temp = "temp_script.py"
    saida_arquivo = "saida_codigo.txt"

    with open(script_temp, "w", encoding="utf-8") as f:
        f.write(codigo)

    with open(saida_arquivo, "w", encoding="utf-8") as f_saida:
        process = subprocess.Popen(
            ["python", script_temp],
            stdout=f_saida,
            stderr=subprocess.STDOUT,
            text=True
        )

    output_box = st.empty()
    tempo_box = st.empty()
    cancelar_box = st.empty()

    tempo_inicio = time.time()
    cancelado = False

    messages.append(("execucao", "🚀 **Executando código Python...**"))

    while True:
        if cancelar_box.button("❌ Cancelar Execução", key=f"cancelar_execucao_{uuid.uuid4()}"):
            if process.poll() is None:
                process.terminate()
                cancelado = True

        if os.path.exists(saida_arquivo):
            with open(saida_arquivo, "r", encoding="utf-8") as f:
                content = f.read()
            content_limpo = limpar_ansi(content)
            output_box.markdown(f"```text\n{content_limpo}\n```")

        tempo_decorrido = time.time() - tempo_inicio
        tempo_box.markdown(f"⏱️ **Tempo de execução:** {tempo_decorrido:.1f} segundos")

        if process.poll() is not None:
            break

        time.sleep(1)

    if os.path.exists(saida_arquivo):
        with open(saida_arquivo, "r", encoding="utf-8") as f:
            saida_final = f.read()
        saida_final_limpa = limpar_ansi(saida_final)
        output_box.markdown(f"```text\n{saida_final_limpa}\n```")

    analise_msg = "🔎 **Analisando resultados da execução...**"
    st.chat_message("💭 Sistema").markdown(analise_msg)
    messages.append(("system", analise_msg))

    nova_resposta = chat.send_message(saida_final_limpa).text
    st.chat_message("Gemini").markdown(nova_resposta)
    messages.append(("bot", nova_resposta))

    # Atualizar tokens
    tokens_saida_follow = estimar_tokens(nova_resposta)
    total_tokens = st.session_state.get("total_tokens", 0) + tokens_saida_follow
    st.session_state["total_tokens"] = total_tokens

    st.markdown(
        f"<div style='color: gray; font-size: small;'>"
        f"Rodada: {int(tokens_saida_follow)} "
        f"Total: {int(total_tokens)}"
        f"</div>",
        unsafe_allow_html=True
    )

    if os.path.exists(saida_arquivo):
        os.remove(saida_arquivo)
    if os.path.exists(script_temp):
        os.remove(script_temp)

    # Recursivamente processar nova resposta
    executar_codigos(nova_resposta, profundidade=profundidade+1, max_profundidade=max_profundidade)

# ───────────────────────────── 3) Estado persistente
chat             = st.session_state.setdefault("chat", model.start_chat())
messages         = st.session_state.setdefault("messages", [])
total_tokens     = st.session_state.setdefault("total_tokens", 0)

# ───────────────────────────── 3.1) Instrução inicial
if "instrucoes_enviadas" not in st.session_state:
    instrucao_inicial = (
        "Você é um assistente de programação.\n"
        "Seu objetivo é ajudar o usuário a criar, melhorar e executar códigos Python.\n"
        "Sempre que gerar códigos Python, escreva-os em blocos entre crases e identifique com 'python'.\n"
        "Se precisar fazer análises de resultados, gere instruções claras e simples.\n"
        "Responda apenas com informações técnicas, sem floreios ou enfeites desnecessários.\n"
        "Seja objetivo, técnico e profissional."
    )
    resposta_instrucao = chat.send_message(instrucao_inicial).text
    messages.append(("system", instrucao_inicial))
    messages.append(("bot", resposta_instrucao))
    st.session_state["instrucoes_enviadas"] = True

# ───────────────────────────── 4) Cabeçalho
st.title("🗨️ Gemini Chatbot")
st.caption(f"Modelo: **{MODEL_ID}** ｜ Projeto: **{PROJECT_ID}**")
st.markdown("---")

# ───────────────────────────── 5) Histórico
for role, txt in messages:
    lbl = (
        "Você" if role == "user" else
        "Gemini" if role == "bot" else
        "⚙️ Execução" if role == "execucao" else
        "🔎 Análise" if role == "analise" else
        "💭 Sistema"
    )
    st.chat_message(lbl).markdown(txt)

# ───────────────────────────── 6) Caixa de entrada
prompt = st.chat_input("Digite sua pergunta...")

if prompt:
    st.chat_message("Você").markdown(prompt)
    messages.append(("user", prompt))

    st.chat_message("💭 Sistema").markdown("💭 **IA pensando...**")
    messages.append(("system", "💭 **IA pensando...**"))

    answer = chat.send_message(prompt).text
    st.chat_message("Gemini").markdown(answer)
    messages.append(("bot", answer))

    # Tokens
    tokens_entrada = estimar_tokens(prompt)
    tokens_saida = estimar_tokens(answer)
    tokens_rodada = tokens_entrada + tokens_saida
    total_tokens += tokens_rodada
    st.session_state["total_tokens"] = total_tokens

    st.markdown(
        f"<div style='color: gray; font-size: small;'>"
        f"Rodada: {int(tokens_rodada)} "
        f"Total: {int(total_tokens)}"
        f"</div>",
        unsafe_allow_html=True
    )

    # Agora sempre executa qualquer código, e reanalisa
    executar_codigos(answer)

#Adicionado pelo script de análise
