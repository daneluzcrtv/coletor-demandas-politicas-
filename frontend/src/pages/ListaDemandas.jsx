import React, { useEffect, useState, useCallback } from "react";
import { api } from "../api";
import Mapa from "../components/Mapa";
import ModalDemanda from "../components/ModalDemanda";

const CATEGORIAS = [
  "infraestrutura", "saude", "educacao", "iluminacao",
  "seguranca", "transporte", "meio_ambiente", "assistencia_social", "outro",
];

const BADGE = {
  aberta: "badge badge-aberta",
  em_andamento: "badge badge-andamento",
  concluida: "badge badge-concluida",
};

export default function ListaDemandas() {
  const [demandas, setDemandas] = useState([]);
  const [bairros, setBairros] = useState([]);
  const [assessores, setAssessores] = useState([]);
  const [filtros, setFiltros] = useState({});
  const [busca, setBusca] = useState("");
  const [carregando, setCarregando] = useState(true);
  const [detalhe, setDetalhe] = useState(null);
  const [focoMapa, setFocoMapa] = useState(null);

  const carregar = useCallback(async () => {
    setCarregando(true);
    try {
      const params = { ...filtros };
      if (busca.trim()) params.busca = busca.trim();
      const data = await api.demandas.listar(params);
      setDemandas(data);
    } finally {
      setCarregando(false);
    }
  }, [filtros, busca]);

  useEffect(() => {
    const timer = setTimeout(carregar, 300);
    return () => clearTimeout(timer);
  }, [carregar]);

  useEffect(() => {
    Promise.all([api.bairros.listar(), api.assessores.listar()]).then(
      ([b, a]) => { setBairros(b); setAssessores(a); }
    );
  }, []);

  function setFiltro(campo, valor) {
    setFiltros((prev) => ({ ...prev, [campo]: valor || undefined }));
  }

  async function mudarStatus(id, novoStatus) {
    await api.demandas.atualizar(id, { status: novoStatus });
    setDemandas((prev) =>
      prev.map((d) => (d.id === id ? { ...d, status: novoStatus } : d))
    );
  }

  async function selecionarDemanda(d) {
    if (d.latitude && d.longitude) setFocoMapa(d);
    const data = await api.demandas.detalhe(d.id);
    setDetalhe(data);
  }

  return (
    <>
      <ModalDemanda demanda={detalhe} onFechar={() => setDetalhe(null)} />
      <h2 className="page-title">Demandas</h2>
      <p className="page-subtitle">Gerenciamento e acompanhamento de solicitações</p>

      {/* Busca por nome / protocolo */}
      <div style={{ marginBottom: 12 }}>
        <input
          type="text"
          placeholder="Buscar por nome do cidadão ou protocolo..."
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          style={{ width: "100%", padding: "8px 12px", fontSize: 14, border: "1px solid var(--border)", borderRadius: 8, boxSizing: "border-box", background: "var(--surface)", color: "var(--text)" }}
        />
      </div>

      {/* Filtros */}
      <div className="filtros">
        <select onChange={(e) => setFiltro("status", e.target.value)}>
          <option value="">Todos os status</option>
          <option value="aberta">Aberta</option>
          <option value="em_andamento">Em andamento</option>
          <option value="concluida">Concluída</option>
        </select>

        <select onChange={(e) => setFiltro("bairro_id", e.target.value)}>
          <option value="">Todos os bairros</option>
          {bairros.map((b) => (
            <option key={b.id} value={b.id}>{b.nome}</option>
          ))}
        </select>

        <select onChange={(e) => setFiltro("categoria", e.target.value)}>
          <option value="">Todas as categorias</option>
          {CATEGORIAS.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        <select onChange={(e) => setFiltro("assessor_id", e.target.value)}>
          <option value="">Todos os assessores</option>
          {assessores.map((a) => (
            <option key={a.id} value={a.id}>{a.nome}</option>
          ))}
        </select>
      </div>

      {/* Mapa */}
      <Mapa demandas={demandas} foco={focoMapa} />

      {/* Tabela */}
      <div className="tabela-wrap">
        {carregando ? (
          <p style={{ padding: 16, color: "var(--muted)" }}>Carregando...</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Protocolo</th>
                <th>Resumo</th>
                <th>Categoria</th>
                <th>Bairro</th>
                <th>Status</th>
                <th>Data</th>
              </tr>
            </thead>
            <tbody>
              {demandas.length === 0 && (
                <tr><td colSpan={6} className="muted" style={{ padding: 24, textAlign: "center" }}>Nenhuma demanda encontrada.</td></tr>
              )}
              {demandas.map((d) => (
                <tr
                  key={d.id}
                  onClick={() => selecionarDemanda(d)}
                  style={{
                    cursor: "pointer",
                    background: focoMapa?.id === d.id ? "rgba(249,115,22,0.08)" : undefined,
                  }}
                >
                  <td style={{ fontFamily: "monospace", fontSize: 12 }}>
                    #{d.protocolo}
                  </td>
                  <td style={{ maxWidth: 280 }}>
                    <div>{d.resumo || "—"}</div>
                    <div className="muted" style={{ fontSize: 12, marginTop: 2 }}>
                      {d.descricao?.slice(0, 80)}{d.descricao?.length > 80 ? "…" : ""}
                    </div>
                  </td>
                  <td>{d.categoria ?? <span className="muted">—</span>}</td>
                  <td>{bairros.find((b) => b.id === d.bairro_id)?.nome ?? <span className="muted">—</span>}</td>
                  <td onClick={(e) => e.stopPropagation()}>
                    <select
                      className={`status-select ${BADGE[d.status] ?? ""}`}
                      value={d.status}
                      onChange={(e) => mudarStatus(d.id, e.target.value)}
                    >
                      <option value="aberta">aberta</option>
                      <option value="em_andamento">em andamento</option>
                      <option value="concluida">concluída</option>
                    </select>
                  </td>
                  <td className="muted">
                    {new Date(d.data_abertura).toLocaleDateString("pt-BR")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
