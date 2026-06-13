from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import psycopg2
from datetime import datetime, timezone

app = FastAPI()

DB_HOST = "cartwatch-db.cp26g6s4i09v.eu-north-1.rds.amazonaws.com"
DB_NAME = "cartwatch"
DB_USER = "cartwatch_user"
DB_PASS = "cartwatch_pass_2024"

def get_db():
    return psycopg2.connect(
        host=DB_HOST, port=5432,
        database=DB_NAME, user=DB_USER, password=DB_PASS
    )

@app.get("/", response_class=HTMLResponse)
def dashboard():
    conn = get_db()
    cur = conn.cursor()

    # Total events
    cur.execute("SELECT COUNT(*) FROM events;")
    total = cur.fetchone()[0]

    # Abandonment rate
    cur.execute("SELECT COUNT(*) FROM events WHERE event_type = 'abandon_cart';")
    abandonments = cur.fetchone()[0]
    rate = round((abandonments / total * 100), 1) if total > 0 else 0

    # Top abandoned products
    cur.execute("""
        SELECT product_name, COUNT(*) as count
        FROM events WHERE event_type = 'abandon_cart'
        GROUP BY product_name ORDER BY count DESC LIMIT 5;
    """)
    top_abandoned = cur.fetchall()

    # Recent events
    cur.execute("""
        SELECT event_type, product_name, user_id, timestamp
        FROM events ORDER BY timestamp DESC LIMIT 10;
    """)
    recent = cur.fetchall()

    cur.close()
    conn.close()

    # Build HTML
    top_rows = "".join([
        f"<tr><td>{p}</td><td>{c}</td></tr>"
        for p, c in top_abandoned
    ])
    recent_rows = "".join([
        f"<tr><td>{e}</td><td>{p}</td><td>{u}</td><td>{t}</td></tr>"
        for e, p, u, t in recent
    ])

    return f"""
    <html>
    <head>
        <title>CartWatch Dashboard</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body {{ font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; padding: 2rem; }}
            h1 {{ color: #38bdf8; }}
            .stats {{ display: flex; gap: 2rem; margin: 2rem 0; }}
            .card {{ background: #1e293b; padding: 1.5rem; border-radius: 8px; min-width: 150px; }}
            .card h2 {{ margin: 0; font-size: 2rem; color: #38bdf8; }}
            .card p {{ margin: 0; color: #94a3b8; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
            th {{ background: #1e293b; padding: 0.75rem; text-align: left; color: #38bdf8; }}
            td {{ padding: 0.75rem; border-bottom: 1px solid #1e293b; }}
            h3 {{ color: #38bdf8; margin-top: 2rem; }}
        </style>
    </head>
    <body>
        <h1>🛒 CartWatch — Live Dashboard</h1>
        <div class="stats">
            <div class="card"><h2>{total}</h2><p>Total Events</p></div>
            <div class="card"><h2>{abandonments}</h2><p>Abandonments</p></div>
            <div class="card"><h2>{rate}%</h2><p>Abandonment Rate</p></div>
        </div>

        <h3>Top Abandoned Products</h3>
        <table>
            <tr><th>Product</th><th>Abandonments</th></tr>
            {top_rows}
        </table>

        <h3>Recent Events</h3>
        <table>
            <tr><th>Event</th><th>Product</th><th>User</th><th>Time</th></tr>
            {recent_rows}
        </table>

        <p style="color:#475569; margin-top:2rem;">Auto-refreshes every 5 seconds</p>
    </body>
    </html>
    """

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/stats")
def stats():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM events;")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM events WHERE event_type = 'abandon_cart';")
    abandonments = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {
        "total_events": total,
        "abandonments": abandonments,
        "abandonment_rate": round((abandonments / total * 100), 1) if total > 0 else 0
    }
