# Aplicación Flask

## Requisitos

- Python 3.9 o posterior

## Iniciar en Windows

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py
```

Abre <http://127.0.0.1:5000> en el navegador. El endpoint `/health` responde con `{"status":"ok"}`.
