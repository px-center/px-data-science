virtualenv ../../.pesos_ocorrencias_venv
source ../../.pesos_ocorrencias_venv/bin/activate
../../.pesos_ocorrencias_venv/bin/pip install -r requirements.txt

python -m ipykernel install \
  --user \
  --name .pesos_ocorrencias_venv \
  --display-name "Python (.pesos_ocorrencias_venv)"
