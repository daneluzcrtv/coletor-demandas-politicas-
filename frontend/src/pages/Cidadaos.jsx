import React, { useEffect, useState } from "react";
import { api } from "../api";

function formatarTelefone(wa_id) {
  if (!wa_id) return "—";
  const n = wa_id.replace(/\D/g, "");
  if (n.length === 13) return `+${n.slice(0, 2)} (${n.slice(2, 4)}) ${n.slice(4, 9)}-${n.slice(9)}`;
  return `+${n}`;
}

function formatarData(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("pt-BR");
}

export default function Cidadaos() {
  const [cidadaos, setCidadaos] = useState([]);
  const [busca, setBusca] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.cidadaos.listar().then(setCidadaos).finally(() => setLoading(false));
  }, []);

  const filtrados = cidadaos.filter(c =>
    c.nome?.toLowerCase().includes(busca.toLowerCase()) ||
    c.wa_id?.includes(busca) ||
    c.endereco_texto?.toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
        <h2 className="page-title" style={{ margin: 0 }}>Cidadãos</h2>
        <span style={{ fontSize: 13, color: "var(--muted)" }}>{cidadaos.length} cadastrados</span>
      </div>

      <input
        value={busca}
        onChange={e => setBusca(e.target.value)}
        placeholder="Buscar por nome, WhatsApp ou endereço..."
        style={{ width: "100%", padding: "8px 12px", border: "1px solid var(--border)", borderRadius: 6, fontSize: 13, marginBottom: 16, background: "var(--surface)", color: "var(--text)", boxSizing: "border-box" }}
      />

      {loading ? (
        <p className="muted" style={{ textAlign: "center", marginTop: 60 }}>Carregando...</p>
      ) : filtrados.length === 0 ? (
        <p className="muted" style={{ textAlign: "center", marginTop: 60 }}>Nenhum cidadão encontrado.</p>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)", color: "var(--muted)", textAlign: "left" }}>
                <th style={{ padding: "8px 12px", fontWeight: 600 }}>Nome</th>
                <th style={{ padding: "8px 12px", fontWeight: 600 }}>WhatsApp</th>
                <th style={{ padding: "8px 12px", fontWeight: 600 }}>Endereço</th>
                <th style={{ padding: "8px 12px", fontWeight: 600 }}>Demandas</th>
                <th style={{ padding: "8px 12px", fontWeight: 600 }}>Cadastro</th>
              </tr>
            </thead>
            <tbody>
              {filtrados.map(c => (
                <tr key={c.id} style={{ borderBottom: "1px solid var(--border)" }}>
                  <td style={{ padding: "10px 12px", color: "var(--text)", fontWeight: 500 }}>{c.nome}</td>
                  <td style={{ padding: "10px 12px", color: "var(--muted)" }}>{formatarTelefone(c.wa_id)}</td>
                  <td style={{ padding: "10px 12px", color: "var(--muted)", maxWidth: 260, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{c.endereco_texto || "—"}</td>
                  <td style={{ padding: "10px 12px", color: "var(--accent)", fontWeight: 600, textAlign: "center" }}>{c.total_demandas}</td>
                  <td style={{ padding: "10px 12px", color: "var(--muted)" }}>{formatarData(c.data_cadastro)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
