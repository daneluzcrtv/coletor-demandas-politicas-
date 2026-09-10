import React, { useEffect, useState, useCallback } from "react";
import { api } from "../api";

const BADGE = {
  aberta: "badge badge-aberta",
  em_andamento: "badge badge-andamento",
  concluida: "badge badge-concluida",
};

const CATEGORIAS = [
  "infraestrutura","saude","educacao","iluminacao",
  "seguranca","transporte","meio_ambiente","assistencia_social","outro",
];

export default function Historico() {
  const [demandas, setDemandas] = useState([]);
  const [bairros, setBairros] = useState([]);
  const [filtros, setFiltros] = useState({});
  const [carregando, setCarregando] = useState(true);

  const carregar = useCallback(async () => {
    setCarregando(true);
    try {
      const data = await api.demandas.listar(filtros);
      setDemandas(data);
    } finally {
      setCarregando(false);
    }
  }, [filtros]);

  useEffect(() => { carregar(); }, [carregar]);
  useEffect(() => { api.bairros.listar().then(setBairros); }, []);

  function setFiltro(campo, valor) {
    setFiltros(prev => ({ ...prev, [campo]: valor || undefined }));
  }

  // Agrupa por mês para exibir linha do tempo
  const porMes = demandas.reduce((acc, d) => {
    const mes = new Date(d.data_abertura).toLocaleDateString("pt-BR", { month: "long", year: "numeric" });
    if (!acc[mes]) acc[mes] = [];
    acc[mes].push(d);
    return acc;
  }, {});

  return (
    <>
      <h2 className="page-title">Histórico</h2>
      <p className="page-subtitle">Linha do tempo de demandas por período</p>

      <div className="filtros" style={{ marginBottom: 24 }}>
        <select onChange={e => setFiltro("status", e.target.value)}>
          <option value="">Todos os status</option>
          <option value="aberta">Aberta</option>
          <option value="em_andamento">Em andamento</option>
          <option value="concluida">Concluída</option>
        </select>

        <select onChange={e => setFiltro("bairro_id", e.target.value)}>
          <option value="">Todos os bairros</option>
          {bairros.map(b => <option key={b.id} value={b.id}>{b.nome}</option>)}
        </select>

        <select onChange={e => setFiltro("categoria", e.target.value)}>
          <option value="">Todas as categorias</option>
          {CATEGORIAS.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      {carregando ? (
        <p className="muted">Carregando...</p>
      ) : demandas.length === 0 ? (
        <p className="muted">Nenhuma demanda encontrada.</p>
      ) : (
        Object.entries(porMes).map(([mes, items]) => (
          <div key={mes} style={{ marginBottom: 32 }}>
            {/* Cabeçalho do mês */}
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
              <span style={{ fontWeight: 700, fontSize: 15 }}>{mes}</span>
              <span className="badge" style={{ background: "var(--surface-2)", color: "var(--muted)" }}>
                {items.length} demanda{items.length !== 1 ? "s" : ""}
              </span>
            </div>

            {/* Timeline */}
            <div style={{ borderLeft: "2px solid var(--border)", paddingLeft: 20, display: "flex", flexDirection: "column", gap: 12 }}>
              {items.map(d => (
                <div key={d.id} style={{ position: "relative" }}>
                  {/* Ponto na linha */}
                  <div style={{
                    position: "absolute", left: -26, top: 14,
                    width: 10, height: 10, borderRadius: "50%",
                    background: d.status === "concluida" ? "var(--status-concluida)" : d.status === "em_andamento" ? "var(--status-andamento)" : "var(--status-aberta)",
                    border: "2px solid var(--bg)",
                    boxShadow: "0 0 0 2px var(--border)",
                  }} />

                  <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, padding: "12px 16px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8, flexWrap: "wrap" }}>
                      <div>
                        <span style={{ fontFamily: "monospace", fontSize: 12, color: "var(--muted)" }}>#{d.protocolo}</span>
                        {d.categoria && (
                          <span className="badge" style={{ background: "var(--surface-2)", color: "var(--muted)", marginLeft: 8 }}>{d.categoria}</span>
                        )}
                      </div>
                      <span className={BADGE[d.status] ?? "badge"}>{d.status.replace("_", " ")}</span>
                    </div>

                    <p style={{ margin: "6px 0 4px", fontSize: 14 }}>
                      {d.resumo || d.descricao?.slice(0, 120)}
                    </p>

                    <div style={{ fontSize: 12, color: "var(--muted)", display: "flex", gap: 12 }}>
                      <span>{new Date(d.data_abertura).toLocaleDateString("pt-BR")}</span>
                      {bairros.find(b => b.id === d.bairro_id)?.nome && (
                        <span>📍 {bairros.find(b => b.id === d.bairro_id)?.nome}</span>
                      )}
                      {d.data_conclusao && (
                        <span>✅ Concluída em {new Date(d.data_conclusao).toLocaleDateString("pt-BR")}</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))
      )}
    </>
  );
}
