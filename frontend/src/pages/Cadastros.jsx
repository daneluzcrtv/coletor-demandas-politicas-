import React, { useEffect, useState } from "react";
import { api } from "../api";

// ── Shared components ─────────────────────────────────────────────────────────

function TabBtn({ label, ativa, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "9px 18px", border: "none", background: "none", cursor: "pointer",
        fontSize: 13, fontWeight: ativa ? 700 : 400,
        color: ativa ? "var(--accent)" : "var(--muted)",
        borderBottom: ativa ? "2px solid var(--accent)" : "2px solid transparent",
        marginBottom: -1,
      }}
    >
      {label}
    </button>
  );
}

function Modal({ titulo, onFechar, children }) {
  useEffect(() => {
    const onKey = (e) => { if (e.key === "Escape") onFechar(); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onFechar]);

  return (
    <div
      onClick={onFechar}
      style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.65)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000, padding: 16 }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14, width: "100%", maxWidth: 500, boxShadow: "0 24px 80px rgba(0,0,0,0.6)" }}
      >
        <div style={{ padding: "16px 22px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontWeight: 700, fontSize: 15, color: "var(--text)" }}>{titulo}</span>
          <button onClick={onFechar} style={{ background: "none", border: "none", fontSize: 20, cursor: "pointer", color: "var(--muted)", lineHeight: 1, padding: "0 4px" }}>×</button>
        </div>
        <div style={{ padding: "20px 22px" }}>{children}</div>
      </div>
    </div>
  );
}

function Campo({ label, required, children }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <label style={{ display: "block", fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--muted)", marginBottom: 5 }}>
        {label}{required && <span style={{ color: "var(--accent)" }}> *</span>}
      </label>
      {children}
    </div>
  );
}

const inputStyle = {
  width: "100%", padding: "8px 11px", border: "1px solid var(--border)", borderRadius: 8,
  background: "var(--surface-2)", color: "var(--text)", fontSize: 13, boxSizing: "border-box",
};

function BotaoSalvar({ enviando, disabled }) {
  return (
    <button
      type="submit"
      disabled={enviando || disabled}
      style={{ padding: "9px 22px", background: "var(--accent)", color: "#fff", border: "none", borderRadius: 8, fontWeight: 700, fontSize: 13, cursor: "pointer", opacity: enviando ? 0.6 : 1 }}
    >
      {enviando ? "Salvando..." : "Salvar"}
    </button>
  );
}

function BotaoCancelar({ onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={{ padding: "9px 16px", background: "none", color: "var(--muted)", border: "1px solid var(--border)", borderRadius: 8, fontWeight: 500, fontSize: 13, cursor: "pointer" }}
    >
      Cancelar
    </button>
  );
}

// ── Assessores ────────────────────────────────────────────────────────────────

const FORM_ASSESSOR_VAZIO = { nome: "", telefone: "", email: "", areas_tematicas: "", ativo: true };

function ModalSenha({ assessor, onFechar }) {
  const [senha, setSenha]         = useState("");
  const [confirma, setConfirma]   = useState("");
  const [enviando, setEnviando]   = useState(false);
  const [erro, setErro]           = useState("");
  const [ok, setOk]               = useState(false);

  async function submit(e) {
    e.preventDefault();
    if (senha.length < 6) { setErro("Mínimo de 6 caracteres."); return; }
    if (senha !== confirma) { setErro("As senhas não coincidem."); return; }
    setEnviando(true);
    setErro("");
    try {
      await api.assessores.definirSenha(assessor.id, senha);
      setOk(true);
      setTimeout(onFechar, 1200);
    } catch {
      setErro("Erro ao definir senha.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Modal titulo={`Definir senha — ${assessor.nome}`} onFechar={onFechar}>
      {ok ? (
        <p style={{ textAlign: "center", color: "#4ade80", fontWeight: 600, padding: "12px 0" }}>✓ Senha definida com sucesso!</p>
      ) : (
        <form onSubmit={submit}>
          <Campo label="Nova senha" required>
            <input type="password" style={inputStyle} value={senha} onChange={e => setSenha(e.target.value)} placeholder="mínimo 6 caracteres" required />
          </Campo>
          <Campo label="Confirmar senha" required>
            <input type="password" style={inputStyle} value={confirma} onChange={e => setConfirma(e.target.value)} placeholder="repita a senha" required />
          </Campo>
          {erro && <p style={{ color: "#f87171", fontSize: 13, marginBottom: 12 }}>{erro}</p>}
          <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
            <BotaoCancelar onClick={onFechar} />
            <BotaoSalvar enviando={enviando} />
          </div>
        </form>
      )}
    </Modal>
  );
}

function formParaPayload(f) {
  return {
    nome:             f.nome.trim(),
    telefone:         f.telefone.trim() || null,
    email:            f.email.trim() || null,
    areas_tematicas:  f.areas_tematicas
      ? f.areas_tematicas.split(",").map(s => s.trim()).filter(Boolean)
      : [],
    ativo:            f.ativo,
  };
}

function payloadParaForm(a) {
  return {
    nome:            a.nome,
    telefone:        a.telefone ?? "",
    email:           a.email ?? "",
    areas_tematicas: (a.areas_tematicas ?? []).join(", "),
    ativo:           a.ativo ?? true,
  };
}

function FormAssessor({ inicial, onSalvar, onCancelar }) {
  const [form, setForm] = useState(inicial ?? FORM_ASSESSOR_VAZIO);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");

  function set(campo, valor) { setForm(f => ({ ...f, [campo]: valor })); }

  async function submit(e) {
    e.preventDefault();
    if (!form.nome.trim()) return;
    setEnviando(true);
    setErro("");
    try {
      await onSalvar(formParaPayload(form));
    } catch (err) {
      setErro(err.message || "Erro ao salvar.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={submit}>
      <Campo label="Nome" required>
        <input style={inputStyle} value={form.nome} onChange={e => set("nome", e.target.value)} placeholder="Nome completo do assessor" required />
      </Campo>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <Campo label="Telefone">
          <input style={inputStyle} value={form.telefone} onChange={e => set("telefone", e.target.value)} placeholder="(11) 99999-9999" />
        </Campo>
        <Campo label="E-mail">
          <input style={inputStyle} type="email" value={form.email} onChange={e => set("email", e.target.value)} placeholder="email@exemplo.com" />
        </Campo>
      </div>

      <Campo label="Áreas Temáticas">
        <input
          style={inputStyle}
          value={form.areas_tematicas}
          onChange={e => set("areas_tematicas", e.target.value)}
          placeholder="infraestrutura, saúde, educação  (separar por vírgula)"
        />
      </Campo>

      <Campo label="Status">
        <label style={{ display: "flex", alignItems: "center", gap: 10, cursor: "pointer", userSelect: "none" }}>
          <div
            onClick={() => set("ativo", !form.ativo)}
            style={{
              width: 40, height: 22, borderRadius: 11, cursor: "pointer",
              background: form.ativo ? "var(--accent)" : "var(--border)",
              position: "relative", transition: "background 0.2s", flexShrink: 0,
            }}
          >
            <div style={{
              position: "absolute", top: 3, left: form.ativo ? 21 : 3,
              width: 16, height: 16, borderRadius: "50%", background: "#fff",
              transition: "left 0.2s",
            }} />
          </div>
          <span style={{ fontSize: 13, color: form.ativo ? "var(--accent)" : "var(--muted)" }}>
            {form.ativo ? "Ativo" : "Inativo"}
          </span>
        </label>
      </Campo>

      {erro && <p style={{ color: "#ef4444", fontSize: 13, marginBottom: 12 }}>{erro}</p>}

      <div style={{ display: "flex", gap: 10, justifyContent: "flex-end", marginTop: 4 }}>
        <BotaoCancelar onClick={onCancelar} />
        <BotaoSalvar enviando={enviando} disabled={!form.nome.trim()} />
      </div>
    </form>
  );
}

function TabelaAssessores() {
  const [lista, setLista]   = useState([]);
  const [modal, setModal]   = useState(null); // null | "novo" | assessor-obj
  const [modalSenha, setModalSenha] = useState(null);
  const [erro, setErro]     = useState("");
  const [carregando, setCarregando] = useState(true);

  async function carregar() {
    setCarregando(true);
    try { setLista(await api.assessores.listar()); }
    finally { setCarregando(false); }
  }

  useEffect(() => { carregar(); }, []);

  async function salvar(dados) {
    if (modal === "novo") {
      const novo = await api.assessores.criar(dados);
      setLista(prev => [...prev, novo].sort((a, b) => a.nome.localeCompare(b.nome)));
    } else {
      const att = await api.assessores.atualizar(modal.id, dados);
      setLista(prev => prev.map(a => a.id === att.id ? att : a));
    }
    setModal(null);
  }

  async function deletar(a) {
    if (!confirm(`Remover o assessor "${a.nome}"? Esta ação não pode ser desfeita.`)) return;
    setErro("");
    try {
      await api.assessores.deletar(a.id);
      setLista(prev => prev.filter(x => x.id !== a.id));
    } catch {
      setErro(`Não foi possível remover "${a.nome}". Pode haver demandas ou bairros associados.`);
    }
  }

  return (
    <>
      {modal && (
        <Modal
          titulo={modal === "novo" ? "Novo Assessor" : `Editar — ${modal.nome}`}
          onFechar={() => setModal(null)}
        >
          <FormAssessor
            inicial={modal !== "novo" ? payloadParaForm(modal) : undefined}
            onSalvar={salvar}
            onCancelar={() => setModal(null)}
          />
        </Modal>
      )}
      {modalSenha && <ModalSenha assessor={modalSenha} onFechar={() => setModalSenha(null)} />}

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <span style={{ fontSize: 13, color: "var(--muted)" }}>{lista.length} assessor{lista.length !== 1 ? "es" : ""} cadastrado{lista.length !== 1 ? "s" : ""}</span>
        <button
          onClick={() => setModal("novo")}
          style={{ padding: "8px 18px", background: "var(--accent)", color: "#fff", border: "none", borderRadius: 8, fontWeight: 700, fontSize: 13, cursor: "pointer" }}
        >
          + Novo assessor
        </button>
      </div>

      {erro && (
        <div style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: 8, padding: "10px 14px", marginBottom: 14, fontSize: 13, color: "#f87171" }}>
          {erro}
          <button onClick={() => setErro("")} style={{ marginLeft: 12, background: "none", border: "none", color: "#f87171", cursor: "pointer", fontSize: 14, lineHeight: 1 }}>×</button>
        </div>
      )}

      <div className="tabela-wrap">
        {carregando ? (
          <p style={{ padding: 20, color: "var(--muted)" }}>Carregando...</p>
        ) : lista.length === 0 ? (
          <p style={{ padding: 32, textAlign: "center", color: "var(--muted)", fontSize: 13 }}>Nenhum assessor cadastrado ainda.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>Telefone</th>
                <th>E-mail</th>
                <th>Áreas Temáticas</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {lista.map(a => (
                <tr key={a.id}>
                  <td style={{ fontWeight: 600 }}>{a.nome}</td>
                  <td style={{ color: "var(--muted)" }}>{a.telefone || "—"}</td>
                  <td style={{ color: "var(--muted)" }}>{a.email || "—"}</td>
                  <td>
                    {a.areas_tematicas?.length > 0 ? (
                      <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                        {a.areas_tematicas.map((area, i) => (
                          <span key={i} style={{ background: "var(--accent-dim)", color: "var(--accent)", borderRadius: 99, fontSize: 11, padding: "2px 8px", fontWeight: 600 }}>
                            {area}
                          </span>
                        ))}
                      </div>
                    ) : <span style={{ color: "var(--muted)" }}>—</span>}
                  </td>
                  <td>
                    <span style={{ fontSize: 12, fontWeight: 600, color: a.ativo ? "#4ade80" : "var(--muted)" }}>
                      {a.ativo ? "● Ativo" : "○ Inativo"}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: "flex", gap: 6, justifyContent: "flex-end" }}>
                      <button onClick={() => setModalSenha(a)} style={{ ...btnStyle, color: "var(--accent)", borderColor: "rgba(249,115,22,0.3)" }}>
                        Def. senha
                      </button>
                      <button onClick={() => setModal(a)} style={btnStyle}>Editar</button>
                      <button onClick={() => deletar(a)} style={{ ...btnStyle, color: "#f87171", borderColor: "rgba(239,68,68,0.3)" }}>Remover</button>
                    </div>
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

// ── Bairros ───────────────────────────────────────────────────────────────────

const ZONAS = ["Centro", "Norte", "Sul", "Leste", "Oeste", "Rural"];
const FORM_BAIRRO_VAZIO = { nome: "", zona: "", assessor_responsavel_id: "" };

function FormBairro({ inicial, assessores, onSalvar, onCancelar }) {
  const [form, setForm] = useState(inicial ?? FORM_BAIRRO_VAZIO);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");

  function set(campo, valor) { setForm(f => ({ ...f, [campo]: valor })); }

  async function submit(e) {
    e.preventDefault();
    if (!form.nome.trim()) return;
    setEnviando(true);
    setErro("");
    try {
      await onSalvar({
        nome:                    form.nome.trim(),
        zona:                    form.zona || null,
        assessor_responsavel_id: form.assessor_responsavel_id ? parseInt(form.assessor_responsavel_id) : null,
      });
    } catch (err) {
      setErro(err.message || "Erro ao salvar.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={submit}>
      <Campo label="Nome do Bairro" required>
        <input style={inputStyle} value={form.nome} onChange={e => set("nome", e.target.value)} placeholder="Ex: Centro, Jardim das Flores..." required />
      </Campo>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <Campo label="Zona">
          <select style={inputStyle} value={form.zona} onChange={e => set("zona", e.target.value)}>
            <option value="">Não definido</option>
            {ZONAS.map(z => <option key={z} value={z}>{z}</option>)}
          </select>
        </Campo>

        <Campo label="Assessor Responsável">
          <select style={inputStyle} value={form.assessor_responsavel_id} onChange={e => set("assessor_responsavel_id", e.target.value)}>
            <option value="">Nenhum</option>
            {assessores.filter(a => a.ativo).map(a => (
              <option key={a.id} value={a.id}>{a.nome}</option>
            ))}
          </select>
        </Campo>
      </div>

      {erro && <p style={{ color: "#ef4444", fontSize: 13, marginBottom: 12 }}>{erro}</p>}

      <div style={{ display: "flex", gap: 10, justifyContent: "flex-end", marginTop: 4 }}>
        <BotaoCancelar onClick={onCancelar} />
        <BotaoSalvar enviando={enviando} disabled={!form.nome.trim()} />
      </div>
    </form>
  );
}

function bairroParaForm(b) {
  return {
    nome:                    b.nome,
    zona:                    b.zona ?? "",
    assessor_responsavel_id: b.assessor_responsavel_id ?? "",
  };
}

function TabelaBairros() {
  const [lista, setLista]       = useState([]);
  const [assessores, setAssessores] = useState([]);
  const [modal, setModal]       = useState(null);
  const [erro, setErro]         = useState("");
  const [carregando, setCarregando] = useState(true);

  async function carregar() {
    setCarregando(true);
    try {
      const [b, a] = await Promise.all([api.bairros.listar(), api.assessores.listar()]);
      setLista(b);
      setAssessores(a);
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => { carregar(); }, []);

  async function salvar(dados) {
    if (modal === "novo") {
      const novo = await api.bairros.criar(dados);
      setLista(prev => [...prev, novo].sort((a, b) => a.nome.localeCompare(b.nome)));
    } else {
      const att = await api.bairros.atualizar(modal.id, dados);
      setLista(prev => prev.map(b => b.id === att.id ? att : b));
    }
    setModal(null);
  }

  async function deletar(b) {
    if (!confirm(`Remover o bairro "${b.nome}"? Esta ação não pode ser desfeita.`)) return;
    setErro("");
    try {
      await api.bairros.deletar(b.id);
      setLista(prev => prev.filter(x => x.id !== b.id));
    } catch {
      setErro(`Não foi possível remover "${b.nome}". Pode haver demandas associadas a este bairro.`);
    }
  }

  function nomeAssessor(id) {
    return assessores.find(a => a.id === id)?.nome ?? "—";
  }

  return (
    <>
      {modal && (
        <Modal
          titulo={modal === "novo" ? "Novo Bairro" : `Editar — ${modal.nome}`}
          onFechar={() => setModal(null)}
        >
          <FormBairro
            inicial={modal !== "novo" ? bairroParaForm(modal) : undefined}
            assessores={assessores}
            onSalvar={salvar}
            onCancelar={() => setModal(null)}
          />
        </Modal>
      )}

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <span style={{ fontSize: 13, color: "var(--muted)" }}>{lista.length} bairro{lista.length !== 1 ? "s" : ""} cadastrado{lista.length !== 1 ? "s" : ""}</span>
        <button
          onClick={() => setModal("novo")}
          style={{ padding: "8px 18px", background: "var(--accent)", color: "#fff", border: "none", borderRadius: 8, fontWeight: 700, fontSize: 13, cursor: "pointer" }}
        >
          + Novo bairro
        </button>
      </div>

      {erro && (
        <div style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: 8, padding: "10px 14px", marginBottom: 14, fontSize: 13, color: "#f87171" }}>
          {erro}
          <button onClick={() => setErro("")} style={{ marginLeft: 12, background: "none", border: "none", color: "#f87171", cursor: "pointer", fontSize: 14, lineHeight: 1 }}>×</button>
        </div>
      )}

      <div className="tabela-wrap">
        {carregando ? (
          <p style={{ padding: 20, color: "var(--muted)" }}>Carregando...</p>
        ) : lista.length === 0 ? (
          <p style={{ padding: 32, textAlign: "center", color: "var(--muted)", fontSize: 13 }}>Nenhum bairro cadastrado ainda.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>Zona</th>
                <th>Assessor Responsável</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {lista.map(b => (
                <tr key={b.id}>
                  <td style={{ fontWeight: 600 }}>{b.nome}</td>
                  <td>
                    {b.zona
                      ? <span style={{ background: "var(--surface-2)", color: "var(--muted)", borderRadius: 6, fontSize: 12, padding: "2px 8px" }}>{b.zona}</span>
                      : <span style={{ color: "var(--muted)" }}>—</span>}
                  </td>
                  <td style={{ color: b.assessor_responsavel_id ? "var(--text)" : "var(--muted)" }}>
                    {b.assessor_responsavel_id ? nomeAssessor(b.assessor_responsavel_id) : "—"}
                  </td>
                  <td>
                    <div style={{ display: "flex", gap: 6, justifyContent: "flex-end" }}>
                      <button onClick={() => setModal(b)} style={btnStyle}>Editar</button>
                      <button onClick={() => deletar(b)} style={{ ...btnStyle, color: "#f87171", borderColor: "rgba(239,68,68,0.3)" }}>Remover</button>
                    </div>
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

// ── Shared style ──────────────────────────────────────────────────────────────

const btnStyle = {
  padding: "5px 12px", background: "none", border: "1px solid var(--border)",
  borderRadius: 6, cursor: "pointer", fontSize: 12, color: "var(--muted)",
};

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Cadastros() {
  const [aba, setAba] = useState("assessores");

  return (
    <>
      <h2 className="page-title">Cadastros</h2>
      <p className="page-subtitle">Gerenciamento de assessores e bairros</p>

      <div style={{ display: "flex", borderBottom: "1px solid var(--border)", marginBottom: 24 }}>
        <TabBtn label="Assessores" ativa={aba === "assessores"} onClick={() => setAba("assessores")} />
        <TabBtn label="Bairros"    ativa={aba === "bairros"}    onClick={() => setAba("bairros")}    />
      </div>

      {aba === "assessores" && <TabelaAssessores />}
      {aba === "bairros"    && <TabelaBairros />}
    </>
  );
}
