FROM python:3.12-slim

WORKDIR /app

COPY api/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY api/ /app/api/

# Moteur IA distant (Hugging Face) + fichiers catalogue (sans le gros modèle .gguf local)
COPY ia-reco/Ia_recom_mistral_distant.py ia-reco/exercices.txt ia-reco/materiels.txt ia-reco/exercice_materiel.txt /app/ia-reco/

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
