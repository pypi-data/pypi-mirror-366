# Nhonga API - Python Library

Biblioteca Python para integração com a API de pagamentos da Nhonga.net.

## Instalação

```bash
pip install nhonga-api
```

## Configuração

```python
from nhonga_api import NhongaAPI

nhonga = NhongaAPI({
    "api_key": "SUA_CHAVE_API",
    "secret_key": "SUA_CHAVE_SECRETA",  # Opcional, necessária para webhooks
    "base_url": "https://nhonga.net/api/"  # Opcional, padrão já configurado
})
```

## Uso

### Criar Pagamento

```python
from nhonga_api import NhongaAPI, NhongaError, Currency, Environment

try:
    payment = nhonga.create_payment({
        "amount": 1500,
        "context": "Pagamento do curso de programação",
        "callbackUrl": "https://seusite.com/webhook",
        "returnUrl": "https://seusite.com/obrigado",
        "currency": Currency.MZN,
        "enviroment": Environment.PRODUCTION
    })

    if payment["success"]:
        print("URL de redirecionamento:", payment["redirectUrl"])
        print("ID da transação:", payment["id"])
    else:
        print("Erro:", payment["error"])
        
except NhongaError as e:
    print("Erro da API Nhonga:", e)
```

### Verificar Status do Pagamento

```python
try:
    status = nhonga.get_payment_status({
        "id": "txn_123456789"
    })

    print("Status:", status["status"])
    print("Valor:", status["amount"])
    print("Método:", status["method"])
    print("Taxa:", status["tax"])
    
except NhongaError as e:
    print("Erro ao verificar status:", e)
```

### Pagamento Direto Mobile

```python
from nhonga_api import PaymentMethod

try:
    mobile_payment = nhonga.create_mobile_payment({
        "method": PaymentMethod.MPESA,
        "amount": 2500,
        "context": "Recarga de saldo",
        "useremail": "cliente@exemplo.com",
        "userwhatsApp": "841234567",
        "phone": "841416077"
    })

    if mobile_payment["success"]:
        print("ID da transação:", mobile_payment["id"])
    else:
        print("Erro:", mobile_payment["error"])
        
except NhongaError as e:
    print("Erro no pagamento mobile:", e)
```

### Processamento de Webhooks

#### Com Flask

```python
from flask import Flask, request, jsonify
from nhonga_api import NhongaAPI, NhongaError

app = Flask(__name__)
nhonga = NhongaAPI({"api_key": "SUA_CHAVE_API", "secret_key": "SUA_CHAVE_SECRETA"})

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        secret_key = request.headers.get('secretkey')
        payload = request.get_json()

        def processar_pagamento(webhook_data):
            print("Pagamento confirmado:", webhook_data["id"])
            print("Valor pago:", webhook_data["paid"])
            print("Valor recebido:", webhook_data["received"])
            print("Taxa:", webhook_data["fee"])
            
            # Processar o pagamento confirmado
            # Atualizar banco de dados, enviar email, etc.

        nhonga.process_webhook(payload, secret_key, processar_pagamento)
        return jsonify({"status": "success"}), 200
        
    except NhongaError as e:
        print("Webhook inválido:", e)
        return jsonify({"error": "Invalid webhook"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
```

#### Com FastAPI

```python
from fastapi import FastAPI, Request, HTTPException, Header
from nhonga_api import NhongaAPI, NhongaError
from typing import Optional

app = FastAPI()
nhonga = NhongaAPI({"api_key": "SUA_CHAVE_API", "secret_key": "SUA_CHAVE_SECRETA"})

@app.post("/webhook")
async def webhook(request: Request, secretkey: Optional[str] = Header(None)):
    try:
        if not secretkey:
            raise HTTPException(status_code=400, detail="Missing secret key")
        
        payload = await request.json()

        def processar_pagamento(webhook_data):
            print("Pagamento confirmado:", webhook_data["id"])
            # Processar pagamento...

        nhonga.process_webhook(payload, secretkey, processar_pagamento)
        return {"status": "success"}
        
    except NhongaError as e:
        raise HTTPException(status_code=400, detail="Invalid webhook")

# Para executar: uvicorn main:app --host 0.0.0.0 --port 3000
```

## Tipos e Enums

A biblioteca inclui tipos e enums para melhor experiência de desenvolvimento:

```python
from nhonga_api import (
    PaymentStatus,
    PaymentMethod, 
    Currency,
    Environment,
    CreatePaymentRequest,
    PaymentStatusResponse,
    MobilePaymentRequest,
    WebhookPayload
)

# Enums disponíveis
PaymentStatus.PENDING     # "pending"
PaymentStatus.COMPLETED   # "completed"
PaymentStatus.CANCELLED   # "cancelled"

PaymentMethod.MPESA       # "mpesa"
PaymentMethod.EMOLA       # "emola"

Currency.MZN              # "MZN"
Currency.USD              # "USD"

Environment.PRODUCTION    # "prod"
Environment.DEVELOPMENT   # "dev"
```

## Context Manager

Use context manager para gerenciamento automático de recursos:

```python
with NhongaAPI({"api_key": "SUA_CHAVE_API"}) as nhonga:
    payment = nhonga.create_payment({
        "amount": 1000,
        "context": "Teste de pagamento",
        "enviroment": Environment.DEVELOPMENT
    })
    print("Pagamento criado:", payment["id"])
```

## Tratamento de Erros

A biblioteca usa a classe `NhongaError` para erros específicos da API:

```python
from nhonga_api import NhongaError

try:
    payment = nhonga.create_payment(payment_data)
except NhongaError as e:
    print("Erro da API Nhonga:", e.message)
    print("Código de status:", e.status_code)
except Exception as e:
    print("Erro inesperado:", e)
```

## Ambiente de Desenvolvimento

Para testes, use `Environment.DEVELOPMENT` nas requisições de pagamento:

```python
from nhonga_api import Environment

payment = nhonga.create_payment({
    "amount": 1000,
    "context": "Teste de pagamento",
    "enviroment": Environment.DEVELOPMENT  # Não gera cobrança real
})
```

## Exemplos Completos

Veja o arquivo `examples.py` para exemplos completos de uso com Flask, FastAPI e outras funcionalidades.

## Requisitos

- Python 3.7+
- requests >= 2.25.0
- typing-extensions >= 4.0.0

## Desenvolvimento

Para contribuir com o desenvolvimento:

```bash
# Clonar repositório
git clone https://github.com/nhonga/nhonga-python
cd nhonga-python

# Instalar dependências de desenvolvimento
pip install -e ".[dev]"

# Executar testes
pytest

# Verificar tipos
mypy nhonga_api

# Formatar código
black nhonga_api
```

## Suporte

Para suporte técnico, entre em contato:
- Email: support@nhonga.net
- Documentação: https://nhonga.net/api-docs

## Licença

MIT

