import React, { useEffect, useState } from "react";
import { api } from "../api";

const COR_CATEGORIA = {
  infraestrutura: "#3b82f6", saude: "#ef4444", educacao: "#8b5cf6",
  iluminacao: "#f59e0b", seguranca: "#6b7280", transporte: "#06b6d4",
  meio_ambiente: "#10b981", assistencia_social: "#f97316", outro: "#9ca3af",
};

const STATUS_LABEL = {
  aberta:       { label: "Aberta",       bg: "rgba(239,68,68,0.15)",  color: "#f87171"  },
  em_andamento: { label: "Em andamento", bg: "rgba(245,158,11,0.15)", color: "#fbbf24"  },
  concluida:    { label: "Concluída",    bg: "rgba(34,197,94,0.15)",  color: "#4ade80"  },
};

const TIPO_LABEL = {
  nota:              { label: "Nota",               cor: "#6b7280" },
  visita:            { label: "Visita ao local",    cor: "#3b82f6" },
  contato:           { label: "Contato c/ cidadão", cor: "#8b5cf6" },
  encaminhamento:    { label: "Encaminhamento",     cor: "#f59e0b" },
  resolucao_parcial: { label: "Resolução parcial",  cor: "#06b6d4" },
  conclusao:         { label: "Concluído",          cor: "#22c55e" },
};

const iconesTipo = {
  nota: "📝", visita: "🏠", contato: "📞",
  encaminhamento: "📤", resolucao_parcial: "🔧", conclusao: "✅",
};

function formatarWA(wa_id) {
  if (!wa_id) return null;
  const n = wa_id.replace(/\D/g, "");
  if (n.length === 13) return `+${n.slice(0,2)} (${n.slice(2,4)}) ${n.slice(4,9)}-${n.slice(9)}`;
  if (n.length === 12) return `+${n.slice(0,2)} (${n.slice(2,4)}) ${n.slice(4,8)}-${n.slice(8)}`;
  return wa_id;
}

function Campo({ label, valor }) {
  if (valor === null || valor === undefined || valor === "") return null;
  return (
    <div style={{ marginBottom: 10 }}>
      <span style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--muted)", fontWeight: 600 }}>{label}</span>
      <div style={{ marginTop: 2, fontSize: 14, color: "var(--text)" }}>{valor}</div>
    </div>
  );
}

function Secao({ titulo, children }) {
  return (
    <div style={{ marginBottom: 20 }}>
      <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 700, color: "var(--accent)", marginBottom: 10, paddingBottom: 6, borderBottom: "1px solid var(--border)" }}>
        {titulo}
      </div>
      {children}
    </div>
  );
}

function Aba({ label, ativa, onClick, badge }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "9px 16px", border: "none", background: "none", cursor: "pointer",
        fontSize: 13, fontWeight: ativa ? 700 : 400,
        color: ativa ? "var(--accent)" : "var(--muted)",
        borderBottom: ativa ? "2px solid var(--accent)" : "2px solid transparent",
        marginBottom: -1, display: "flex", alignItems: "center", gap: 6,
        transition: "color 0.15s",
      }}
    >
      {label}
      {badge > 0 && (
        <span style={{ background: "var(--accent)", color: "#fff", borderRadius: 99, fontSize: 10, padding: "1px 5px", fontWeight: 700 }}>
          {badge}
        </span>
      )}
    </button>
  );
}

// ── Aba Demanda ───────────────────────────────────────────────────────────────

function TabDemanda({ demanda }) {
  return (
    <>
      <Secao titulo="Descrição">
        <div style={{ background: "var(--surface-2)", borderRadius: 8, padding: "12px 14px", fontSize: 14, lineHeight: 1.6, color: "var(--text)" }}>
          {demanda.descricao}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", marginTop: 12 }}>
          <Campo label="Canal de origem"  valor={demanda.canal_origem} />
          <Campo label="Data de abertura" valor={new Date(demanda.data_abertura).toLocaleString("pt-BR")} />
          {demanda.data_conclusao && <Campo label="Data de conclusão" valor={new Date(demanda.data_conclusao).toLocaleString("pt-BR")} />}
          {demanda.latitude && <Campo label="Coordenadas GPS" valor={`${demanda.latitude.toFixed(5)}, ${demanda.longitude.toFixed(5)}`} />}
        </div>
      </Secao>

      <Secao titulo="Cidadão (quem abriu)">
        {demanda.cidadao ? (
          <>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr" }}>
              <Campo label="Nome"              valor={demanda.cidadao.nome} />
              <Campo label="WhatsApp"          valor={formatarWA(demanda.cidadao.wa_id)} />
              <Campo label="Telefone"          valor={demanda.cidadao.telefone} />
              <Campo label="Total de demandas" valor={demanda.cidadao.total_demandas} />
              <Campo label="Cadastrado em"     valor={new Date(demanda.cidadao.data_cadastro).toLocaleDateString("pt-BR")} />
            </div>
            <Campo label="Endereço" valor={demanda.cidadao.endereco_texto} />
          </>
        ) : (
          <p style={{ margin: 0, fontSize: 13, color: "var(--muted)" }}>Não identificado</p>
        )}
      </Secao>

      {(demanda.bairro || demanda.assessor) && (
        <Secao titulo="Localização e responsável">
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr" }}>
            {demanda.bairro && <>
              <Campo label="Bairro" valor={demanda.bairro.nome} />
              <Campo label="Zona"   valor={demanda.bairro.zona} />
            </>}
            {demanda.assessor && <>
              <Campo label="Assessor responsável" valor={demanda.assessor.nome} />
              <Campo label="Telefone do assessor" valor={demanda.assessor.telefone} />
              <Campo label="E-mail"               valor={demanda.assessor.email} />
            </>}
          </div>
        </Secao>
      )}
    </>
  );
}

// ── Aba Acompanhamento ────────────────────────────────────────────────────────

function TabAcompanhamento({ demandaId, inicial }) {
  const [lista, setLista]     = useState(inicial || []);
  const [enviando, setEnviando] = useState(false);
  const [form, setForm]       = useState({ tipo: "nota", autor: "", descricao: "" });
  const [fotos, setFotos]     = useState([]);
  const [erro, setErro]       = useState("");

  async function submit(e) {
    e.preventDefault();
    if (!form.descricao.trim()) return;
    setEnviando(true);
    setErro("");
    try {
      const fd = new FormData();
      fd.append("tipo", form.tipo);
      fd.append("autor", form.autor || "Assessoria");
      fd.append("descricao", form.descricao);
      fotos.forEach((f) => fd.append("fotos", f));
      const novo = await api.acompanhamento.criar(demandaId, fd);
      setLista((prev) => [...prev, novo]);
      setForm({ tipo: "nota", autor: form.autor, descricao: "" });
      setFotos([]);
    } catch {
      setErro("Erro ao salvar. Tente novamente.");
    } finally {
      setEnviando(false);
    }
  }

  async function deletar(id) {
    if (!confirm("Remover este registro?")) return;
    await api.acompanhamento.deletar(id);
    setLista((prev) => prev.filter((a) => a.id !== id));
  }

  return (
    <div>
      {/* Timeline */}
      {lista.length === 0 ? (
        <p style={{ color: "var(--muted)", fontSize: 13, marginBottom: 20, textAlign: "center", padding: "24px 0" }}>
          Nenhuma ação registrada ainda.
        </p>
      ) : (
        <div style={{ position: "relative", marginBottom: 24 }}>
          <div style={{ position: "absolute", left: 15, top: 0, bottom: 0, width: 2, background: "var(--border)" }} />
          {lista.map((a) => {
            const t = TIPO_LABEL[a.tipo] ?? { label: a.tipo, cor: "#9ca3af" };
            return (
              <div key={a.id} style={{ display: "flex", gap: 14, marginBottom: 20, position: "relative" }}>
                <div style={{ width: 32, height: 32, borderRadius: "50%", background: t.cor, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1 }}>
                  <span style={{ fontSize: 14 }}>{iconesTipo[a.tipo] || "📝"}</span>
                </div>
                <div style={{ flex: 1, background: "var(--surface-2)", borderRadius: 8, padding: "10px 14px", border: "1px solid var(--border)" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4, flexWrap: "wrap" }}>
                    <span style={{ fontSize: 12, fontWeight: 700, color: t.cor }}>{t.label}</span>
                    {a.autor && <span style={{ fontSize: 12, color: "var(--muted)" }}>por {a.autor}</span>}
                    <span style={{ fontSize: 11, color: "var(--muted)", marginLeft: "auto" }}>
                      {new Date(a.data).toLocaleString("pt-BR")}
                    </span>
                    <button onClick={() => deletar(a.id)} title="Remover" style={{ background: "none", border: "none", cursor: "pointer", color: "var(--muted)", fontSize: 16, padding: 0, lineHeight: 1 }}>×</button>
                  </div>
                  <p style={{ margin: 0, fontSize: 14, lineHeight: 1.6, whiteSpace: "pre-wrap", color: "var(--text)" }}>{a.descricao}</p>
                  {a.fotos.length > 0 && (
                    <div style={{ display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap" }}>
                      {a.fotos.map((f) => (
                        <a key={f.id} href={api.acompanhamento.urlFoto(f.id)} target="_blank" rel="noreferrer">
                          <img
                            src={api.acompanhamento.urlFoto(f.id)}
                            alt={f.nome_arquivo}
                            style={{ width: 80, height: 80, objectFit: "cover", borderRadius: 6, border: "1px solid var(--border)", cursor: "pointer" }}
                          />
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Formulário */}
      <form onSubmit={submit} style={{ background: "var(--surface-2)", borderRadius: 10, padding: 16, border: "1px solid var(--border)" }}>
        <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 12, color: "var(--text)" }}>Registrar nova ação</div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 10 }}>
          <div>
            <label style={{ fontSize: 11, color: "var(--muted)", fontWeight: 600, textTransform: "uppercase" }}>Tipo</label>
            <select
              value={form.tipo}
              onChange={(e) => setForm((f) => ({ ...f, tipo: e.target.value }))}
              style={{ display: "block", width: "100%", marginTop: 4, padding: "7px 10px", border: "1px solid var(--border)", borderRadius: 6, fontSize: 13, background: "var(--surface)", color: "var(--text)" }}
            >
              {Object.entries(TIPO_LABEL).map(([k, v]) => (
                <option key={k} value={k}>{v.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label style={{ fontSize: 11, color: "var(--muted)", fontWeight: 600, textTransform: "uppercase" }}>Autor</label>
            <input
              type="text"
              placeholder="Nome do assessor..."
              value={form.autor}
              onChange={(e) => setForm((f) => ({ ...f, autor: e.target.value }))}
              style={{ display: "block", width: "100%", marginTop: 4, padding: "7px 10px", border: "1px solid var(--border)", borderRadius: 6, fontSize: 13, background: "var(--surface)", color: "var(--text)", boxSizing: "border-box" }}
            />
          </div>
        </div>

        <div style={{ marginBottom: 10 }}>
          <label style={{ fontSize: 11, color: "var(--muted)", fontWeight: 600, textTransform: "uppercase" }}>Descrição da ação</label>
          <textarea
            required
            rows={3}
            placeholder="O que foi feito, quem foi contatado, qual encaminhamento..."
            value={form.descricao}
            onChange={(e) => setForm((f) => ({ ...f, descricao: e.target.value }))}
            style={{ display: "block", width: "100%", marginTop: 4, padding: "7px 10px", border: "1px solid var(--border)", borderRadius: 6, fontSize: 13, resize: "vertical", background: "var(--surface)", color: "var(--text)", boxSizing: "border-box" }}
          />
        </div>

        <div style={{ marginBottom: 12 }}>
          <label style={{ fontSize: 11, color: "var(--muted)", fontWeight: 600, textTransform: "uppercase" }}>Fotos (opcional)</label>
          <input
            type="file"
            multiple
            accept="image/*"
            onChange={(e) => setFotos(Array.from(e.target.files))}
            style={{ display: "block", marginTop: 4, fontSize: 13, color: "var(--muted)" }}
          />
          {fotos.length > 0 && (
            <div style={{ display: "flex", gap: 6, marginTop: 8, flexWrap: "wrap" }}>
              {fotos.map((f, i) => (
                <img key={i} src={URL.createObjectURL(f)} alt={f.name} style={{ width: 64, height: 64, objectFit: "cover", borderRadius: 6, border: "1px solid var(--border)" }} />
              ))}
            </div>
          )}
        </div>

        {erro && <p style={{ color: "#ef4444", fontSize: 13, margin: "0 0 8px" }}>{erro}</p>}

        <button
          type="submit"
          disabled={enviando || !form.descricao.trim()}
          style={{ background: "var(--accent)", color: "#fff", border: "none", borderRadius: 6, padding: "8px 18px", fontWeight: 700, fontSize: 13, cursor: "pointer", opacity: enviando ? 0.6 : 1 }}
        >
          {enviando ? "Salvando..." : "Salvar registro"}
        </button>
      </form>
    </div>
  );
}

// ── Aba Conversa ──────────────────────────────────────────────────────────────

function TabConversa({ conversa }) {
  if (!conversa?.length) {
    return <p style={{ color: "var(--muted)", fontSize: 13, textAlign: "center", padding: "32px 0" }}>Sem histórico de conversa.</p>;
  }
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {conversa.map((m, i) => (
        <div key={i} style={{ display: "flex", justifyContent: m.remetente === "cidadao" ? "flex-end" : "flex-start" }}>
          <div style={{
            maxWidth: "78%", padding: "8px 12px", borderRadius: 10, fontSize: 13, lineHeight: 1.5,
            whiteSpace: "pre-wrap", wordBreak: "break-word",
            background: m.remetente === "cidadao" ? "rgba(249,115,22,0.15)" : "var(--surface-2)",
            color: m.remetente === "cidadao" ? "#fdba74" : "var(--text)",
            borderBottomRightRadius: m.remetente === "cidadao" ? 2 : 10,
            borderBottomLeftRadius:  m.remetente === "bot"     ? 2 : 10,
          }}>
            {m.mensagem}
          </div>
        </div>
      ))}
    </div>
  );
}

// ── Modal principal ───────────────────────────────────────────────────────────

export default function ModalDemanda({ demanda, onFechar }) {
  const [aba, setAba] = useState("demanda");

  useEffect(() => {
    if (demanda) setAba("demanda");
  }, [demanda?.id]);

  useEffect(() => {
    function onKey(e) { if (e.key === "Escape") onFechar(); }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onFechar]);

  if (!demanda) return null;

  const st     = STATUS_LABEL[demanda.status] ?? { label: demanda.status, bg: "var(--surface-2)", color: "var(--muted)" };
  const corCat = COR_CATEGORIA[demanda.categoria] ?? "#9ca3af";

  return (
    <div
      onClick={onFechar}
      style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.65)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000, padding: 16 }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{ background: "var(--surface)", borderRadius: 14, width: "100%", maxWidth: 660, maxHeight: "90vh", display: "flex", flexDirection: "column", boxShadow: "0 24px 80px rgba(0,0,0,0.7)", border: "1px solid var(--border)" }}
      >
        {/* Header */}
        <div style={{ padding: "14px 20px", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", flexShrink: 0 }}>
          <span style={{ fontFamily: "monospace", fontWeight: 700, fontSize: 14, color: "var(--muted)" }}>#{demanda.protocolo}</span>
          {demanda.categoria && (
            <span style={{ background: corCat + "22", color: corCat, fontSize: 12, padding: "2px 9px", borderRadius: 99, fontWeight: 600 }}>{demanda.categoria}</span>
          )}
          <span style={{ background: st.bg, color: st.color, fontSize: 12, padding: "2px 9px", borderRadius: 99, fontWeight: 600 }}>{st.label}</span>
          <button onClick={onFechar} style={{ marginLeft: "auto", background: "none", border: "none", fontSize: 20, cursor: "pointer", color: "var(--muted)", lineHeight: 1, padding: "0 4px" }}>×</button>
        </div>

        {/* Abas */}
        <div style={{ display: "flex", borderBottom: "1px solid var(--border)", paddingLeft: 10, flexShrink: 0 }}>
          <Aba label="Demanda"        ativa={aba === "demanda"}  onClick={() => setAba("demanda")}  />
          <Aba label="Acompanhamento" ativa={aba === "acomp"}    onClick={() => setAba("acomp")}   badge={demanda.acompanhamentos?.length} />
          <Aba label="Conversa"       ativa={aba === "conversa"} onClick={() => setAba("conversa")} badge={demanda.conversa?.length} />
        </div>

        {/* Conteúdo */}
        <div style={{ overflowY: "auto", padding: "20px 24px", flex: 1 }}>
          {aba === "demanda"  && <TabDemanda demanda={demanda} />}
          {aba === "acomp"   && <TabAcompanhamento demandaId={demanda.id} inicial={demanda.acompanhamentos} />}
          {aba === "conversa" && <TabConversa conversa={demanda.conversa} />}
        </div>
      </div>
    </div>
  );
}
