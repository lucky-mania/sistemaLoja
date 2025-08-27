from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class User:
    id: Optional[int] = None
    nome: str = ""
    email: str = ""
    senha_hash: str = ""
    criado_em: Optional[datetime] = None

@dataclass
class Product:
    id: Optional[int] = None
    nome: str = ""
    categoria: str = ""
    quantidade: int = 0
    valor_compra: float = 0.0
    valor_venda: float = 0.0
    data_entrada: Optional[str] = None
    criado_em: Optional[datetime] = None

@dataclass
class Sale:
    id: Optional[int] = None
    produto_id: int = 0
    quantidade: int = 0
    valor_venda: float = 0.0
    data_venda: Optional[str] = None
    criado_em: Optional[datetime] = None
    produto_nome: Optional[str] = None
