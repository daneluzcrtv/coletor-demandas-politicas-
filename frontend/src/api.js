const BASE = "/api";

function authHeader() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function handle401() {
  localStorage.removeItem("token");
  window.location.href = "/";
}

async function get(path, params = {}) {
  const url = new URL(BASE + path, window.location.origin);
  Object.entries(params).forEach(([k, v]) => v != null && url.searchParams.set(k, v));
  const res = await fetch(url, { headers: authHeader() });
  if (res.status === 401) { handle401(); return; }
  if (!res.ok) throw new Error(`Erro ${res.status}: ${path}`);
  return res.json();
}

async function post(path, body) {
  const res = await fetch(BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(body),
  });
  if (res.status === 401) { handle401(); return; }
  if (!res.ok) throw new Error(`Erro ${res.status}`);
  return res.json();
}

async function patch(path, body) {
  const res = await fetch(BASE + path, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(body),
  });
  if (res.status === 401) { handle401(); return; }
  if (!res.ok) throw new Error(`Erro ${res.status}`);
  return res.json();
}

async function postForm(path, formData) {
  const res = await fetch(BASE + path, {
    method: "POST",
    headers: authHeader(),
    body: formData,
  });
  if (res.status === 401) { handle401(); return; }
  if (!res.ok) throw new Error(`Erro ${res.status}`);
  return res.json();
}

async function del(path) {
  const res = await fetch(BASE + path, { method: "DELETE", headers: authHeader() });
  if (res.status === 401) { handle401(); return; }
  if (!res.ok) throw new Error(`Erro ${res.status}`);
}

export const api = {
  auth: {
    login: (email, senha) => post("/auth/login", { email, senha }),
    me:    ()             => get("/auth/me"),
  },
  demandas: {
    listar:    (filtros)     => get("/demandas/", filtros),
    detalhe:   (id)          => get(`/demandas/${id}/detalhe`),
    atualizar: (id, dados)   => patch(`/demandas/${id}`, dados),
  },
  bairros: {
    listar:    ()            => get("/bairros/"),
    criar:     (dados)       => post("/bairros/", dados),
    atualizar: (id, dados)   => patch(`/bairros/${id}`, dados),
    deletar:   (id)          => del(`/bairros/${id}`),
  },
  assessores: {
    listar:        ()            => get("/assessores/"),
    criar:         (dados)       => post("/assessores/", dados),
    atualizar:     (id, dados)   => patch(`/assessores/${id}`, dados),
    deletar:       (id)          => del(`/assessores/${id}`),
    definirSenha:  (id, senha)   => post(`/assessores/${id}/senha`, { senha }),
  },
  relatorio: {
    mensal: (mes) => get("/relatorio/mensal", { mes }),
  },
  analise: {
    eleitoral: (mes)         => get("/analise/eleitoral", { mes }),
    simular:   (bairro, acao) => get("/analise/simular", { bairro, acao }),
  },
  acompanhamento: {
    listar:  (demandaId)          => get(`/acompanhamento/demanda/${demandaId}`),
    criar:   (demandaId, formData) => postForm(`/acompanhamento/demanda/${demandaId}`, formData),
    deletar: (id)                  => del(`/acompanhamento/${id}`),
    urlFoto: (fotoId)              => `${BASE}/acompanhamento/foto/${fotoId}`,
  },
};
