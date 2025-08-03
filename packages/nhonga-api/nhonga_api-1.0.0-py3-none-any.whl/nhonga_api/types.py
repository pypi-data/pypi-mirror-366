"""
Tipos e classes para a API Nhonga
"""

from typing import Optional, Literal, TypedDict
from enum import Enum


class PaymentStatus(str, Enum):
    """Status possíveis de um pagamento"""
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    """Métodos de pagamento suportados"""
    MPESA = "mpesa"
    EMOLA = "emola"


class Currency(str, Enum):
    """Moedas suportadas"""
    MZN = "MZN"
    USD = "USD"


class Environment(str, Enum):
    """Ambientes disponíveis"""
    PRODUCTION = "prod"
    DEVELOPMENT = "dev"


class NhongaConfig(TypedDict):
    """Configuração para inicializar a API Nhonga"""
    api_key: str
    secret_key: Optional[str]
    base_url: Optional[str]


class CreatePaymentRequest(TypedDict, total=False):
    """Requisição para criar um pagamento"""
    amount: int
    context: str
    callbackUrl: Optional[str]
    returnUrl: Optional[str]
    currency: Optional[Currency]
    enviroment: Optional[Environment]


class CreatePaymentResponse(TypedDict):
    """Resposta da criação de pagamento"""
    success: bool
    error: Optional[str]
    redirectUrl: Optional[str]
    id: Optional[str]


class PaymentStatusRequest(TypedDict):
    """Requisição para verificar status de pagamento"""
    id: str


class PaymentStatusResponse(TypedDict):
    """Resposta do status de pagamento"""
    success: bool
    status: PaymentStatus
    amount: int
    tax: int
    method: str
    currency: str


class MobilePaymentRequest(TypedDict):
    """Requisição para pagamento mobile"""
    method: PaymentMethod
    amount: int
    context: str
    useremail: str
    userwhatsApp: str
    phone: str


class MobilePaymentResponse(TypedDict):
    """Resposta do pagamento mobile"""
    success: bool
    error: Optional[str]
    id: Optional[str]
    currency: Optional[str]


class WebhookPayload(TypedDict):
    """Payload recebido via webhook"""
    id: str
    productId: str
    method: str
    paid: int
    received: int
    fee: int
    context: str


class NhongaError(Exception):
    """Exceção específica para erros da API Nhonga"""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
    
    def __str__(self) -> str:
        if self.status_code:
            return f"NhongaError({self.status_code}): {self.message}"
        return f"NhongaError: {self.message}"

