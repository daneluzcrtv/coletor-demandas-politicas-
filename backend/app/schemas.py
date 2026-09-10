from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ── Assessor ──────────────────────────────────────────────────────────────────

class AssessorBase(BaseModel):
    nome: str
    telefone: Optional[str] = None
    email: Optional[str] = None
    areas_tematicas: Optional[list[str]] = None
    ativo: bool = True


class AssessorCreate(AssessorBase):
    pass


class AssessorUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    areas_tematicas: Optional[list[str]] = None
    ativo: Optional[bool] = None


class AssessorOut(AssessorBase):
    id: int

    model_config = {"from_attributes": True}


# ── Bairro ────────────────────────────────────────────────────────────────────

class BairroBase(BaseModel):
    nome: str
    zona: Optional[str] = None
    assessor_responsavel_id: Optional[int] = None


class BairroCreate(BairroBase):
    pass


class BairroUpdate(BaseModel):
    nome: Optional[str] = None
    zona: Optional[str] = None
    assessor_responsavel_id: Optional[int] = None


class BairroOut(BairroBase):
    id: int

    model_config = {"from_attributes": True}


# ── Cidadao ───────────────────────────────────────────────────────────────────

class CidadaoBase(BaseModel):
    nome: str
    wa_id: Optional[str] = None
    telefone: Optional[str] = None
    endereco_texto: Optional[str] = None
    bairro_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CidadaoCreate(CidadaoBase):
    pass


class CidadaoUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    endereco_texto: Optional[str] = None
    bairro_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CidadaoOut(CidadaoBase):
    id: int
    total_demandas: int
    data_cadastro: datetime

    model_config = {"from_attributes": True}


# ── Demanda ───────────────────────────────────────────────────────────────────

class DemandaBase(BaseModel):
    descricao: str
    cidadao_id: Optional[int] = None
    bairro_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    canal_origem: str = "whatsapp"


class DemandaCreate(DemandaBase):
    pass


class DemandaUpdate(BaseModel):
    status: Optional[str] = None
    assessor_responsavel_id: Optional[int] = None
    bairro_id: Optional[int] = None
    categoria: Optional[str] = None
    resumo: Optional[str] = None
    data_conclusao: Optional[datetime] = None


class DemandaOut(DemandaBase):
    id: int
    categoria: Optional[str]
    resumo: Optional[str]
    status: str
    assessor_responsavel_id: Optional[int]
    protocolo: Optional[str]
    data_abertura: datetime
    data_conclusao: Optional[datetime]

    model_config = {"from_attributes": True}
