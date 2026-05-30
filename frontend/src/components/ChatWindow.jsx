import { useState, useRef, useEffect } from "react";
import axios from "axios";

function ChatWindow({ onChecklistUpdate }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hi — I'm your onboarding assistant. To get started, tell me your name, role (backend / frontend / devops), experience level (intern / junior / senior), and the tech stack you'll be working with.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [userId, setUserId] = useState(() => {
    const saved = localStorage.getItem("onboarding_user_id");
    return saved ? parseInt(saved) : null;
  });
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const autoResize = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 120) + "px";
  };

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg = { role: "user", content: text };
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
    setLoading(true);

    const history = updatedMessages.slice(1).map((m) => ({
      role: m.role,
      content: m.content,
    }));

    try {
      const res = await axios.post("http://localhost:8000/chat", {
        message: text,
        history,
        user_id: userId,
      });

      const { reply, user_id, checklist } = res.data;
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
      
      if (user_id) {
        setUserId(user_id);
        localStorage.setItem("onboarding_user_id", user_id);
      }
      
      if (checklist !== undefined && checklist !== null) onChecklistUpdate(checklist);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Could not reach the backend. Make sure FastAPI is running on localhost:8000.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat">
      <div className="chat-topbar">
        <div className="chat-topbar-left">
          <span className="status-dot" />
          <span className="chat-title">Assistant</span>
        </div>
        <span className="chat-model-tag">AI · OpenRouter</span>
      </div>

      <div className="chat-body">
        {messages.map((msg, i) => (
          <div key={i} className={`msg-row ${msg.role}`}>
            {msg.role === "assistant" && (
              <div className="msg-avatar">A</div>
            )}
            <div className={`msg-bubble ${msg.role}`}>
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="msg-row assistant">
            <div className="msg-avatar">A</div>
            <div className="msg-bubble assistant typing-bubble">
              <span className="dot" /><span className="dot" /><span className="dot" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="chat-inputbar">
        <textarea
          ref={textareaRef}
          className="chat-textarea"
          rows={1}
          placeholder="Message..."
          value={input}
          onChange={(e) => { setInput(e.target.value); autoResize(); }}
          onKeyDown={handleKeyDown}
        />
        <button
          className={`send-btn ${!input.trim() || loading ? "disabled" : ""}`}
          onClick={sendMessage}
          disabled={!input.trim() || loading}
          aria-label="Send"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M1 7h12M7 1l6 6-6 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;