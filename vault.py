"""
Ofrenda AI - Local Sanctuary Vault
Air-gapped local storage, audit tracking, and standalone offline export engine.
"""

import os
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from models import Altar, Ancestor, Offering, Memory

BASE_PROJECT_DIR = Path(__file__).resolve().parent
VAULT_DIR = BASE_PROJECT_DIR / ".ofrenda_vault"

class Vault:
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or VAULT_DIR
        self.altars_dir = self.storage_dir / "altars"
        self.exports_dir = self.storage_dir / "exports"
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        self.altars_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    def save_altar(self, altar: Altar) -> Path:
        """Persist an altar to local JSON storage."""
        file_path = self.altars_dir / f"{altar.id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(altar.to_dict(), f, indent=2, ensure_ascii=False)
        return file_path

    def get_altar(self, altar_id: str) -> Optional[Altar]:
        """Retrieve an altar by its unique ID."""
        file_path = self.altars_dir / f"{altar_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return Altar.from_dict(data)

    def list_altars(self) -> List[Altar]:
        """List all preserved altars in the local vault."""
        altars = []
        for file in self.altars_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    altars.append(Altar.from_dict(data))
            except Exception:
                continue
        return sorted(altars, key=lambda a: a.created_at, reverse=True)

    def delete_altar(self, altar_id: str) -> bool:
        """Delete an altar from local storage."""
        file_path = self.altars_dir / f"{altar_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def export_standalone_memorial_html(self, altar: Altar, calaverita: str = "", remembrance: str = "") -> Path:
        """
        Generate a fully self-contained, air-gapped HTML file that can be kept on a USB drive,
        emailed to family members, or archived forever without any internet connection.
        """
        export_file = self.exports_dir / f"memorial_{altar.id}.html"

        ancestors_html = ""
        for a in altar.ancestors:
            dates = f"({a.birth_year or ''} — {a.passing_year or ''})".replace("—", "").strip(" ()")
            ancestors_html += f"""
            <div class="ancestor-card">
                <div class="photo-frame">
                    <span class="icon">🕯️</span>
                    <div class="candle-flame"></div>
                </div>
                <h3>{a.name}</h3>
                <p class="relationship">{a.relationship} {f'• {dates}' if dates else ''}</p>
                <p class="bio">{a.bio}</p>
                <div class="favorites">
                    <strong>Favorite Foods:</strong> {', '.join(a.favorite_foods) or 'Pan de Muerto, Mole'}<br>
                    <strong>Sayings:</strong> <em>"{a.sayings_and_advice[0] if a.sayings_and_advice else 'Live with honor and love.'}"</em>
                </div>
            </div>
            """

        offerings_html = ""
        by_tier = altar.get_offerings_by_tier()
        for tier_name, tier_label in [("cielo", "Top Tier: Cielo (Spirit & Light)"),
                                       ("tierra", "Middle Tier: Tierra (Memory & Sustenance)"),
                                       ("inframundo", "Base Tier: Inframundo (Purification & Aztec Marigolds)")]:
            items = by_tier.get(tier_name, [])
            items_html = "".join([f"<li class='offering-item'><span class='icon'>{o.icon}</span> <strong>{o.name}</strong>: {o.description}</li>" for o in items])
            offerings_html += f"""
            <div class="tier-section">
                <h4>{tier_label}</h4>
                <ul class="offerings-list">{items_html or '<li>Candles and marigold petals resting peacefully.</li>'}</ul>
            </div>
            """

        calaverita_section = f"""
        <div class="poetry-box">
            <h3>🏵️ Calaverita Literaria</h3>
            <pre>{calaverita}</pre>
        </div>
        """ if calaverita else ""

        remembrance_section = f"""
        <div class="remembrance-box">
            <h3>🕯️ Living Remembrance</h3>
            <p>{remembrance.replace(chr(10), '<br>')}</p>
        </div>
        """ if remembrance else ""

        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{altar.title} — Ofrenda AI Living Sanctuary</title>
    <style>
        :root {{
            --bg: #0f0d13;
            --card-bg: rgba(28, 22, 38, 0.85);
            --gold: #f5b726;
            --orange: #ff7700;
            --pink: #e97b77;
            --marigold: #ffa726;
            --text: #f0edf5;
            --muted: #a49cb5;
        }}
        body {{
            margin: 0;
            padding: 0;
            background: radial-gradient(circle at 50% 20%, #20172c 0%, var(--bg) 100%);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
        }}
        .header {{
            text-align: center;
            padding: 50px 20px 30px;
            border-bottom: 1px solid rgba(245, 183, 38, 0.2);
        }}
        .marigold-banner {{
            font-size: 28px;
            letter-spacing: 4px;
            margin-bottom: 10px;
        }}
        h1 {{
            color: var(--gold);
            margin: 0 0 10px;
            font-size: 2.2rem;
            text-shadow: 0 0 15px rgba(245, 183, 38, 0.4);
        }}
        .dedication {{
            color: var(--pink);
            font-style: italic;
            font-size: 1.1rem;
        }}
        .container {{
            max-width: 900px;
            margin: 40px auto;
            padding: 0 20px;
        }}
        .altar-display {{
            background: var(--card-bg);
            border: 1px solid rgba(245, 183, 38, 0.3);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }}
        .ancestors-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .ancestor-card {{
            background: rgba(15, 13, 19, 0.7);
            border: 1px solid rgba(233, 123, 119, 0.3);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        .photo-frame {{
            width: 70px;
            height: 70px;
            margin: 0 auto 15px;
            border-radius: 50%;
            background: #2a1f3d;
            border: 2px solid var(--gold);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 30px;
            box-shadow: 0 0 15px rgba(245, 183, 38, 0.5);
        }}
        .tier-section {{
            margin-top: 25px;
            padding-top: 20px;
            border-top: 1px dashed rgba(245, 183, 38, 0.2);
        }}
        .tier-section h4 {{
            color: var(--marigold);
            margin: 0 0 12px;
        }}
        .offerings-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .offering-item {{
            padding: 8px 12px;
            margin-bottom: 6px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 6px;
            font-size: 0.95rem;
        }}
        .poetry-box, .remembrance-box {{
            background: rgba(245, 183, 38, 0.05);
            border-left: 4px solid var(--gold);
            border-radius: 8px;
            padding: 20px;
            margin-top: 30px;
        }}
        pre {{
            white-space: pre-wrap;
            font-family: Georgia, serif;
            font-size: 1.05rem;
            color: #ffe6a7;
        }}
        .footer {{
            text-align: center;
            padding: 30px;
            color: var(--muted);
            font-size: 0.85rem;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="marigold-banner">🏵️ 🕯️ 💀 🕯️ 🏵️</div>
        <h1>{altar.title}</h1>
        <div class="dedication">{altar.dedication_text or "Honrando la memoria eterna de quienes amamos y nunca olvidamos."}</div>
    </div>
    <div class="container">
        <div class="altar-display">
            <h2 style="color: var(--gold); text-align: center; margin-top: 0;">Nuestros Ancestros y Seres Queridos</h2>
            <div class="ancestors-grid">
                {ancestors_html}
            </div>
            <h2 style="color: var(--gold); text-align: center;">Ofrendas y Elementos Sagrados del Altar</h2>
            {offerings_html}
            {calaverita_section}
            {remembrance_section}
        </div>
    </div>
    <div class="footer">
        Preserved locally with Ofrenda AI • 100% On-Device Data Sovereignty • Powered by Google Gemma 2
    </div>
</body>
</html>
"""
        with open(export_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        return export_file
