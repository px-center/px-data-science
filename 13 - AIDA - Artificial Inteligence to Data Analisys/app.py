import os, re, subprocess, time, uuid, glob, shutil
import streamlit as st
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from src.libs.lib import * 

# ───────────────────────────── 1) Configuração inicial
st.set_page_config(page_title="Gemini Chat", page_icon="🤖")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ".formal-purpose-354320-af3d391f5234.json"
PROJECT_ID = "formal-purpose-354320"
LOCATION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
MODEL_ID = "gemini-2.0-flash"

vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel(MODEL_ID)

# Diretórios de imagem
TMP_DIR = "src/data/tmp"
SHOW_DIR = "src/data/tmp/show"
os.makedirs(TMP_DIR, exist_ok=True)
os.makedirs(SHOW_DIR, exist_ok=True)

def limpar_ansi(texto):
    texto = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', texto)
    linhas = texto.splitlines()
    return "\n".join([l for l in linhas if l.strip()])

def estimar_tokens(texto):
    return len(texto) / 4

def executar_codigos(texto, profundidade=0, max_profundidade=50000):
    if profundidade >= max_profundidade:
        st.warning("🔄 Limite máximo de ciclos de execução atingido!")
        return

    python_blocks = re.findall(r"```python\s+(.*?)```", texto, re.DOTALL | re.IGNORECASE)
    sql_blocks = re.findall(r"```sql\s+(.*?)```", texto, re.DOTALL | re.IGNORECASE)

    saida_final = ""

    # 🔵 1) Executar Python
    if python_blocks:
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
                saida_final += f.read()
            os.remove(saida_arquivo)

        if os.path.exists(script_temp):
            os.remove(script_temp)

        # 🖼️ Exibir imagens geradas
        imagens = glob.glob(os.path.join(TMP_DIR, "*.png"))
        for img_path in sorted(imagens):
            nome = os.path.basename(img_path)
            destino = os.path.join(SHOW_DIR, nome)
            destino_abs = os.path.abspath(destino)
            shutil.move(img_path, destino_abs)
            st.image(destino_abs, caption=os.path.basename(destino_abs), use_column_width=True)
            messages.append(("imagem", destino_abs))

    # 🔵 2) Executar SQL logo após o Python
    if sql_blocks:
        for sql in sql_blocks:
            messages.append(("execucao", "📦 **Executando bloco SQL...**"))
            try:
                resultado_sql = run_query(sql.strip())
                if isinstance(resultado_sql, pd.DataFrame):
                    st.dataframe(resultado_sql.head(100))
                    saida_final += resultado_sql.to_string()
                else:
                    st.error(resultado_sql)
                    saida_final += str(resultado_sql)
            except Exception as e:
                erro_sql = f"Erro ao executar bloco SQL: {e}"
                st.error(erro_sql)
                saida_final += erro_sql

    # 🔵 3) Pós-processamento com Gemini
    if saida_final:
        saida_final_limpa = limpar_ansi(saida_final)
        st.chat_message("💭 Sistema").markdown("🔎 **Analisando resultados da execução...**")
        messages.append(("system", "🔎 **Analisando resultados da execução...**"))

        nova_resposta = chat.send_message(saida_final_limpa).text
        st.chat_message("Gemini").markdown(nova_resposta)
        messages.append(("bot", nova_resposta))

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

        # 🔵 4) Verifica se a nova resposta trouxe mais blocos
        python_blocks = re.findall(r"```python\s+(.*?)```", nova_resposta, re.DOTALL | re.IGNORECASE)
        sql_blocks = re.findall(r"```sql\s+(.*?)```", nova_resposta, re.DOTALL | re.IGNORECASE)
        if python_blocks or sql_blocks:
            executar_codigos(nova_resposta, profundidade=profundidade+1, max_profundidade=max_profundidade)

    if profundidade >= max_profundidade:
        st.warning("🔄 Limite máximo de ciclos de execução atingido!")
        return

    python_blocks = re.findall(r"```python\s+(.*?)```", texto, re.DOTALL | re.IGNORECASE)
    sql_blocks = re.findall(r"```sql\s+(.*?)```", texto, re.DOTALL | re.IGNORECASE)
    saida_final = ""

    # Executar blocos Python
    if python_blocks:
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
                saida_final += f.read()
            os.remove(saida_arquivo)

        if os.path.exists(script_temp):
            os.remove(script_temp)

        imagens = glob.glob(os.path.join(TMP_DIR, "*.png"))
        for img_path in sorted(imagens):
            nome = os.path.basename(img_path)
            destino = os.path.join(SHOW_DIR, nome)
            destino_abs = os.path.abspath(destino)
            shutil.move(img_path, destino_abs)

            # Exibe imediatamente no fluxo atual
            st.image(destino_abs, caption=os.path.basename(destino_abs), use_column_width=True)

            # Também salva no histórico
            messages.append(("imagem", destino_abs))


    # Executar blocos SQL
    if sql_blocks:
        for sql in sql_blocks:
            messages.append(("execucao", "📦 **Executando bloco SQL...**"))
            try:
                resultado_sql = run_query(sql.strip())
                if isinstance(resultado_sql, pd.DataFrame):
                    st.dataframe(resultado_sql.head(100))  # head(100) aqui
                    saida_final += resultado_sql.to_string()
                else:
                    st.error(resultado_sql)
                    saida_final += str(resultado_sql)
            except Exception as e:
                erro_sql = f"Erro ao executar bloco SQL: {e}"
                st.error(erro_sql)
                saida_final += erro_sql

    # Pós-processamento
    if saida_final:
        saida_final_limpa = limpar_ansi(saida_final)
        st.chat_message("💭 Sistema").markdown("🔎 **Analisando resultados da execução...**")
        messages.append(("system", "🔎 **Analisando resultados da execução...**"))

        nova_resposta = chat.send_message(saida_final_limpa).text
        st.chat_message("Gemini").markdown(nova_resposta)
        messages.append(("bot", nova_resposta))

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


        python_blocks = re.findall(r"```python\s+(.*?)```", nova_resposta, re.DOTALL | re.IGNORECASE)
        sql_blocks = re.findall(r"```sql\s+(.*?)```", nova_resposta, re.DOTALL | re.IGNORECASE)
        if python_blocks or sql_blocks:
            executar_codigos(nova_resposta, profundidade=profundidade+1, max_profundidade=max_profundidade)

# ───────────────────────────── 3) Estado persistente
chat = st.session_state.setdefault("chat", model.start_chat())
chat_motivador = st.session_state.setdefault("chat_motivador", model.start_chat())
messages = st.session_state.setdefault("messages", [])
total_tokens = st.session_state.setdefault("total_tokens", 0)

# ───────────────────────────── 3.1) Instrução inicial
if "instrucoes_enviadas" not in st.session_state:
    instrucao_inicial = (
        "Você é um assistente de programação especializado em Python e SQL (PostgreSQL).\n"
        "Seu objetivo é ajudar o usuário a criar, melhorar e executar códigos nessas linguagens.\n"
        "Sempre que gerar código Python, escreva-o em blocos entre crases com o identificador 'python'.\n"
        "Sempre que gerar código SQL, escreva-o em blocos entre crases com o identificador 'sql'.\n"
        "Se precisar fazer análises de resultados, seja direto e claro nas instruções.\n"
        "Responda apenas com informações técnicas, evitando floreios, enfeites ou linguagem desnecessária.\n"
        "Seja objetivo, técnico e profissional em todas as respostas."
        "Usar esta função em python para executar queries: run_query(sql_query: str)"
        "Quando gerar gráficos em python sempre salvar em ./src/data/tmp/"
    )

    resposta_instrucao = chat.send_message(instrucao_inicial).text
    messages.append(("system", instrucao_inicial))
    messages.append(("bot", resposta_instrucao))
    st.session_state["instrucoes_enviadas"] = True

# ───────────────────────────── 4) Cabeçalho
st.title("🗨️ Gemini Chatbot")
st.caption(f"Modelo: **{MODEL_ID}** ｜ Projeto: **{PROJECT_ID}**")
st.markdown("---")

# ───────────────────────────── 5) Histórico (texto + imagens)
for role, txt in messages:
    if role == "imagem":
        st.image(txt, caption=os.path.basename(txt))
        continue
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

    executar_codigos(answer)
