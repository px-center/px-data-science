#!/usr/bin/env sh
# ------------------------------------------------------------
# setup_venv.sh  –  cria/atualiza ../../.aida_env
# ------------------------------------------------------------
set -e  # sai imediatamente se algum comando falhar

VENV_DIR="../../.aida_env"
REQ_FILE="requirements.txt"

# 1) cria o venv se a pasta não existir
if [ ! -d "$VENV_DIR" ]; then
  echo "[setup] Criando virtualenv em $VENV_DIR …"
  python3 -m venv "$VENV_DIR"
fi

# 2) caminho absoluto do pip dentro do venv
PIP="$VENV_DIR/bin/pip"

# 3) garante que pip esteja atualizado
echo "[setup] Atualizando pip …"
"$PIP" install --upgrade pip

# 4) instala / atualiza dependências
echo "[setup] Instalando / atualizando pacotes de $REQ_FILE …"
"$PIP" install -r "$REQ_FILE"

echo "[setup] Ambiente pronto ✅"

