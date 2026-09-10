import React, { useEffect, useState } from "react";
import ListaDemandas from "./pages/ListaDemandas";
import Historico from "./pages/Historico";
import Relatorio from "./pages/Relatorio";
import Simulador from "./pages/Simulador";
import MapaEleitoral from "./pages/MapaEleitoral";
import AnaliseEleitoral from "./pages/AnaliseEleitoral";
import Cadastros from "./pages/Cadastros";
import Cidadaos from "./pages/Cidadaos";
import Login from "./pages/Login";

const PAGINAS = [
  { id: "demandas",  label: "Demandas",          Icon: IconDemandas  },
  { id: "mapa",      label: "Mapa Eleitoral",     Icon: IconMapa      },
  { id: "analise",   label: "Análise Eleitoral",  Icon: IconAnalise   },
  { id: "relatorio", label: "Relatório Mensal",   Icon: IconRelatorio },
  { id: "historico", label: "Histórico",          Icon: IconHistorico },
  { id: "cidadaos",  label: "Cidadãos",            Icon: IconCidadaosPage },
  { id: "simulador", label: "Simulador do Bot",   Icon: IconSimulador },
  { id: "cadastros", label: "Cadastros",          Icon: IconCadastros },
];

export default function App() {
  const [pagina, setPagina] = useState("demandas");
  const [tema, setTema] = useState(() => localStorage.getItem("tema") || "dark");
  const [usuario, setUsuario] = useState(() => {
    const token = localStorage.getItem("token");
    const nome  = localStorage.getItem("usuario_nome");
    const cargo = localStorage.getItem("usuario_cargo") || "assessor";
    return token && nome ? { nome, cargo } : null;
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", tema);
    localStorage.setItem("tema", tema);
  }, [tema]);

  function alternarTema() {
    setTema(t => t === "dark" ? "light" : "dark");
  }

  function onLogin(user) {
    localStorage.setItem("usuario_nome", user.nome);
    localStorage.setItem("usuario_cargo", user.cargo || "assessor");
    setUsuario(user);
  }

  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("usuario_nome");
    localStorage.removeItem("usuario_cargo");
    setUsuario(null);
  }

  if (!usuario) return <Login onLogin={onLogin} />;

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="sidebar-logo-title">
            <span className="sidebar-accent-dot" />
            Gabinete
          </div>
          <div className="sidebar-logo-sub">Itapecerica da Serra</div>
        </div>

        <nav className="sidebar-nav">
          {PAGINAS.filter(p => {
            const soDeputado = ["cadastros", "analise", "relatorio"];
            return !soDeputado.includes(p.id) || usuario.cargo === "deputado";
          }).map(({ id, label, Icon }) => (
            <button
              key={id}
              className={`nav-link ${pagina === id ? "active" : ""}`}
              onClick={() => setPagina(id)}
            >
              <Icon size={15} />
              {label}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
            <div style={{ width: 26, height: 26, borderRadius: "50%", background: "var(--accent-dim)", border: "1px solid var(--accent)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700, color: "var(--accent)", flexShrink: 0 }}>
              {usuario.nome?.[0]?.toUpperCase()}
            </div>
            <span style={{ fontSize: 12, color: "var(--text)", fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              {usuario.nome}
            </span>
          </div>
          <button className="theme-toggle" onClick={alternarTema}>
            {tema === "dark" ? <IconSun size={13} /> : <IconMoon size={13} />}
            {tema === "dark" ? "Tema claro" : "Tema escuro"}
          </button>
          <button
            onClick={logout}
            style={{ background: "none", border: "none", cursor: "pointer", fontSize: 12, color: "var(--muted)", textAlign: "left", padding: 0, display: "flex", alignItems: "center", gap: 6 }}
          >
            <IconLogout size={13} /> Sair
          </button>
        </div>
      </aside>

      <main className="main">
        {pagina === "demandas"  && <ListaDemandas />}
        {pagina === "historico" && <Historico />}
        {pagina === "mapa"      && <MapaEleitoral />}
        {pagina === "analise"   && usuario.cargo === "deputado" && <AnaliseEleitoral />}
        {pagina === "relatorio" && usuario.cargo === "deputado" && <Relatorio />}
        {pagina === "cidadaos"  && <Cidadaos />}
        {pagina === "simulador" && <Simulador />}
        {pagina === "cadastros" && usuario.cargo === "deputado" && <Cadastros />}
      </main>
    </div>
  );
}

// ── Inline SVG icons ──────────────────────────────────────────────────────────
function IconDemandas({ size = 16 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
      <polyline points="14,2 14,8 20,8"/>
      <line x1="16" y1="13" x2="8" y2="13"/>
      <line x1="16" y1="17" x2="8" y2="17"/>
      <line x1="10" y1="9" x2="8" y2="9"/>
    </svg>
  );
}

function IconMapa({ size = 16 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="1,6 1,22 8,18 16,22 23,18 23,2 16,6 8,2 1,6"/>
      <line x1="8" y1="2" x2="8" y2="18"/>
      <line x1="16" y1="6" x2="16" y2="22"/>
    </svg>
  );
}

function IconAnalise({ size = 16 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="20" x2="18" y2="10"/>
      <line x1="12" y1="20" x2="12" y2="4"/>
      <line x1="6" y1="20" x2="6" y2="14"/>
      <polyline points="20,10 18,8 16,10"/>
    </svg>
  );
}

function IconRelatorio({ size = 16 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
      <polyline points="13,2 13,9 20,9"/>
      <line x1="8" y1="13" x2="16" y2="13"/>
      <line x1="8" y1="17" x2="14" y2="17"/>
    </svg>
  );
}

function IconHistorico({ size = 16 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <polyline points="12,6 12,12 16,14"/>
    </svg>
  );
}

function IconSimulador({ size = 16 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
    </svg>
  );
}

function IconSun({ size = 16 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="5"/>
      <line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
      <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
    </svg>
  );
}

function IconMoon({ size = 16 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </svg>
  );
}

function IconLogout({ size = 16 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
      <polyline points="16,17 21,12 16,7"/>
      <line x1="21" y1="12" x2="9" y2="12"/>
    </svg>
  );
}

function IconCidadaosPage({ size = 16 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
      <circle cx="9" cy="7" r="4"/>
      <line x1="23" y1="11" x2="17" y2="11"/>
    </svg>
  );
}

function IconCadastros({ size = 16 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
      <circle cx="9" cy="7" r="4"/>
      <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
      <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
    </svg>
  );
}
