import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";

const API = "http://localhost:8000";

type Message = {
  role: "user" | "assistant";
  text: string;
  sources?: string[];
};

export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      text: "Olá, fazendeiro! Sou seu guia de Stardew Valley. Como posso ajudar?",
    },
  ]);
  const [input, setInput] = useState("");
  const [gameState, setGameState] = useState("");
  const [editingState, setEditingState] = useState(false);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    const question = input.trim();
    if (!question || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setLoading(true);

    // placeholder para a resposta do assistente
    setMessages((prev) => [...prev, { role: "assistant", text: "" }]);

    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          game_state: gameState,
          // últimas 6 mensagens completas (exclui o placeholder vazio que acabou de ser adicionado)
          history: messages.slice(-7, -1).map((m) => ({ role: m.role, text: m.text })),
        }),
      });

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const data = JSON.parse(line.slice(6));

          if (data.type === "token") {
            setMessages((prev) => {
              const updated = [...prev];
              updated[updated.length - 1] = {
                ...updated[updated.length - 1],
                text: updated[updated.length - 1].text + data.text,
              };
              return updated;
            });
          } else if (data.type === "sources") {
            setMessages((prev) => {
              const updated = [...prev];
              updated[updated.length - 1] = {
                ...updated[updated.length - 1],
                sources: data.sources,
              };
              return updated;
            });
          }
        }
      }
    } catch {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          ...updated[updated.length - 1],
          text: "Erro ao conectar com o servidor. O backend está rodando?",
        };
        return updated;
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="w-screen h-screen bg-cover bg-center flex items-center justify-center"
      style={{ backgroundImage: "url('/bg.jpeg')" }}
    >
      {/* Painel principal */}
      <div className="flex flex-col w-[680px] h-[80vh] rounded-sm overflow-hidden"
           style={{ border: "4px solid #3D2B1F", boxShadow: "0 0 0 2px #8B5E3C, 6px 6px 0 rgba(0,0,0,0.5)" }}>

        {/* Header */}
        <div className="bg-wood px-4 py-2 flex items-center justify-between"
             style={{ borderBottom: "3px solid #3D2B1F" }}>
          <span className="text-gold text-2xl tracking-wide">⚒ Stardew Assistant</span>
          <button
            onClick={() => setEditingState((v) => !v)}
            className="text-parchment text-lg opacity-80 hover:opacity-100 transition-opacity"
          >
            {editingState ? "✕ fechar" : "📋 estado"}
          </button>
        </div>

        {/* Barra de estado do jogo (colapsável) */}
        {editingState && (
          <div className="bg-bark px-4 py-2 flex gap-2 items-center"
               style={{ borderBottom: "2px solid #3D2B1F" }}>
            <span className="text-gold text-lg whitespace-nowrap">📅 Estado:</span>
            <input
              className="flex-1 bg-transparent text-parchment text-lg outline-none placeholder-stone"
              placeholder="Ex: Ano 1, Verão dia 5. Tenho 15k gold. Falta vault bundle."
              value={gameState}
              onChange={(e) => setGameState(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && setEditingState(false)}
            />
            <button
              onClick={() => setEditingState(false)}
              className="text-grass text-lg hover:text-gold transition-colors"
            >
              ✓
            </button>
          </div>
        )}

        {gameState && !editingState && (
          <div className="bg-bark/80 px-4 py-1" style={{ borderBottom: "2px solid #3D2B1F" }}>
            <span className="text-stone text-base">📅 {gameState}</span>
          </div>
        )}

        {/* Mensagens */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3"
             style={{ background: "rgba(20, 12, 6, 0.82)" }}>
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[85%] px-3 py-2 rounded-sm text-xl leading-snug
                ${msg.role === "user"
                  ? "bg-grass/80 text-white"
                  : "bg-parchment/90 text-bark"
                }`}
                style={{ border: "2px solid", borderColor: msg.role === "user" ? "#3A7A22" : "#8B5E3C" }}>
                {msg.role === "assistant" ? (
                  <div className="prose-stardew">
                    <ReactMarkdown
                      components={{
                        p: ({ children }) => <p className="mb-1 last:mb-0">{children}</p>,
                        strong: ({ children }) => <strong className="text-wood font-bold">{children}</strong>,
                        ol: ({ children }) => <ol className="list-decimal list-inside space-y-0.5 my-1">{children}</ol>,
                        ul: ({ children }) => <ul className="list-disc list-inside space-y-0.5 my-1">{children}</ul>,
                        li: ({ children }) => <li>{children}</li>,
                        h1: ({ children }) => <p className="font-bold text-wood">{children}</p>,
                        h2: ({ children }) => <p className="font-bold text-wood">{children}</p>,
                        h3: ({ children }) => <p className="font-bold text-wood">{children}</p>,
                      }}
                    >
                      {msg.text}
                    </ReactMarkdown>
                    {msg.text === "" && loading && (
                      <span className="animate-pulse text-stone">▌</span>
                    )}
                  </div>
                ) : (
                  <span>{msg.text}</span>
                )}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-1 pt-1 border-t border-wood/40">
                    <span className="text-stone text-base">
                      Fontes: {msg.sources.join(", ")}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="flex gap-2 p-3 bg-bark"
             style={{ borderTop: "3px solid #3D2B1F" }}>
          <input
            className="flex-1 bg-black/40 text-parchment text-xl px-3 py-2 rounded-sm outline-none
                       placeholder-stone focus:bg-black/60 transition-colors"
            style={{ border: "2px solid #8B5E3C" }}
            placeholder="Pergunte algo..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="px-4 py-2 text-xl text-bark font-bold rounded-sm transition-all
                       disabled:opacity-40"
            style={{
              background: loading ? "#A09080" : "#F0C040",
              border: "2px solid #3D2B1F",
              boxShadow: loading ? "none" : "2px 2px 0 #3D2B1F",
            }}
          >
            {loading ? "..." : "Enviar"}
          </button>
        </div>
      </div>
    </div>
  );
}
