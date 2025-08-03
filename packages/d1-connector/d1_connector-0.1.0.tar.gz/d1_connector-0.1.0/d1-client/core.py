# d1_connector/core.py
import asyncio
import json
import websockets
from websockets.exceptions import WebSocketException, ConnectionClosed

_shared_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_shared_loop)

def _run(coro):
    return _shared_loop.run_until_complete(coro)

class D1Cursor:
    def __init__(self, websocket, connection):
        self.websocket = websocket
        self._connection = connection
        self._last_result = None
        self._closed = False
        self._connection._register_cursor(self)

    async def _send(self, message):
        await self.websocket.send(json.dumps(message))
        response = await self.websocket.recv()
        data = json.loads(response)
        if "error" in data:
            raise Exception(f"Server error: {data['error']}")
        self._last_result = data.get("result")

    def execute(self, query, params=None):
        _run(self._send({"sql": query, "params": params or []}))

    def fetchall(self):
        if not self._last_result:
            return []
        return self._last_result.get("results") or []

    def fetchone(self):
        rows = self.fetchall()
        return rows[0] if rows else None

    def close(self):
        if not self._closed:
            try:
                _run(self.websocket.close())
            except:
                pass
            self._closed = True
            self._connection._unregister_cursor(self)

    def __del__(self):
        self.close()

class D1Connection:
    def __init__(self, host, username, password, database):
        self.url = f"ws://{host}/ws?username={username}&password={password}&database={database}"
        try:
            self.websocket = _run(websockets.connect(self.url))
        except WebSocketException as e:
            raise Exception(f"WebSocket connection failed: {e}")
        except Exception as e:
            raise Exception(f"Failed to connect to WebSocket: {e}")
        self._cursors = []
        self._closed = False

    def _register_cursor(self, cursor):
        self._cursors.append(cursor)

    def _unregister_cursor(self, cursor):
        if cursor in self._cursors:
            self._cursors.remove(cursor)

    def cursor(self):
        return D1Cursor(self.websocket, self)

    def close(self):
        if not self._closed:
            for cursor in self._cursors[:]:
                cursor.close()
            try:
                _run(self.websocket.close())
            except:
                pass
            self._closed = True

    def __del__(self):
        self.close()

def connect(host, username, password, database):
    return D1Connection(host, username, password, database)
