"""
Exemplos de uso da biblioteca Nhonga API Python
"""

import asyncio
from typing import Dict, Any
from nhonga_api import (
    NhongaAPI, 
    NhongaError, 
    CreatePaymentRequest,
    PaymentStatusRequest,
    MobilePaymentRequest,
    WebhookPayload,
    PaymentMethod,
    Currency,
    Environment
)


def exemplo_configuracao():
    """Exemplo de configuração da API"""
    
    # Configuração básica
    nhonga = NhongaAPI({
        "api_key": "SUA_CHAVE_API",
        "secret_key": "SUA_CHAVE_SECRETA",  # Opcional, necessária para webhooks
        "base_url": "https://nhonga.net/api/beta"  # Opcional
    })
    
    return nhonga


def exemplo_create_payment():
    """Exemplo de criação de pagamento"""
    
    nhonga = exemplo_configuracao()
    
    try:
        # Dados do pagamento
        payment_request: CreatePaymentRequest = {
            "amount": 1500,
            "context": "Pagamento do curso de programação",
            "callbackUrl": "https://seusite.com/webhook",
            "returnUrl": "https://seusite.com/obrigado",
            "currency": Currency.MZN,
            "enviroment": Environment.DEVELOPMENT  # Use PRODUCTION para produção
        }
        
        # Criar pagamento
        payment = nhonga.create_payment(payment_request)
        
        if payment["success"]:
            print("✅ Pagamento criado com sucesso!")
            print(f"🔗 URL de redirecionamento: {payment['redirectUrl']}")
            print(f"🆔 ID da transação: {payment['id']}")
            return payment["id"]
        else:
            print(f"❌ Erro ao criar pagamento: {payment['error']}")
            
    except NhongaError as e:
        print(f"🚨 Erro da API Nhonga: {e}")
    except Exception as e:
        print(f"🚨 Erro inesperado: {e}")


def exemplo_verificar_status(transaction_id: str = "txn_123456789"):
    """Exemplo de verificação de status"""
    
    nhonga = exemplo_configuracao()
    
    try:
        # Verificar status
        status_request: PaymentStatusRequest = {"id": transaction_id}
        status = nhonga.get_payment_status(status_request)
        
        print("📊 Status do pagamento:")
        print(f"   Status: {status['status']}")
        print(f"   Valor: {status['amount']} {status['currency']}")
        print(f"   Método: {status['method']}")
        print(f"   Taxa: {status['tax']}")
        
        return status
        
    except NhongaError as e:
        print(f"🚨 Erro ao verificar status: {e}")
    except Exception as e:
        print(f"🚨 Erro inesperado: {e}")


def exemplo_pagamento_mobile():
    """Exemplo de pagamento mobile"""
    
    nhonga = exemplo_configuracao()
    
    try:
        # Dados do pagamento mobile
        mobile_request: MobilePaymentRequest = {
            "method": PaymentMethod.MPESA,
            "amount": 2500,
            "context": "Recarga de saldo",
            "useremail": "cliente@exemplo.com",
            "userwhatsApp": "841234567",
            "phone": "841416077"
        }
        
        # Criar pagamento mobile
        mobile_payment = nhonga.create_mobile_payment(mobile_request)
        
        if mobile_payment["success"]:
            print("✅ Pagamento mobile iniciado!")
            print(f"🆔 ID da transação: {mobile_payment['id']}")
            print(f"💱 Moeda: {mobile_payment['currency']}")
            return mobile_payment["id"]
        else:
            print(f"❌ Erro no pagamento mobile: {mobile_payment['error']}")
            
    except NhongaError as e:
        print(f"🚨 Erro no pagamento mobile: {e}")
    except Exception as e:
        print(f"🚨 Erro inesperado: {e}")


def exemplo_webhook_flask():
    """Exemplo de processamento de webhook com Flask"""
    
    try:
        from flask import Flask, request, jsonify
    except ImportError:
        print("❌ Flask não está instalado. Execute: pip install flask")
        return
    
    app = Flask(__name__)
    nhonga = exemplo_configuracao()
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        try:
            # Obter chave secreta do cabeçalho
            secret_key = request.headers.get('secretkey')
            if not secret_key:
                return jsonify({"error": "Missing secret key"}), 400
            
            # Obter payload
            payload: WebhookPayload = request.get_json()
            
            # Processar webhook
            def processar_pagamento(webhook_data: WebhookPayload):
                print("🎉 Pagamento confirmado!")
                print(f"🆔 ID: {webhook_data['id']}")
                print(f"💰 Valor pago: {webhook_data['paid']}")
                print(f"💵 Valor recebido: {webhook_data['received']}")
                print(f"💸 Taxa: {webhook_data['fee']}")
                print(f"💳 Método: {webhook_data['method']}")
                print(f"📝 Contexto: {webhook_data['context']}")
                
                # Aqui você processaria o pagamento confirmado
                # Exemplo: atualizar banco de dados, enviar email, etc.
            
            nhonga.process_webhook(payload, secret_key, processar_pagamento)
            
            return jsonify({"status": "success"}), 200
            
        except NhongaError as e:
            print(f"🚨 Webhook inválido: {e}")
            return jsonify({"error": "Invalid webhook"}), 400
        except Exception as e:
            print(f"🚨 Erro no webhook: {e}")
            return jsonify({"error": "Internal error"}), 500
    
    print("🚀 Servidor webhook Flask configurado!")
    print("Para executar: app.run(host='0.0.0.0', port=3000)")
    
    return app


def exemplo_webhook_fastapi():
    """Exemplo de processamento de webhook com FastAPI"""
    
    try:
        from fastapi import FastAPI, Request, HTTPException, Header
        from typing import Optional
    except ImportError:
        print("❌ FastAPI não está instalado. Execute: pip install fastapi uvicorn")
        return
    
    app = FastAPI(title="Nhonga Webhook API")
    nhonga = exemplo_configuracao()
    
    @app.post("/webhook")
    async def webhook(
        request: Request,
        secretkey: Optional[str] = Header(None)
    ):
        try:
            if not secretkey:
                raise HTTPException(status_code=400, detail="Missing secret key")
            
            # Obter payload
            payload: WebhookPayload = await request.json()
            
            # Processar webhook
            def processar_pagamento(webhook_data: WebhookPayload):
                print("🎉 Pagamento confirmado!")
                print(f"🆔 ID: {webhook_data['id']}")
                print(f"💰 Valor pago: {webhook_data['paid']}")
                print(f"💵 Valor recebido: {webhook_data['received']}")
                print(f"💸 Taxa: {webhook_data['fee']}")
                print(f"💳 Método: {webhook_data['method']}")
                print(f"📝 Contexto: {webhook_data['context']}")
            
            nhonga.process_webhook(payload, secretkey, processar_pagamento)
            
            return {"status": "success"}
            
        except NhongaError as e:
            print(f"🚨 Webhook inválido: {e}")
            raise HTTPException(status_code=400, detail="Invalid webhook")
        except Exception as e:
            print(f"🚨 Erro no webhook: {e}")
            raise HTTPException(status_code=500, detail="Internal error")
    
    print("🚀 Servidor webhook FastAPI configurado!")
    print("Para executar: uvicorn examples:app --host 0.0.0.0 --port 3000")
    
    return app


def exemplo_context_manager():
    """Exemplo usando context manager"""
    
    with NhongaAPI({
        "api_key": "SUA_CHAVE_API",
        "secret_key": "SUA_CHAVE_SECRETA"
    }) as nhonga:
        
        try:
            # Criar pagamento
            payment = nhonga.create_payment({
                "amount": 1000,
                "context": "Teste com context manager",
                "enviroment": Environment.DEVELOPMENT
            })
            
            print(f"✅ Pagamento criado: {payment['id']}")
            
        except NhongaError as e:
            print(f"🚨 Erro: {e}")


def main():
    """Função principal para executar exemplos"""
    
    print("🧪 Executando exemplos da API Nhonga Python...\n")
    
    # Exemplo 1: Criar pagamento
    print("1️⃣ Criando pagamento...")
    transaction_id = exemplo_create_payment()
    print()
    
    # Exemplo 2: Verificar status
    if transaction_id:
        print("2️⃣ Verificando status...")
        exemplo_verificar_status(transaction_id)
        print()
    
    # Exemplo 3: Pagamento mobile
    print("3️⃣ Pagamento mobile...")
    exemplo_pagamento_mobile()
    print()
    
    # Exemplo 4: Context manager
    print("4️⃣ Context manager...")
    exemplo_context_manager()
    print()
    
    # Exemplo 5: Configurar webhooks
    print("5️⃣ Configurando webhooks...")
    print("Flask app:", exemplo_webhook_flask())
    print("FastAPI app:", exemplo_webhook_fastapi())


if __name__ == "__main__":
    main()

