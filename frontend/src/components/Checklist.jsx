function Checklist({ checklist }) {
  const done = checklist.filter((t) => t.is_completed).length;
  const total = checklist.length;
  const percent = total > 0 ? Math.round((done / total) * 100) : 0;

  return (
    <div className="checklist">
      <div className="checklist-label">Onboarding Progress</div>

      {total === 0 ? (
        <div className="checklist-empty">
          <div className="empty-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.3">
              <rect x="3" y="3" width="18" height="18" rx="3"/>
              <path d="M9 12l2 2 4-4"/>
            </svg>
          </div>
          <p>Your checklist appears once you introduce yourself in the chat.</p>
        </div>
      ) : (
        <>
          <div className="progress-block">
            <div className="progress-numbers">
              <span className="progress-percent">{percent}%</span>
              <span className="progress-fraction">{done} / {total} tasks</span>
            </div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${percent}%` }} />
            </div>
          </div>

          <ul className="task-list">
            {checklist.map((task) => (
              <li key={task.id} className={`task-item ${task.is_completed ? "completed" : ""}`}>
                <span className="task-check">
                  {task.is_completed ? (
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                      <path d="M2.5 6l2.5 2.5 4.5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  ) : null}
                </span>
                <span className="task-name">{task.task_name}</span>
              </li>
            ))}
          </ul>

          {done === total && total > 0 && (
            <div className="checklist-complete-badge">
              <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                <path d="M2 6.5l3 3 6-6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Onboarding complete — HR notified
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Checklist;
