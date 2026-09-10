from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, DateTime, Double, ForeignKey,
    Integer, LargeBinary, String, Text, func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Assessor(Base):
    __tablename__ = "assessor"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    telefone: Mapped[Optional[str]] = mapped_column(Text)
    email: Mapped[Optional[str]] = mapped_column(Text)
    areas_tematicas: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    cargo: Mapped[Optional[str]] = mapped_column(Text, default="assessor")
    senha_hash: Mapped[Optional[str]] = mapped_column(Text)

    bairros: Mapped[list["Bairro"]] = relationship(back_populates="assessor_responsavel")
    demandas: Mapped[list["Demanda"]] = relationship(back_populates="assessor_responsavel")


class Bairro(Base):
    __tablename__ = "bairro"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    zona: Mapped[Optional[str]] = mapped_column(Text)
    assessor_responsavel_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("assessor.id")
    )

    assessor_responsavel: Mapped[Optional[Assessor]] = relationship(back_populates="bairros")
    cidadaos: Mapped[list["Cidadao"]] = relationship(back_populates="bairro")
    demandas: Mapped[list["Demanda"]] = relationship(back_populates="bairro")


class Cidadao(Base):
    __tablename__ = "cidadao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    wa_id: Mapped[Optional[str]] = mapped_column(Text, unique=True)  # número WhatsApp (ex: "5511999999999")
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    telefone: Mapped[Optional[str]] = mapped_column(Text)
    endereco_texto: Mapped[Optional[str]] = mapped_column(Text)
    bairro_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("bairro.id"))
    latitude: Mapped[Optional[float]] = mapped_column(Double)
    longitude: Mapped[Optional[float]] = mapped_column(Double)
    total_demandas: Mapped[int] = mapped_column(Integer, default=0)
    data_cadastro: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    bairro: Mapped[Optional[Bairro]] = relationship(back_populates="cidadaos")
    demandas: Mapped[list["Demanda"]] = relationship(back_populates="cidadao")
    interacoes: Mapped[list["InteracaoBot"]] = relationship(back_populates="cidadao")


class Demanda(Base):
    __tablename__ = "demanda"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cidadao_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("cidadao.id"))
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    categoria: Mapped[Optional[str]] = mapped_column(Text)
    resumo: Mapped[Optional[str]] = mapped_column(Text)
    bairro_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("bairro.id"))
    latitude: Mapped[Optional[float]] = mapped_column(Double)
    longitude: Mapped[Optional[float]] = mapped_column(Double)
    status: Mapped[str] = mapped_column(String(20), default="aberta")
    assessor_responsavel_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("assessor.id")
    )
    canal_origem: Mapped[str] = mapped_column(Text, default="whatsapp")
    protocolo: Mapped[Optional[str]] = mapped_column(Text, unique=True)
    data_abertura: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    data_conclusao: Mapped[Optional[datetime]] = mapped_column(DateTime)

    cidadao: Mapped[Optional[Cidadao]] = relationship(back_populates="demandas")
    bairro: Mapped[Optional[Bairro]] = relationship(back_populates="demandas")
    assessor_responsavel: Mapped[Optional[Assessor]] = relationship(back_populates="demandas")
    acompanhamentos: Mapped[list["Acompanhamento"]] = relationship(
        back_populates="demanda", cascade="all, delete-orphan", order_by="Acompanhamento.data"
    )


class InteracaoBot(Base):
    __tablename__ = "interacao_bot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cidadao_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("cidadao.id"))
    mensagem: Mapped[Optional[str]] = mapped_column(Text)
    remetente: Mapped[Optional[str]] = mapped_column(Text)  # 'cidadao' | 'bot'
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    cidadao: Mapped[Optional[Cidadao]] = relationship(back_populates="interacoes")


class Acompanhamento(Base):
    __tablename__ = "acompanhamento"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    demanda_id: Mapped[int] = mapped_column(Integer, ForeignKey("demanda.id"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), default="nota")
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    autor: Mapped[Optional[str]] = mapped_column(Text)
    data: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    demanda: Mapped["Demanda"] = relationship(back_populates="acompanhamentos")
    fotos: Mapped[list["FotoAcompanhamento"]] = relationship(
        back_populates="acompanhamento", cascade="all, delete-orphan"
    )


class FotoAcompanhamento(Base):
    __tablename__ = "foto_acompanhamento"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    acompanhamento_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("acompanhamento.id"), nullable=False
    )
    nome_arquivo: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(Text, default="image/jpeg")
    dados: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    acompanhamento: Mapped[Acompanhamento] = relationship(back_populates="fotos")
