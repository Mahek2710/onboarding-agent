import { useState } from "react";
import ChatWindow from "./components/ChatWindow";
import Checklist from "./components/Checklist";
import "./App.css";

function App() {
  const [checklist, setChecklist] = useState([]);
  const [theme, setTheme] = useState("dark");

  const toggleTheme = () => setTheme((t) => (t === "dark" ? "light" : "dark"));

  return (
    <div className={`root ${theme}`} data-theme={theme}>
      <aside className="sidebar">
        <div className="sidebar-top">
          <div className="brand">
            <span className="brand-icon">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <rect x="1" y="1" width="7" height="7" rx="2" fill="currentColor" opacity="0.9"/>
                <rect x="10" y="1" width="7" height="7" rx="2" fill="currentColor" opacity="0.5"/>
                <rect x="1" y="10" width="7" height="7" rx="2" fill="currentColor" opacity="0.5"/>
                <rect x="10" y="10" width="7" height="7" rx="2" fill="currentColor" opacity="0.9"/>
              </svg>
            </span>
            <span className="brand-name">Onboard</span>
          </div>
          <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === "dark" ? (
              <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
                <circle cx="7.5" cy="7.5" r="3" stroke="currentColor" strokeWidth="1.3"/>
                <line x1="7.5" y1="1" x2="7.5" y2="2.5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
                <line x1="7.5" y1="12.5" x2="7.5" y2="14" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
                <line x1="1" y1="7.5" x2="2.5" y2="7.5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
                <line x1="12.5" y1="7.5" x2="14" y2="7.5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
                <line x1="3.1" y1="3.1" x2="4.15" y2="4.15" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
                <line x1="10.85" y1="10.85" x2="11.9" y2="11.9" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
                <line x1="10.85" y1="4.15" x2="11.9" y2="3.1" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
                <line x1="3.1" y1="11.9" x2="4.15" y2="10.85" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
              </svg>
            ) : (
              <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
                <path d="M7.5 1.5C4.19 1.5 1.5 4.19 1.5 7.5C1.5 10.81 4.19 13.5 7.5 13.5C10.2 13.5 12.5 11.8 13.3 9.4C12.7 9.6 12.1 9.7 11.5 9.7C8.74 9.7 6.5 7.46 6.5 4.7C6.5 3.5 6.9 2.4 7.5 1.5Z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round"/>
              </svg>
            )}
          </button>
        </div>

        <div className="sidebar-content">
          <Checklist checklist={checklist} />
        </div>

        <div className="sidebar-footer">
          <div className="footer-meta">
            <span className="footer-dot" />
            <span>Internal tool · v1.0</span>
          </div>
        </div>
      </aside>

      <main className="main">
        <ChatWindow onChecklistUpdate={setChecklist} />
      </main>
    </div>
  );
}

export default App;
