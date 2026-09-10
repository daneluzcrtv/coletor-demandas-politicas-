import React, { useState } from "react";
import { api } from "../api";

const CONTAS_DEMO = [
  { label: "Deputado",  email: "deputado@gabinete.com",  senha: "demo123", cor: "#f97316" },
  { label: "Assessor",  email: "assessor@gabinete.com",  senha: "demo123", cor: "#8b5cf6" },
];

export default function Login({ onLogin }) {
  const [email, setEmail]     = useState("");
  const [senha, setSenha]     = useState("");
  const [erro, setErro]       = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setErro("");
    setLoading(true);
    try {
      const data = await api.auth.login(email, senha);
      localStorage.setItem("token", data.access_token);
      onLogin({ nome: data.nome, id: data.assessor_id, cargo: data.cargo });
    } catch {
      setErro("E-mail ou senha incorretos.");
    } finally {
      setLoading(false);
    }
  }

  function preencherConta(conta) {
    setEmail(conta.email);
    setSenha(conta.senha);
    setErro("");
  }

  return (
    <div style={{
      minHeight: "100vh", background: "var(--bg)",
      display: "flex", alignItems: "center", justifyContent: "center",
      padding: 24,
    }}>
      <div style={{ width: "100%", maxWidth: 400 }}>

        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
            <div style={{ width: 10, height: 10, borderRadius: "50%", background: "var(--accent)", boxShadow: "0 0 10px var(--accent-glow)" }} />
            <span style={{ fontSize: 22, fontWeight: 800, color: "var(--text)", letterSpacing: "-0.5px" }}>Gabinete</span>
          </div>
          <p style={{ fontSize: 13, color: "var(--muted)" }}>Itapecerica da Serra</p>
        </div>

        {/* Card de login */}
        <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14, padding: "28px 28px 24px" }}>
          <h2 style={{ fontSize: 17, fontWeight: 700, color: "var(--text)", marginBottom: 4 }}>Entrar na plataforma</h2>
          <p style={{ fontSize: 13, color: "var(--muted)", marginBottom: 22 }}>Use o e-mail e senha do seu acesso.</p>

          <form onSubmit={submit}>
            <div style={{ marginBottom: 14 }}>
              <label style={labelStyle}>E-mail</label>
              <input
                type="email"
                required
                autoFocus
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="seu@email.com"
                style={inputStyle}
              />
            </div>

            <div style={{ marginBottom: 20 }}>
              <label style={labelStyle}>Senha</label>
              <input
                type="password"
                required
                value={senha}
                onChange={e => setSenha(e.target.value)}
                placeholder="••••••••"
                style={inputStyle}
              />
            </div>

            {erro && (
              <div style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.25)", borderRadius: 8, padding: "9px 12px", marginBottom: 16, fontSize: 13, color: "#f87171" }}>
                {erro}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              style={{ width: "100%", padding: "11px", background: "var(--accent)", color: "#fff", border: "none", borderRadius: 8, fontWeight: 700, fontSize: 14, cursor: "pointer", opacity: loading ? 0.7 : 1 }}
            >
              {loading ? "Entrando..." : "Entrar"}
            </button>
          </form>
        </div>

        {/* Contas de teste */}
        <div style={{ marginTop: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
            <div style={{ flex: 1, height: 1, background: "var(--border)" }} />
            <span style={{ fontSize: 11, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.06em", whiteSpace: "nowrap" }}>
              Contas de demonstração
            </span>
            <div style={{ flex: 1, height: 1, background: "var(--border)" }} />
          </div>

          <div style={{ display: "flex", gap: 10 }}>
            {CONTAS_DEMO.map(conta => (
              <button
                key={conta.email}
                onClick={() => preencherConta(conta)}
                style={{
                  flex: 1, padding: "12px 16px",
                  background: "var(--surface)", border: `1px solid var(--border)`,
                  borderRadius: 10, cursor: "pointer", textAlign: "left",
                  transition: "border-color 0.15s",
                }}
                onMouseEnter={e => e.currentTarget.style.borderColor = conta.cor}
                onMouseLeave={e => e.currentTarget.style.borderColor = "var(--border)"}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                  <div style={{ width: 28, height: 28, borderRadius: "50%", background: conta.cor + "22", border: `1px solid ${conta.cor}44`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, fontWeight: 800, color: conta.cor }}>
                    {conta.label[0]}
                  </div>
                  <span style={{ fontSize: 13, fontWeight: 700, color: "var(--text)" }}>{conta.label}</span>
                </div>
                <div style={{ fontSize: 11, color: "var(--muted)", fontFamily: "monospace" }}>{conta.email}</div>
                <div style={{ fontSize: 11, color: "var(--muted)", fontFamily: "monospace" }}>senha: {conta.senha}</div>
              </button>
            ))}
          </div>

          <p style={{ textAlign: "center", marginTop: 12, fontSize: 11, color: "var(--muted)" }}>
            Clique em uma conta para preencher automaticamente
          </p>
        </div>

      </div>
    </div>
  );
}

const labelStyle = {
  display: "block", fontSize: 11, fontWeight: 600,
  textTransform: "uppercase", letterSpacing: "0.05em",
  color: "var(--muted)", marginBottom: 5,
};

const inputStyle = {
  width: "100%", padding: "10px 12px",
  border: "1px solid var(--border)", borderRadius: 8,
  background: "var(--surface-2)", color: "var(--text)",
  fontSize: 14, boxSizing: "border-box",
};
