import sqlite3

DB_PATH = "onboarding.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            experience TEXT NOT NULL,
            tech_stack TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checklists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            is_completed BOOLEAN DEFAULT FALSE,
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database ready!")

TASKS = {
    ("backend", "intern"): [
        "Install Node.js aur npm",
        "Clone backend repository",
        "Run local server",
        "Read API standards document",
        "Complete starter bug fix",
    ],
    ("backend", "junior"): [
        "Clone backend repository",
        "Setup local environment",
        "Read API standards document",
        "Read database schema",
        "Review PR guidelines",
    ],
    ("backend", "senior"): [
        "Clone backend repository",
        "Review system architecture",
        "Read API standards document",
        "Review deployment pipeline",
        "Schedule team intro meeting",
    ],
    ("frontend", "intern"): [
        "Install Node.js aur npm",
        "Clone frontend repository",
        "Run npm install aur npm run dev",
        "Read component guidelines",
        "Complete starter UI task",
    ],
    ("frontend", "junior"): [
        "Clone frontend repository",
        "Setup local environment",
        "Access Figma design system",
        "Read component guidelines",
        "Review PR guidelines",
    ],
    ("frontend", "senior"): [
        "Clone frontend repository",
        "Review frontend architecture",
        "Access Figma design system",
        "Review deployment pipeline",
        "Schedule team intro meeting",
    ],
    ("devops", "intern"): [
        "Setup local Docker",
        "Clone infrastructure repo",
        "Read CI/CD pipeline docs",
        "Run test deployment",
        "Review monitoring dashboard",
    ],
    ("devops", "senior"): [
        "Clone infrastructure repo",
        "Review cloud architecture",
        "Read CI/CD pipeline docs",
        "Review security policies",
        "Schedule team intro meeting",
    ],
}

def create_user(name, role, experience, tech_stack):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO users (name, role, experience, tech_stack)
        VALUES (?, ?, ?, ?)
    ''', (name, role.lower(), experience.lower(), tech_stack))

    user_id = cursor.lastrowid

    key = (role.lower(), experience.lower())
    tasks = TASKS.get(key, TASKS.get((role.lower(), "intern"), []))

    for task in tasks:
        cursor.execute('''
            INSERT INTO checklists (user_id, task_name)
            VALUES (?, ?)
        ''', (user_id, task))

    conn.commit()
    conn.close()
    return user_id

def get_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_checklist(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM checklists
        WHERE user_id = ?
        ORDER BY id ASC
    ''', (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    return [dict(t) for t in tasks]

def mark_task_done(user_id, task_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE checklists
        SET is_completed = TRUE,
            completed_at = CURRENT_TIMESTAMP
        WHERE user_id = ? AND task_name = ?
    ''', (user_id, task_name))
    conn.commit()
    conn.close()

def is_onboarding_complete(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) as total,
               SUM(is_completed) as done
        FROM checklists WHERE user_id = ?
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result["done"] == result["total"]

if __name__ == "__main__":
    init_db()