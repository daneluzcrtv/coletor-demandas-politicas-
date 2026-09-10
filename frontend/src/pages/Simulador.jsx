import React, { useState, useRef, useEffect } from "react";

const WA_ID_TESTE = "5500000000000";

const EXEMPLO_CONVERSA = [
  { remetente: "cidadao", texto: "Oi" },
  { remetente: "bot", texto: "Olá! 👋 Bem-vindo ao atendimento digital do gabinete.\n\nAqui você pode registrar demandas para o seu bairro de forma rápida e fácil.\n\nPara começar, qual é o seu *nome completo*?" },
  { remetente: "cidadao", texto: "João Silva" },
  { remetente: "bot", texto: "Obrigado, João! 😊\n\nAgora preciso do seu *CPF* para cadastro:" },
  { remetente: "cidadao", texto: "123.456.789-00" },
  { remetente: "bot", texto: "Perfeito! Qual é o seu *telefone de contato*?\n\n_(pode ser este mesmo número do WhatsApp)_" },
  { remetente: "cidadao", texto: "11 99999-0000" },
  { remetente: "bot", texto: "Anotado! Agora me diga: em qual *bairro* você mora?" },
  { remetente: "cidadao", texto: "Centro" },
  { remetente: "bot", texto: "Ótimo! E qual é o seu *endereço completo*?\n\n_(rua, número e complemento)_" },
  { remetente: "cidadao", texto: "Rua das Flores, 142, apto 3" },
  { remetente: "bot", texto: "Tudo certo! Agora me conte: *qual é a sua demanda?*\n\nDescreva o problema com o máximo de detalhes possível." },
  { remetente: "cidadao", texto: "Tem um buraco grande na Rua das Flores, perto da escola municipal. Está causando acidentes e já danificou vários carros." },
  { remetente: "bot", texto: "Entendi! Vou registrar sua demanda:\n\n👤 Nome: João Silva\n📞 Telefone: 11 99999-0000\n📍 Bairro: Centro\n🏠 Endereço: Rua das Flores, 142, apto 3\n🔧 Categoria: Infraestrutura\n📝 Descrição: Buraco na Rua das Flores, próximo à escola municipal\n\nConfirma o registro? (sim/não)" },
  { remetente: "cidadao", texto: "sim" },
  { remetente: "bot", texto: "✅ Demanda registrada com sucesso!\n\nSeu protocolo é *#2025-0042*.\n\nVocê receberá atualizações aqui pelo WhatsApp. Obrigado, João! 🙏" },
  { remetente: "sistema", texto: "✅ Demanda registrada — Protocolo #2025-0042" },
];

export default function Simulador() {
  const [mensagens, setMensagens] = useState(EXEMPLO_CONVERSA);
  const [input, setInput] = useState("");
  const [enviando, setEnviando] = useState(false);
  const fimRef = useRef(null);

  useEffect(() => {
    fimRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [mensagens]);

  async function enviar(e) {
    e.preventDefault();
    if (!input.trim() || enviando) return;

    const texto = input.trim();
    setInput("");
    setMensagens((prev) => [...prev, { remetente: "cidadao", texto }]);
    setEnviando(true);

    try {
      const res = await fetch("/api/simular/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ wa_id: WA_ID_TESTE, mensagem: texto }),
      });
      const dados = await res.json();

      setMensagens((prev) => [
        ...prev,
        { remetente: "bot", texto: dados.resposta },
        ...(dados.demanda_registrada
          ? [{ remetente: "sistema", texto: `✅ Demanda registrada — Protocolo #${dados.protocolo}` }]
          : []),
      ]);
    } catch {
      setMensagens((prev) => [
        ...prev,
        { remetente: "sistema", texto: "❌ Erro ao conectar com o servidor." },
      ]);
    } finally {
      setEnviando(false);
    }
  }

  function limpar() {
    setMensagens([]);
  }

  function carregarExemplo() {
    setMensagens(EXEMPLO_CONVERSA);
  }

  return (
    <>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
        <h2 className="page-title" style={{ margin: 0 }}>Simulador do Bot</h2>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={carregarExemplo} style={{ padding: "6px 14px", border: "1px solid var(--primary)", borderRadius: 6, background: "rgba(249,115,22,0.1)", cursor: "pointer", fontSize: 13, color: "var(--primary)", fontWeight: 600 }}>
            Ver exemplo
          </button>
          <button onClick={limpar} style={{ padding: "6px 14px", border: "1px solid var(--border)", borderRadius: 6, background: "var(--surface)", cursor: "pointer", fontSize: 13, color: "var(--muted)" }}>
            Limpar
          </button>
        </div>
      </div>

      <p className="muted" style={{ marginBottom: 16, fontSize: 13 }}>
        Simula uma conversa via WhatsApp. As demandas registradas aqui aparecem na lista de demandas.
      </p>

      {/* Janela do chat */}
      <div style={{
        background: "var(--surface)",
        border: "1px solid var(--border)",
        borderRadius: 10,
        height: 480,
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}>
        <div style={{ flex: 1, overflowY: "auto", padding: 16, display: "flex", flexDirection: "column", gap: 10 }}>
          {mensagens.length === 0 && (
            <p className="muted" style={{ textAlign: "center", marginTop: 80, fontSize: 13 }}>
              Digite uma mensagem para iniciar a conversa com o bot.
            </p>
          )}

          {mensagens.map((m, i) => (
            <Balao key={i} {...m} />
          ))}

          {enviando && (
            <div style={{ alignSelf: "flex-start" }}>
              <div style={estiloBalao("bot")}>
                <span style={{ letterSpacing: 2 }}>···</span>
              </div>
            </div>
          )}

          <div ref={fimRef} />
        </div>

        {/* Input */}
        <form onSubmit={enviar} style={{ borderTop: "1px solid var(--border)", display: "flex", gap: 8, padding: 12 }}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Digite sua mensagem..."
            disabled={enviando}
            style={{
              flex: 1,
              border: "1px solid var(--border)",
              borderRadius: 6,
              padding: "8px 12px",
              fontSize: 14,
            }}
          />
          <button
            type="submit"
            disabled={enviando || !input.trim()}
            style={{
              padding: "8px 18px",
              background: "var(--primary)",
              color: "#fff",
              border: "none",
              borderRadius: 6,
              cursor: "pointer",
              fontWeight: 600,
              opacity: enviando || !input.trim() ? 0.5 : 1,
            }}
          >
            Enviar
          </button>
        </form>
      </div>
    </>
  );
}

function estiloBalao(remetente) {
  const base = {
    maxWidth: "72%",
    padding: "8px 12px",
    borderRadius: 10,
    fontSize: 14,
    lineHeight: 1.5,
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
  };
  if (remetente === "cidadao") return { ...base, background: "rgba(249,115,22,0.15)", color: "#fdba74", alignSelf: "flex-end", borderBottomRightRadius: 2 };
  if (remetente === "bot")     return { ...base, background: "#263349", color: "#e2e8f0", alignSelf: "flex-start", borderBottomLeftRadius: 2 };
  return { ...base, background: "rgba(34,197,94,0.12)", alignSelf: "center", fontSize: 12, color: "#4ade80", textAlign: "center" };
}

function Balao({ remetente, texto }) {
  return (
    <div style={{ display: "flex", justifyContent: remetente === "cidadao" ? "flex-end" : remetente === "sistema" ? "center" : "flex-start" }}>
      <div style={estiloBalao(remetente)}>{texto}</div>
    </div>
  );
}
