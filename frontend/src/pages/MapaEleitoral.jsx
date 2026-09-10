import React, { useEffect, useState } from "react";
import { api } from "../api";

function corUrgencia(urgencia) {
  if (urgencia > 0.7) return "#dc2626";
  if (urgencia > 0.5) return "#ef4444";
  if (urgencia > 0.3) return "#f97316";
  if (urgencia > 0)   return "#f59e0b";
  return "#22c55e";
}

export default function MapaEleitoral() {
  const [demandas, setDemandas]     = useState([]);
  const [bairros, setBairros]       = useState([]);
  const [filtroZona, setFiltroZona] = useState("todas");
  const [ordenar, setOrdenar]       = useState("total");
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    Promise.all([api.demandas.listar({}), api.bairros.listar()])
      .then(([d, b]) => { setDemandas(d ?? []); setBairros(b ?? []); setCarregando(false); })
      .catch(() => setCarregando(false));
  }, []);

  const stats = bairros
    .map(b => {
      const dems = demandas.filter(d => d.bairro_id === b.id);
      const abertas    = dems.filter(d => d.status === "aberta").length;
      const andamento  = dems.filter(d => d.status === "em_andamento").length;
      const concluidas = dems.filter(d => d.status === "concluida").length;
      const total      = dems.length;
      const urgencia   = total > 0 ? abertas / total : 0;
      return { ...b, total, abertas, andamento, concluidas, urgencia };
    })
    .filter(b => b.total > 0)
    .filter(b => filtroZona === "todas" || b.zona === filtroZona);

  const sorted = [...stats].sort((a, b) => {
    if (ordenar === "total")    return b.total - a.total;
    if (ordenar === "abertas")  return b.abertas - a.abertas;
    if (ordenar === "urgencia") return b.urgencia - a.urgencia;
    return a.nome.localeCompare(b.nome);
  });

  const maxTotal = stats.reduce((m, b) => Math.max(m, b.total), 1);
  const totalGeral = stats.reduce((s, b) => s + b.total, 0);
  const zonas = [...new Set(bairros.map(b => b.zona).filter(Boolean))].sort();

  // Resumo por zona
  const resumoZona = zonas.map(zona => {
    const bZona = stats.filter(b => b.zona === zona);
    return {
      zona,
      total:      bZona.reduce((s, b) => s + b.total, 0),
      abertas:    bZona.reduce((s, b) => s + b.abertas, 0),
      bairros:    bZona.length,
    };
  }).sort((a, b) => b.total - a.total);

  if (carregando) return <p style={{ padding: 24, color: "var(--muted)", fontSize: 13 }}>Carregando...</p>;

  return (
    <>
      <h2 className="page-title">Mapa Eleitoral</h2>
      <p className="page-subtitle">Itapecerica da Serra — ranking de demandas por bairro</p>

      {/* Cards de resumo por zona */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))", gap: 10, marginBottom: 20 }}>
        {resumoZona.map(z => (
          <div key={z.zona}
            onClick={() => setFiltroZona(filtroZona === z.zona ? "todas" : z.zona)}
            style={{
              background: filtroZona === z.zona ? "var(--primary)" : "var(--surface)",
              border: `1px solid ${filtroZona === z.zona ? "var(--primary)" : "var(--border)"}`,
              borderRadius: 10, padding: "12px 14px", cursor: "pointer",
              transition: "all 0.15s",
            }}>
            <div style={{ fontSize: 11, color: filtroZona === z.zona ? "rgba(255,255,255,0.75)" : "var(--muted)", marginBottom: 2 }}>
              Zona {z.zona}
            </div>
            <div style={{ fontSize: 22, fontWeight: 800, color: filtroZona === z.zona ? "#fff" : "var(--text)" }}>
              {z.total}
            </div>
            <div style={{ fontSize: 11, color: filtroZona === z.zona ? "rgba(255,255,255,0.7)" : "var(--muted)" }}>
              {z.bairros} bairro{z.bairros !== 1 ? "s" : ""} · {z.abertas} aberta{z.abertas !== 1 ? "s" : ""}
            </div>
          </div>
        ))}
        <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 10, padding: "12px 14px" }}>
          <div style={{ fontSize: 11, color: "var(--muted)", marginBottom: 2 }}>Total geral</div>
          <div style={{ fontSize: 22, fontWeight: 800, color: "var(--text)" }}>{totalGeral}</div>
          <div style={{ fontSize: 11, color: "var(--muted)" }}>{stats.length} bairros ativos</div>
        </div>
      </div>

      {/* Controles */}
      <div style={{ display: "flex", gap: 10, marginBottom: 14, alignItems: "center", flexWrap: "wrap" }}>
        <select value={filtroZona} onChange={e => setFiltroZona(e.target.value)}
          style={{ fontSize: 13, padding: "6px 10px", borderRadius: 6, border: "1px solid var(--border)", background: "var(--surface)", color: "var(--text)" }}>
          <option value="todas">Todas as zonas</option>
          {zonas.map(z => <option key={z} value={z}>Zona {z}</option>)}
        </select>
        <select value={ordenar} onChange={e => setOrdenar(e.target.value)}
          style={{ fontSize: 13, padding: "6px 10px", borderRadius: 6, border: "1px solid var(--border)", background: "var(--surface)", color: "var(--text)" }}>
          <option value="total">Ordenar por total</option>
          <option value="abertas">Ordenar por abertas</option>
          <option value="urgencia">Ordenar por urgência</option>
          <option value="nome">Ordenar por nome</option>
        </select>
        <span style={{ fontSize: 12, color: "var(--muted)", marginLeft: "auto" }}>
          {sorted.length} bairro{sorted.length !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Tabela de ranking */}
      <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 12, overflow: "hidden" }}>
        {/* Cabeçalho */}
        <div style={{
          display: "grid", gridTemplateColumns: "28px 1fr 80px 70px 70px 80px 120px",
          padding: "10px 16px", borderBottom: "1px solid var(--border)",
          fontSize: 11, color: "var(--muted)", fontWeight: 600, letterSpacing: "0.04em",
          textTransform: "uppercase",
        }}>
          <span>#</span>
          <span>Bairro</span>
          <span style={{ textAlign: "right" }}>Total</span>
          <span style={{ textAlign: "right" }}>Abertas</span>
          <span style={{ textAlign: "right" }}>And.</span>
          <span style={{ textAlign: "right" }}>Conc.</span>
          <span style={{ paddingLeft: 8 }}>Volume</span>
        </div>

        {sorted.length === 0 && (
          <p style={{ padding: 20, fontSize: 13, color: "var(--muted)" }}>Nenhum bairro encontrado.</p>
        )}

        {sorted.map((b, i) => {
          const cor = corUrgencia(b.urgencia);
          const pct = Math.round((b.total / maxTotal) * 100);
          return (
            <div key={b.id} style={{
              display: "grid",
              gridTemplateColumns: "28px 1fr 80px 70px 70px 80px 120px",
              padding: "11px 16px",
              borderBottom: "1px solid var(--border)",
              alignItems: "center",
              transition: "background 0.1s",
            }}
              onMouseEnter={e => e.currentTarget.style.background = "var(--bg)"}
              onMouseLeave={e => e.currentTarget.style.background = ""}
            >
              <span style={{ fontSize: 12, color: "var(--muted)" }}>{i + 1}</span>

              <div>
                <div style={{ fontSize: 13, fontWeight: 500, color: "var(--text)" }}>{b.nome}</div>
                {b.zona && <div style={{ fontSize: 11, color: "var(--muted)" }}>Zona {b.zona}</div>}
              </div>

              <span style={{ textAlign: "right", fontSize: 15, fontWeight: 800, color: "var(--text)" }}>
                {b.total}
              </span>

              <span style={{ textAlign: "right", fontSize: 13, fontWeight: 600, color: "#ef4444" }}>
                {b.abertas}
              </span>

              <span style={{ textAlign: "right", fontSize: 13, color: "#f59e0b" }}>
                {b.andamento}
              </span>

              <span style={{ textAlign: "right", fontSize: 13, color: "#22c55e" }}>
                {b.concluidas}
              </span>

              <div style={{ paddingLeft: 8 }}>
                <div style={{ background: "var(--bg)", borderRadius: 4, height: 6, overflow: "hidden" }}>
                  <div style={{ width: `${pct}%`, height: "100%", borderRadius: 4, background: cor, transition: "width 0.4s" }} />
                </div>
                <div style={{ fontSize: 10, color: "var(--muted)", marginTop: 2 }}>
                  {Math.round(b.urgencia * 100)}% abertas
                </div>
              </div>
            </div>
          );
        })}

        {sorted.length > 0 && (
          <div style={{
            display: "grid", gridTemplateColumns: "28px 1fr 80px 70px 70px 80px 120px",
            padding: "10px 16px", borderTop: "2px solid var(--border)",
            fontSize: 12, fontWeight: 700, color: "var(--text)",
            background: "var(--bg)",
          }}>
            <span />
            <span>Total</span>
            <span style={{ textAlign: "right" }}>{totalGeral}</span>
            <span style={{ textAlign: "right", color: "#ef4444" }}>{stats.reduce((s, b) => s + b.abertas, 0)}</span>
            <span style={{ textAlign: "right", color: "#f59e0b" }}>{stats.reduce((s, b) => s + b.andamento, 0)}</span>
            <span style={{ textAlign: "right", color: "#22c55e" }}>{stats.reduce((s, b) => s + b.concluidas, 0)}</span>
            <span />
          </div>
        )}
      </div>
    </>
  );
}
