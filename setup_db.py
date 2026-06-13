import psycopg2

conn = psycopg2.connect(
    host="cartwatch-db.cp26g6s4i09v.eu-north-1.rds.amazonaws.com",
    port=5432,
    database="cartwatch",
    user="cartwatch_user",
    password="cartwatch_pass_2024"
)

cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(50),
        event_type VARCHAR(50),
        product_name VARCHAR(100),
        price INTEGER,
        timestamp TIMESTAMPTZ
    );
""")

conn.commit()
cur.close()
conn.close()
print("Table created successfully!")
