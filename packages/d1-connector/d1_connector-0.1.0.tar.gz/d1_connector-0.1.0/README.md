# 🌐 d1-client

**`d1-client`** is a lightweight Python client designed to interface with your **Cloudflare D1 database** through a **WebSocket Worker**.  
It replicates the familiar `mysql.connector` pattern, **without needing to use async/await**.

🔗 **Worker code:** [github.com/geetflow/d1_connector](https://github.com/geetflow/d1_connector)



## 🚀 Features

- ✅ 100% compatible with `mysql.connector`-style usage
- 🔌 Simple `connect → cursor → execute → fetch` pattern
- 🧠 No need to manage `asyncio` or `await`
- 🔄 Automatic cleanup of cursors and connections
- 🧵 Internally managed shared event loop
- 🌍 WebSocket-based D1 access via a custom Worker

---

## 📦 Installation

```bash
pip install d1-client
````

Or install directly from source:

```bash
git clone https://github.com/geetflow/d1_connector
cd d1_connector
pip install -e .
```

---

## ✨ Usage Example

```python
from d1_client import connect

conn = connect(
    host="d1_connector.your-worker.workers.dev",
    username="root",
    password="yourpass",
    database="your_db"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM tracks LIMIT 1")
rows = cursor.fetchall()
print("Query Results:", rows)

# No need to call cursor.close() or conn.close()
```

---

## 🔧 How It Works

The client communicates with a WebSocket-enabled **Cloudflare Worker** that acts like a SQL gateway.
It sends queries as JSON, and the Worker executes them using Cloudflare D1 and returns results.

**Client sends:**

```json
{
  "sql": "SELECT * FROM users WHERE id = ?",
  "params": [123]
}
```

**Worker responds:**

```json
{
  "result": {
    "results": [ { "id": 123, "name": "Alice" } ]
  }
}
```

Worker source code:
[https://github.com/geetflow/d1\_connector](https://github.com/geetflow/d1_connector)

---

## 🧪 API Reference

### `connect(host, username, password, database)`

Returns a `D1Connection` object.

### `D1Connection.cursor()`

Returns a `D1Cursor` object.

### `D1Cursor.execute(query, params=None)`

Executes an SQL query with optional parameters.

### `D1Cursor.fetchall()`

Returns a list of rows (each row is a dictionary).

### `D1Cursor.fetchone()`

Returns a single row (or `None` if empty).

---

## 📂 Project Structure

```
d1-client/
├── d1_client/
│   ├── __init__.py
│   └── core.py
├── setup.py
├── LICENSE
└── README.md
```

---

## 📜 License

MIT License © [GeetFlow](https://geetflow.com)

---

## 🔗 Links

* 🌍 Worker Source Code: [github.com/geetflow/d1\_connector](https://github.com/geetflow/d1_connector)
* 📦 PyPI (coming soon)

---

## 💬 Need Help?

If you're facing issues with query formats, D1 errors, or WebSocket connections:

* Double check that your Worker is deployed and working
* Ensure the `host`, `username`, and `password` match your Cloudflare Worker setup

---

## ⭐ Example Query (with D1 compatibility)

```python
query = """
SELECT 
  t.id, t.name, t.src, t.image, t.share_id, ts.stream_seconds
FROM tracks t
LEFT JOIN tracks_stream ts ON t.id = ts.track_id
WHERE date(t.created_at) >= date('now', '-10 days')
  AND t.releases = 1
ORDER BY ts.stream_seconds DESC, t.plays DESC
LIMIT 50
"""

cursor.execute(query)
print(cursor.fetchall())
```

💡 Note: Cloudflare D1 uses SQLite syntax. Replace MySQL’s `NOW() - INTERVAL` with `date('now', '-10 days')`

---

Made with ❤️ by [GeetFlow](https://geetflow.com)



Would you like me to also generate `setup.py`, `LICENSE`, and directory structure in real files so you can publish to PyPI?

