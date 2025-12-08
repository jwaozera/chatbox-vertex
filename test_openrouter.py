import requests

OPENROUTER_API_KEY = "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"

response = requests.get(
    "https://openrouter.ai/api/v1/models",
    headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}"
    }
)

models = response.json()

# Filtrar modelos gratuitos
free_models = [
    m for m in models['data'] 
    if m.get('pricing', {}).get('prompt', '0') == '0'
]

print("Modelos Gratuitos Disponíveis:")
for model in free_models:
    print(f"- {model['id']}")
