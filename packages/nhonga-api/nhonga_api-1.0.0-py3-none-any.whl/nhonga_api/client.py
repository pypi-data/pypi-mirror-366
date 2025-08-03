"""
Cliente principal para a API Nhonga
"""

import requests
from typing import Optional, Callable, Union, Awaitable
from .types import (
    NhongaConfig,
    CreatePaymentRequest,
    CreatePaymentResponse,
    PaymentStatusRequest,
    PaymentStatusResponse,
    MobilePaymentRequest,
    MobilePaymentResponse,
    WebhookPayload,
    NhongaError
)


class NhongaAPI:
    """Cliente para integração com a API Nhonga.net"""
    
    def __init__(self, config: NhongaConfig):
        """
        Inicializa o cliente da API Nhonga
        
        Args:
            config: Configuração contendo api_key, secret_key (opcional) e base_url (opcional)
        """
        self.api_key = config["api_key"]
        self.secret_key = config.get("secret_key")
        self.base_url = config.get("base_url", "https://nhonga.net/api")
        
        self.session = requests.Session()
        self.session.headers.update({
            "apiKey": self.api_key,
            "Content-Type": "application/json"
        })
        self.session.timeout = 30
    
    def _make_request(self, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
        """
        Faz uma requisição HTTP para a API
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint da API
            data: Dados para enviar no corpo da requisição
            
        Returns:
            Resposta da API como dicionário
            
        Raises:
            NhongaError: Em caso de erro na requisição
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise NhongaError(f"HTTP Error: {e.response.status_code} - {e.response.text}", e.response.status_code)
        except requests.exceptions.ConnectionError:
            raise NhongaError("Connection Error: Unable to connect to Nhonga API")
        except requests.exceptions.Timeout:
            raise NhongaError("Timeout Error: Request timed out")
        except requests.exceptions.RequestException as e:
            raise NhongaError(f"Request Error: {str(e)}")
        except ValueError as e:
            raise NhongaError(f"JSON Decode Error: {str(e)}")
    
    def create_payment(self, request: CreatePaymentRequest) -> CreatePaymentResponse:
        """
        Cria uma nova transação de pagamento
        
        Args:
            request: Dados da requisição de pagamento
            
        Returns:
            Resposta contendo URL de redirecionamento e ID da transação
            
        Raises:
            NhongaError: Em caso de erro na criação do pagamento
        """
        try:
            response = self._make_request("POST", "/payment/create", request)
            return CreatePaymentResponse(response)
        except Exception as e:
            if isinstance(e, NhongaError):
                raise
            raise NhongaError(f"Failed to create payment: {str(e)}")
    
    def get_payment_status(self, request: PaymentStatusRequest) -> PaymentStatusResponse:
        """
        Verifica o status de uma transação
        
        Args:
            request: Requisição contendo o ID da transação
            
        Returns:
            Status atual da transação
            
        Raises:
            NhongaError: Em caso de erro na verificação do status
        """
        try:
            response = self._make_request("POST", "/payment/status", request)
            return PaymentStatusResponse(response)
        except Exception as e:
            if isinstance(e, NhongaError):
                raise
            raise NhongaError(f"Failed to get payment status: {str(e)}")
    
    def create_mobile_payment(self, request: MobilePaymentRequest) -> MobilePaymentResponse:
        """
        Realiza pagamento direto via mobile (M-Pesa/e-Mola)
        
        Args:
            request: Dados do pagamento mobile
            
        Returns:
            Resposta do pagamento mobile
            
        Raises:
            NhongaError: Em caso de erro no pagamento mobile
        """
        try:
            response = self._make_request("POST", "/payment/mobile", request)
            return MobilePaymentResponse(response)
        except Exception as e:
            if isinstance(e, NhongaError):
                raise
            raise NhongaError(f"Failed to create mobile payment: {str(e)}")
    
    def validate_webhook(self, payload: WebhookPayload, received_secret_key: str) -> bool:
        """
        Valida webhook payload usando a chave secreta
        
        Args:
            payload: Dados recebidos no webhook
            received_secret_key: Chave secreta recebida no cabeçalho
            
        Returns:
            True se o webhook for válido, False caso contrário
            
        Raises:
            NhongaError: Se a chave secreta não estiver configurada
        """
        if not self.secret_key:
            raise NhongaError("Secret key not configured for webhook validation")
        return self.secret_key == received_secret_key
    
    def process_webhook(
        self, 
        payload: WebhookPayload, 
        received_secret_key: str,
        callback: Callable[[WebhookPayload], Union[None, Awaitable[None]]]
    ) -> None:
        """
        Processa webhook de forma segura
        
        Args:
            payload: Dados recebidos no webhook
            received_secret_key: Chave secreta recebida no cabeçalho
            callback: Função para processar o webhook válido
            
        Raises:
            NhongaError: Se o webhook for inválido
        """
        if self.validate_webhook(payload, received_secret_key):
            callback(payload)
        else:
            raise NhongaError("Invalid webhook secret key")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.session.close()

