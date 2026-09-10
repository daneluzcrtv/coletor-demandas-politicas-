import React, { useEffect, useState } from "react";
import { api } from "../api";

export default function Relatorio() {
  const mesAtual = new Date().toISOString().slice(0, 7); // "YYYY-MM"
  const [mes, setMes] = useState(mesAtual);
  const [dados, setDados] = useState(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    setCarregando(true);
    api.relatorio.mensal(mes).then((d) => {
      setDados(d);
      setCarregando(false);
    });
  }, [mes]);

  if (carregando) return <p className="muted">Carregando relatório...</p>;

  const t = dados.totais;

  return (
    <>
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 24, flexWrap: "wrap" }}>
        <div>
          <h2 className="page-title">Relatório Mensal</h2>
          <p className="page-subtitle" style={{ margin: 0 }}>Desempenho operacional por período</p>
        </div>
        <input
          type="month"
          value={mes}
          max={mesAtual}
          onChange={(e) => setMes(e.target.value)}
          style={{ border: "1px solid var(--border)", borderRadius: 8, padding: "7px 12px", background: "var(--surface)", color: "var(--text)", marginLeft: "auto" }}
        />
      </div>

      {/* Cards de totais */}
      <div className="cards">
        <Card label="Total de demandas"   value={t.total_demandas}     />
        <Card label="Abertas"             value={t.abertas}            color="var(--status-aberta)"    />
        <Card label="Em andamento"        value={t.em_andamento}       color="var(--status-andamento)" />
        <Card label="Concluídas"          value={t.concluidas}         color="var(--status-concluida)" />
        <Card label="Cidadãos atendidos"  value={t.cidadaos_atendidos} />
        <Card label="Média de resolução"  value={t.media_dias_resolucao != null ? `${t.media_dias_resolucao}d` : "—"} />
      </div>

      <div className="relatorio-grid">
        {/* Por bairro e categoria */}
        <div className="tabela-section">
          <h2>Por bairro e categoria</h2>
          <div className="tabela-wrap">
            <table>
              <thead>
                <tr>
                  <th>Bairro</th>
                  <th>Categoria</th>
                  <th>Total</th>
                  <th>Concluídas</th>
                  <th>Média (dias)</th>
                </tr>
              </thead>
              <tbody>
                {dados.por_bairro_categoria.map((r, i) => (
                  <tr key={i}>
                    <td>{r.bairro}</td>
                    <td>{r.categoria}</td>
                    <td><strong>{r.total}</strong></td>
                    <td>{r.concluidas}</td>
                    <td>{r.media_dias_resolucao ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Por assessor */}
        <div className="tabela-section">
          <h2>Por assessor</h2>
          <div className="tabela-wrap">
            <table>
              <thead>
                <tr>
                  <th>Assessor</th>
                  <th>Total</th>
                  <th>Abertas</th>
                  <th>Andamento</th>
                  <th>Concluídas</th>
                </tr>
              </thead>
              <tbody>
                {dados.por_assessor.map((r, i) => (
                  <tr key={i}>
                    <td>{r.assessor}</td>
                    <td><strong>{r.total}</strong></td>
                    <td style={{ color: "var(--status-aberta)" }}>{r.abertas}</td>
                    <td style={{ color: "var(--status-andamento)" }}>{r.em_andamento}</td>
                    <td style={{ color: "var(--status-concluida)" }}>{r.concluidas}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}

function Card({ label, value, color }) {
  return (
    <div className="card">
      <div className="label">{label}</div>
      <div className="value" style={color ? { color } : {}}>{value ?? "—"}</div>
    </div>
  );
}
