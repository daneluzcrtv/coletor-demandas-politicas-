import React from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid,
  PieChart, Pie, Cell,
} from "recharts";

const ACCENT = "#f97316";
const GREEN  = "#22c55e";
const RED    = "#ef4444";
const AMBER  = "#f59e0b";
const PURPLE = "#8b5cf6";

const DEMO = {
  kpis: [
    { label: "Demandas Registradas", value: 347, trend: "+12% vs. ago/25", up: true },
    { label: "Bairros Ativos",       value: 18,  trend: "+3 este ano",      up: true },
    { label: "Cidadãos Atendidos",   value: 284, trend: "+31 este mês",     up: true },
    { label: "Taxa de Resolução",    value: "67%", trend: "+5 pontos",      up: true },
  ],
  por_categoria: [
    { name: "Infraestrutura", value: 89 },
    { name: "Iluminação",     value: 67 },
    { name: "Saúde",          value: 54 },
    { name: "Segurança",      value: 48 },
    { name: "Transporte",     value: 38 },
    { name: "Educação",       value: 27 },
    { name: "Meio Ambiente",  value: 15 },
    { name: "Assist. Social", value: 9  },
  ],
  por_bairro: [
    { bairro: "Centro",       total: 52, abertas: 18 },
    { bairro: "Pq. Paraíso",  total: 44, abertas: 22 },
    { bairro: "Jurubatuba",   total: 38, abertas: 15 },
    { bairro: "Cipó",         total: 31, abertas: 19 },
    { bairro: "Ch. Paraíso",  total: 28, abertas: 8  },
    { bairro: "R. Grande",    total: 22, abertas: 12 },
    { bairro: "M. Bambu",     total: 19, abertas: 14 },
    { bairro: "Jd. S. Paulo", total: 16, abertas: 6  },
  ],
  tendencia: [
    { mes: "Mar", demandas: 42,  resolvidas: 28 },
    { mes: "Abr", demandas: 58,  resolvidas: 39 },
    { mes: "Mai", demandas: 67,  resolvidas: 45 },
    { mes: "Jun", demandas: 73,  resolvidas: 52 },
    { mes: "Jul", demandas: 89,  resolvidas: 61 },
    { mes: "Ago", demandas: 104, resolvidas: 73 },
  ],
  status: [
    { name: "Concluídas",    value: 134, color: GREEN },
    { name: "Em andamento",  value: 99,  color: AMBER },
    { name: "Abertas",       value: 114, color: RED   },
  ],
  pontos_criticos: [
    {
      bairro: "Parque Paraíso",
      urgencia: "alta",
      problema: "22 demandas abertas de iluminação e infraestrutura sem resposta há +30 dias",
      impacto: "~2.400 eleitores potencialmente insatisfeitos",
    },
    {
      bairro: "Cipó",
      urgencia: "alta",
      problema: "19 demandas de segurança concentradas em 2 ruas — risco de mobilização adversária",
      impacto: "~1.100 eleitores em zona de alta disputa",
    },
    {
      bairro: "Morro do Bambu",
      urgencia: "media",
      problema: "14 demandas de saneamento básico não encaminhadas à SABESP",
      impacto: "Área historicamente negligenciada — potencial de virada eleitoral",
    },
  ],
  oportunidades: [
    {
      bairro: "Centro",
      acao: "Concluir 18 demandas de pavimentação já em andamento",
      impacto: "Alto tráfego garante máxima visibilidade política das entregas",
    },
    {
      bairro: "Chácara Paraíso",
      acao: "Evento de entrega + cadastro comunitário",
      impacto: "Taxa de resolução 71% cria terreno fértil para campanha positiva",
    },
    {
      bairro: "Rancho Grande",
      acao: "Mutirão de iluminação (12 pontos pendentes)",
      impacto: "Baixo custo, alta visibilidade — bairro em crescimento eleitoral",
    },
  ],
  ranking: [
    { bairro: "Parque Paraíso", score: 94, eleitores: 3100 },
    { bairro: "Cipó",           score: 87, eleitores: 1900 },
    { bairro: "Centro",         score: 81, eleitores: 4200 },
    { bairro: "Jurubatuba",     score: 76, eleitores: 2800 },
    { bairro: "Morro do Bambu", score: 71, eleitores: 1200 },
    { bairro: "Rancho Grande",  score: 64, eleitores: 1600 },
  ],
};

function DarkTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: "#1a1b1e", border: "1px solid #373a43", borderRadius: 8, padding: "8px 12px", fontSize: 12 }}>
      <p style={{ color: "#94a3b8", marginBottom: 4 }}>{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color, fontWeight: 700, margin: 0 }}>{p.name}: {p.value}</p>
      ))}
    </div>
  );
}

function KpiCard({ label, value, trend, up }) {
  return (
    <div style={{ background: "#25262b", border: "1px solid #373a43", borderRadius: 12, padding: "20px 22px" }}>
      <div style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 600, marginBottom: 10 }}>
        {label}
      </div>
      <div style={{ fontSize: 36, fontWeight: 800, letterSpacing: "-1.5px", color: "#f1f5f9", lineHeight: 1 }}>
        {value}
      </div>
      <div style={{ marginTop: 10, display: "flex", alignItems: "center", gap: 4, fontSize: 12 }}>
        <span style={{ color: up ? GREEN : RED, fontWeight: 700 }}>{up ? "↑" : "↓"}</span>
        <span style={{ color: "#94a3b8" }}>{trend}</span>
      </div>
    </div>
  );
}

function Panel({ title, subtitle, children, style }) {
  return (
    <div style={{ background: "#25262b", border: "1px solid #373a43", borderRadius: 12, padding: "20px 22px", ...style }}>
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 14, fontWeight: 700, color: "#e2e8f0" }}>{title}</div>
        {subtitle && <div style={{ fontSize: 12, color: "#64748b", marginTop: 2 }}>{subtitle}</div>}
      </div>
      {children}
    </div>
  );
}

export default function AnaliseEleitoral() {
  const maxScore = DEMO.ranking[0].score;

  return (
    <>
      <div style={{ marginBottom: 24 }}>
        <h2 className="page-title">Análise Eleitoral</h2>
        <p className="page-subtitle" style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 0 }}>
          Itapecerica da Serra · Agosto 2026
          <span style={{ padding: "2px 9px", background: "rgba(249,115,22,0.12)", color: "#f97316", borderRadius: 99, fontSize: 11, fontWeight: 700, letterSpacing: "0.04em" }}>
            DEMO
          </span>
        </p>
      </div>

      {/* ── KPIs ── */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 20 }}>
        {DEMO.kpis.map((k, i) => <KpiCard key={i} {...k} />)}
      </div>

      {/* ── Categorias + Status ── */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 300px", gap: 16, marginBottom: 16 }}>
        <Panel title="Demandas por Categoria" subtitle="Volume acumulado por tipo de solicitação">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={DEMO.por_categoria} layout="vertical" margin={{ left: 0, right: 24, top: 0, bottom: 0 }}>
              <XAxis type="number" tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fill: "#94a3b8", fontSize: 12 }} width={96} axisLine={false} tickLine={false} />
              <Tooltip content={<DarkTooltip />} />
              <Bar dataKey="value" fill={ACCENT} radius={[0, 4, 4, 0]} maxBarSize={20} name="Demandas" />
            </BarChart>
          </ResponsiveContainer>
        </Panel>

        <Panel title="Status Atual" subtitle="Distribuição por situação">
          <ResponsiveContainer width="100%" height={190}>
            <PieChart>
              <Pie data={DEMO.status} cx="50%" cy="50%" innerRadius={52} outerRadius={82} paddingAngle={3} dataKey="value">
                {DEMO.status.map((s, i) => <Cell key={i} fill={s.color} />)}
              </Pie>
              <Tooltip content={<DarkTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div style={{ display: "flex", flexDirection: "column", gap: 9, marginTop: 6 }}>
            {DEMO.status.map((s, i) => (
              <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#94a3b8" }}>
                  <div style={{ width: 8, height: 8, borderRadius: "50%", background: s.color, flexShrink: 0 }} />
                  {s.name}
                </div>
                <span style={{ fontSize: 14, fontWeight: 800, color: s.color }}>{s.value}</span>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      {/* ── Bairros + Tendência ── */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        <Panel title="Top Bairros por Volume" subtitle="Total de demandas · abertas em destaque">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={DEMO.por_bairro} margin={{ left: 0, right: 8, top: 4, bottom: 44 }}>
              <XAxis dataKey="bairro" tick={{ fill: "#64748b", fontSize: 10, angle: -35, textAnchor: "end" }} axisLine={false} tickLine={false} interval={0} />
              <YAxis tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
              <CartesianGrid strokeDasharray="3 3" stroke="#263349" vertical={false} />
              <Tooltip content={<DarkTooltip />} />
              <Bar dataKey="total"   fill={ACCENT} radius={[4,4,0,0]} maxBarSize={28} name="Total" />
              <Bar dataKey="abertas" fill={RED}    radius={[4,4,0,0]} maxBarSize={28} name="Abertas" fillOpacity={0.7} />
            </BarChart>
          </ResponsiveContainer>
        </Panel>

        <Panel title="Tendência Mensal" subtitle="Novas demandas vs. resolvidas — últimos 6 meses">
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={DEMO.tendencia} margin={{ left: 0, right: 12, top: 4, bottom: 4 }}>
              <XAxis dataKey="mes" tick={{ fill: "#64748b", fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
              <CartesianGrid strokeDasharray="3 3" stroke="#263349" vertical={false} />
              <Tooltip content={<DarkTooltip />} />
              <Line type="monotone" dataKey="demandas"  stroke={ACCENT} strokeWidth={2.5} dot={{ r: 4, fill: ACCENT, strokeWidth: 0 }} name="Demandas"  />
              <Line type="monotone" dataKey="resolvidas" stroke={GREEN}  strokeWidth={2.5} dot={{ r: 4, fill: GREEN,  strokeWidth: 0 }} name="Resolvidas" />
            </LineChart>
          </ResponsiveContainer>
        </Panel>
      </div>

      {/* ── Críticos + Oportunidades ── */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        <Panel title="🔴 Pontos Críticos" subtitle="Bairros que exigem ação imediata">
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {DEMO.pontos_criticos.map((p, i) => (
              <div key={i} style={{ borderLeft: `3px solid ${p.urgencia === "alta" ? RED : AMBER}`, padding: "10px 14px", background: "#2c2e35", borderRadius: "0 8px 8px 0" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4, gap: 8 }}>
                  <strong style={{ fontSize: 13, color: "#e2e8f0" }}>{p.bairro}</strong>
                  <span style={{ fontSize: 10, fontWeight: 700, color: p.urgencia === "alta" ? RED : AMBER, textTransform: "uppercase", letterSpacing: "0.05em", flexShrink: 0 }}>
                    {p.urgencia}
                  </span>
                </div>
                <p style={{ fontSize: 12, color: "#94a3b8", margin: "0 0 6px", lineHeight: 1.5 }}>{p.problema}</p>
                <p style={{ fontSize: 11, color: PURPLE, margin: 0 }}>🗳️ {p.impacto}</p>
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="🟢 Oportunidades Eleitorais" subtitle="Ações com alto retorno político">
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {DEMO.oportunidades.map((o, i) => (
              <div key={i} style={{ borderLeft: `3px solid ${GREEN}`, padding: "10px 14px", background: "#2c2e35", borderRadius: "0 8px 8px 0" }}>
                <strong style={{ fontSize: 13, color: "#e2e8f0", display: "block", marginBottom: 4 }}>{o.bairro}</strong>
                <p style={{ fontSize: 12, color: "#94a3b8", margin: "0 0 6px", lineHeight: 1.5 }}>{o.acao}</p>
                <p style={{ fontSize: 11, color: GREEN, margin: 0 }}>↑ {o.impacto}</p>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      {/* ── Ranking ── */}
      <Panel title="📊 Ranking de Prioridade Eleitoral" subtitle="Score = volume de demandas × base eleitoral afetada × urgência média" style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {DEMO.ranking.map((r, i) => {
            const pct = Math.round((r.score / maxScore) * 100);
            const cores = [ACCENT, "#fb923c", "#fdba74", "#fcd34d", "#94a3b8", "#64748b"];
            const cor = cores[i] ?? "#64748b";
            return (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span style={{ width: 22, fontSize: 12, fontWeight: 700, color: cor, textAlign: "right", flexShrink: 0 }}>#{i + 1}</span>
                <span style={{ width: 140, fontSize: 13, fontWeight: i < 2 ? 700 : 400, color: i < 2 ? "#e2e8f0" : "#94a3b8", flexShrink: 0 }}>{r.bairro}</span>
                <div style={{ flex: 1, background: "#2c2e35", borderRadius: 4, height: 8 }}>
                  <div style={{ width: `${pct}%`, height: "100%", borderRadius: 4, background: cor }} />
                </div>
                <div style={{ display: "flex", gap: 14, fontSize: 12, flexShrink: 0 }}>
                  <span style={{ fontWeight: 800, color: cor, width: 52, textAlign: "right" }}>{r.score} pts</span>
                  <span style={{ color: "#64748b", width: 68, textAlign: "right" }}>{r.eleitores.toLocaleString("pt-BR")} el.</span>
                </div>
              </div>
            );
          })}
        </div>
      </Panel>

      {/* ── Simulator hint ── */}
      <div style={{ background: "rgba(249,115,22,0.06)", border: "1px solid rgba(249,115,22,0.2)", borderRadius: 12, padding: "16px 20px", display: "flex", alignItems: "center", gap: 16 }}>
        <div style={{ fontSize: 26, flexShrink: 0 }}>🔮</div>
        <div>
          <div style={{ fontWeight: 700, fontSize: 14, color: "#e2e8f0", marginBottom: 3 }}>Simulador de Cenários disponível</div>
          <div style={{ fontSize: 12, color: "#64748b" }}>
            Acesse a aba <strong style={{ color: "#f97316" }}>Simulador do Bot</strong> para projetar o impacto eleitoral de ações hipotéticas em cada bairro.
          </div>
        </div>
      </div>
    </>
  );
}
