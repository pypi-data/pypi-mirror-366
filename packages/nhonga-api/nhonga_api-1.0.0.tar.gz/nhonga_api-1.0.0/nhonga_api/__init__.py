"""
Nhonga API - Biblioteca Python para integração com a API Nhonga.net
"""

from .client import NhongaAPI
from .types import (
    NhongaConfig,
    CreatePaymentRequest,
    CreatePaymentResponse,
    PaymentStatusRequest,
    PaymentStatusResponse,
    MobilePaymentRequest,
    MobilePaymentResponse,
    WebhookPayload,
    NhongaError,
    PaymentStatus,
    PaymentMethod,
    Currency,
    Environment
)

__version__ = "1.0.0"
__author__ = "Nhonga API Library"
__email__ = "suporte@nhonga.net"

__all__ = [
    "NhongaAPI",
    "NhongaConfig",
    "CreatePaymentRequest",
    "CreatePaymentResponse",
    "PaymentStatusRequest",
    "PaymentStatusResponse",
    "MobilePaymentRequest",
    "MobilePaymentResponse",
    "WebhookPayload",
    "NhongaError",
    "PaymentStatus",
    "PaymentMethod",
    "Currency",
    "Environment"
]

