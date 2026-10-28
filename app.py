"""
Ofrenda AI - Web Application & Local REST API Server
Zero external npm/pip dependencies. Runs out of the box with standard Python 3.
"""

import sys
import os
import json
import mimetypes
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Import project modules
from models import Altar, Ancestor, Offering, Memory
from engine import OfrendaAIEngine
from vault import Vault

PORT = 8088
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

vault = Vault()
engine = OfrendaAIEngine()

# Auto-seed sample altar if vault is empty
def ensure_sample_seed():
    if not vault.list_altars():
        sample_path = BASE_DIR / "samples" / "sample_altar.json"
        if sample_path.exists():
            with open(sample_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                altar = Altar.from_dict(data)
                vault.save_altar(altar)

class OfrendaRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: Any, status: int = 200):
        response_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response_bytes)

    def _read_body_json(self) -> Dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            raw_body = self.rfile.read(content_length).decode("utf-8")
            return json.loads(raw_body)
        return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # REST API Routes
        if path == "/api/status":
            ollama_ok = engine.is_ollama_available()
            altars = vault.list_altars()
            self._send_json({
                "status": "online",
                "ai_engine": f"Google Gemma 2 ({engine.model_name})" if ollama_ok else "Deterministic Cultural Heuristics",
                "ollama_connected": ollama_ok,
                "altars_count": len(altars),
                "data_sovereignty": "100% On-Device Air-Gapped"
            })
            return

        if path == "/api/altars":
            altars = vault.list_altars()
            self._send_json([a.to_dict() for a in altars])
            return

        if path.startswith("/api/altars/"):
            parts = path.strip("/").split("/")
            if len(parts) == 3:  # /api/altars/<id>
                altar_id = parts[2]
                altar = vault.get_altar(altar_id)
                if altar:
                    self._send_json(altar.to_dict())
                else:
                    self._send_json({"error": "Altar not found"}, 404)
                return

        if path.startswith("/api/export/"):
            altar_id = path.split("/")[-1]
            altar = vault.get_altar(altar_id)
            if altar:
                # Generate sample calaverita & remembrance if available
                calaverita = ""
                remembrance = ""
                if altar.ancestors:
                    calaverita = engine.generate_calaverita(altar.ancestors[0])["calaverita"]
                    remembrance = engine.generate_remembrance(altar.ancestors[0])["remembrance"]
                export_path = vault.export_standalone_memorial_html(altar, calaverita, remembrance)
                with open(export_path, "r", encoding="utf-8") as f:
                    content = f.read()
                content_bytes = content.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Disposition", f'attachment; filename="memorial_{altar.id}.html"')
                self.send_header("Content-Length", str(len(content_bytes)))
                self.end_headers()
                self.wfile.write(content_bytes)
                return
            else:
                self._send_json({"error": "Altar not found"}, 404)
                return

        # Serve static files
        if path == "/" or path == "":
            file_path = STATIC_DIR / "index.html"
        else:
            file_path = STATIC_DIR / path.lstrip("/")

        if file_path.exists() and file_path.is_file():
            mime_type, _ = mimetypes.guess_type(str(file_path))
            mime_type = mime_type or "application/octet-stream"
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            body = self._read_body_json()
        except Exception as e:
            self._send_json({"error": f"Invalid JSON payload: {str(e)}"}, 400)
            return

        if path == "/api/altars":
            altar = Altar.from_dict(body)
            vault.save_altar(altar)
            self._send_json(altar.to_dict(), 201)
            return

        if path.startswith("/api/altars/") and path.endswith("/offerings"):
            altar_id = path.split("/")[3]
            altar = vault.get_altar(altar_id)
            if not altar:
                self._send_json({"error": "Altar not found"}, 404)
                return
            offering = Offering.from_dict(body)
            altar.add_offering(offering)
            vault.save_altar(altar)
            self._send_json(altar.to_dict(), 201)
            return

        if path.startswith("/api/altars/") and path.endswith("/ancestors"):
            altar_id = path.split("/")[3]
            altar = vault.get_altar(altar_id)
            if not altar:
                self._send_json({"error": "Altar not found"}, 404)
                return
            ancestor = Ancestor.from_dict(body)
            altar.add_ancestor(ancestor)
            # Automatically recommend and add authentic offerings for the new ancestor
            recs = engine.recommend_offerings(ancestor)
            for r in recs:
                if not any(o.name == r.name for o in altar.offerings):
                    altar.add_offering(r)
            vault.save_altar(altar)
            self._send_json(altar.to_dict(), 201)
            return

        if path == "/api/generate-calaverita":
            ancestor_data = body.get("ancestor", {})
            ancestor = Ancestor.from_dict(ancestor_data)
            lang = body.get("language", "bilingual")
            result = engine.generate_calaverita(ancestor, lang)
            self._send_json(result)
            return

        if path == "/api/generate-remembrance":
            ancestor_data = body.get("ancestor", {})
            ancestor = Ancestor.from_dict(ancestor_data)
            result = engine.generate_remembrance(ancestor)
            self._send_json(result)
            return

        if path == "/api/ask-ancestor":
            ancestor_data = body.get("ancestor", {})
            ancestor = Ancestor.from_dict(ancestor_data)
            question = body.get("question", "")
            if not question:
                self._send_json({"error": "Question is required"}, 400)
                return
            result = engine.ask_ancestor_wisdom(ancestor, question)
            self._send_json(result)
            return

        if path == "/api/recommend-offerings":
            ancestor_data = body.get("ancestor", {})
            ancestor = Ancestor.from_dict(ancestor_data)
            offerings = engine.recommend_offerings(ancestor)
            self._send_json([o.to_dict() for o in offerings])
            return

        self._send_json({"error": "Endpoint not found"}, 404)

def run_server(port: int = PORT):
    ensure_sample_seed()
    server_address = ("", port)
    httpd = HTTPServer(server_address, OfrendaRequestHandler)
    print(f"===========================================================")
    print(f"  🏵️ Ofrenda AI - Living Altar & Ancestral Memory Vault")
    print(f"  Powered by Google Gemma 2 Open-Weight AI (Air-Gapped)")
    print(f"===========================================================")
    print(f"  Dashboard active at: http://localhost:{port}")
    print(f"  Data Sovereignty:    100% On-Device Local Memory")
    print(f"  Press Ctrl+C to stop.")
    print(f"===========================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Ofrenda AI server peacefully.")
        httpd.server_close()

if __name__ == "__main__":
    p = PORT
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        p = int(sys.argv[1])
    run_server(p)
