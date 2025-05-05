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

# Lista para guardar as instâncias das IAs
comite_ias = []

# ───────────────────────────── 2) Funções
def limpar_ansi(texto):
    texto = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', texto)
    linhas = texto.splitlines()
    linhas_limpa = [linha for linha in linhas if linha.strip()]
    return "\n".join(linhas_limpa)

def estimar_tokens(texto):
    return len(texto) / 4  # Aproximação: 1 token ≈ 4 caracteres

def ia_generator(contexto_inicial):
    chat_novo = model.start_chat()
    resposta_instrucao = chat_novo.send_message(contexto_inicial).text
    comite_ias.append(chat_novo)  # Adiciona a IA no comitê
    return chat_novo


def ai_analysis(entrada_usuario):
    analise_msg = "🔎 **Analisando a entrada pelo comitê...**"
    st.chat_message("💭 Sistema").markdown(analise_msg)
    messages.append(("system", analise_msg))

    nova_resposta = entrada_usuario  # Começa com o prompt

    respostas_comite = []

    for idx, ia in enumerate(comite_ias):
        resposta_ia = ia.send_message(nova_resposta).text

        # Exibe a resposta
        st.chat_message("Gemini").markdown(
            f"**Resposta da IA {idx+1}:**\n\n{resposta_ia}"
        )
        
        messages.append(("bot", f"**Resposta da IA {idx+1}:**\n\n{resposta_ia}"))

        # ✅ NOVO: Verifica se essa resposta tem bloco de código
        if "```python" in resposta_ia:
            executar_codigos(resposta_ia)
            # ⚡⚡ Continua o loop, não interrompe mais!
        
        # Atualiza para a próxima IA trabalhar sobre a resposta anterior
        nova_resposta = resposta_ia
        respostas_comite.append(resposta_ia)

    # Depois de TODAS as IAs (independente de códigos encontrados), atualiza tokens
    tokens_saida_follow = estimar_tokens(nova_resposta)
    total_tokens = st.session_state.get("total_tokens", 0) + tokens_saida_follow
    st.session_state["total_tokens"] = total_tokens

    st.markdown(
        f"<div style='color: gray; font-size: small;'>"
        f"Rodada: {int(tokens_saida_follow)} ｜ Total: {int(total_tokens)}"
        f"</div>",
        unsafe_allow_html=True
    )


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

        ai_analysis(saida_final_limpa)

    if os.path.exists(saida_arquivo):
        os.remove(saida_arquivo)
    if os.path.exists(script_temp):
        os.remove(script_temp)

# ───────────────────────────── 3) Estado persistente
# ───────────────────────────── 3) Estado persistente (adaptado para duas IAs)
if "chat" not in st.session_state:
    # Cria o comitê com duas IAs
    
    # IA 1 - Visionário Criativo
    contexto_criativo = (
        "Você é um assistente de programação com perfil Visionário Criativo.\n"
        "Sua missão é gerar ideias novas, propor soluções inovadoras e ousadas.\n"
        "Você deve incentivar abordagens fora do convencional.\n"
        "Aceita certo grau de risco e imperfeição, priorizando inovação sobre conservadorismo.\n"
        "Seja livre, inventivo e sempre proponha algo novo, mesmo que seja improvável."
    )
    ia_generator(contexto_criativo)

    # IA 2 - Analista Crítico
    contexto_critico = (
        "Você é um assistente de programação com perfil Analista Crítico.\n"
        "Sua missão é revisar cuidadosamente as soluções, buscando falhas, incoerências e riscos.\n"
        "Você deve ser rigoroso, técnico e meticuloso.\n"
        "Questione tudo que parecer impraticável ou mal fundamentado.\n"
        "Seja frio, lógico e priorize a solidez sobre a ousadia."
    )
    ia_generator(contexto_critico)

# Define o chat principal como a primeira IA (Visionário Criativo)
chat = comite_ias[0]
messages = st.session_state.setdefault("messages", [])
total_tokens = st.session_state.setdefault("total_tokens", 0)


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

    # Envia o prompt diretamente para o comitê
    ai_analysis(prompt)
