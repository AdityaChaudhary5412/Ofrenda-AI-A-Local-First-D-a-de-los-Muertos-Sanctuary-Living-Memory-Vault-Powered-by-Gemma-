#!/usr/bin/env python3
"""
Ofrenda AI - Command Line Interface (CLI)
Interact with your living altar, generate calaveritas, and consult ancestors from your terminal.
"""

import sys
import argparse
import json
from models import Altar, Ancestor, Offering
from engine import OfrendaAIEngine
from vault import Vault

def print_banner():
    banner = """
================================================================================
  🏵️  OFRENDA AI - LIVING SANCTUARY & ANCESTRAL MEMORY VAULT 🕯️
  Theme: Ghost in the Machine | Powered by Google Gemma 2 (Local / Air-Gapped)
================================================================================
    """
    print(banner)

def render_ascii_altar(altar: Altar):
    by_tier = altar.get_offerings_by_tier()
    print("\n" + "="*70)
    print(f"  🏛️  {altar.title.upper()}  🏛️")
    if altar.dedication_text:
        print(f"  « {altar.dedication_text} »")
    print("="*70)

    print("\n                     [ 🕊️  TIER 1: CIELO - ESPÍRITU Y LUZ  🕊️ ]")
    print("                   ---------------------------------------------")
    ancestor_names = " | ".join([f"🖼️  {a.name} ({a.relationship})" for a in altar.ancestors])
    print(f"                   {ancestor_names or 'Ningún ancestro registrado aún'}")
    cielo_items = "  ".join([f"{o.icon} {o.name}" for o in by_tier.get('cielo', [])])
    print(f"                   {cielo_items}")

    print("\n             [ 🍞  TIER 2: TIERRA - MEMORIA, COMIDA Y MÚSICA  🍞 ]")
    print("           ---------------------------------------------------------")
    tierra_items = "  ".join([f"{o.icon} {o.name}" for o in by_tier.get('tierra', [])])
    print(f"           {tierra_items}")

    print("\n       [ 🌼  TIER 3: INFRAMUNDO - AGUA, SAL Y CAMINO DE CEMPASÚCHIL  🌼 ]")
    print("     ---------------------------------------------------------------------")
    infra_items = "  ".join([f"{o.icon} {o.name}" for o in by_tier.get('inframundo', [])])
    print(f"     {infra_items}")
    print("\n" + "="*70 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Ofrenda AI - Living Altar & Ancestral Memory Vault")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Command: show
    subparsers.add_parser("show", help="Display the active living altar in ASCII format")

    # Command: calaverita
    cal_parser = subparsers.add_parser("calaverita", help="Generate a Calaverita Literaria for an ancestor")
    cal_parser.add_argument("--ancestor", type=str, help="Ancestor name substring")
    cal_parser.add_argument("--lang", type=str, default="bilingual", choices=["spanish", "bilingual"], help="Language style")

    # Command: remembrance
    rem_parser = subparsers.add_parser("remembrance", help="Generate a touching Día de los Muertos eulogy")
    rem_parser.add_argument("--ancestor", type=str, help="Ancestor name substring")

    # Command: ask
    ask_parser = subparsers.add_parser("ask", help="Ask an ancestor for life guidance & advice")
    ask_parser.add_argument("question", type=str, help="Question to ask the ancestor")
    ask_parser.add_argument("--ancestor", type=str, help="Ancestor name substring")

    # Command: export
    subparsers.add_parser("export", help="Export a standalone air-gapped HTML memorial")

    args = parser.parse_args()

    vault = Vault()
    engine = OfrendaAIEngine()

    # Load or seed
    altars = vault.list_altars()
    if not altars:
        sample_path = "samples/sample_altar.json"
        with open(sample_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            altar = Altar.from_dict(data)
            vault.save_altar(altar)
            altars = [altar]

    altar = altars[0]

    def find_ancestor(query: str = None) -> Ancestor:
        if not altar.ancestors:
            print("❌ No hay ancestros registrados en el altar.")
            sys.exit(1)
        if not query:
            return altar.ancestors[0]
        for a in altar.ancestors:
            if query.lower() in a.name.lower() or query.lower() in a.relationship.lower():
                return a
        print(f"❌ Ancestro coincidente con '{query}' no encontrado. Usando: {altar.ancestors[0].name}")
        return altar.ancestors[0]

    if args.command == "show" or not args.command:
        print_banner()
        render_ascii_altar(altar)
        status_text = "🟢 Gemma 2 (Local Inference Active)" if engine.is_ollama_available() else "🟠 Deterministic Cultural Heuristics (Offline Air-Gapped)"
        print(f"[*] Engine Status: {status_text}")
        print(f"[*] Preserved Ancestors: {len(altar.ancestors)}")
        print(f"[*] Active Sacred Offerings: {len(altar.offerings)}")
        print(f"[*] To launch the web dashboard: python3 app.py\n")

    elif args.command == "calaverita":
        print_banner()
        anc = find_ancestor(args.ancestor)
        print(f"[*] Componiendo Calaverita Literaria para: {anc.name} ({anc.relationship})...\n")
        res = engine.generate_calaverita(anc, args.lang)
        print(res["calaverita"])
        print(f"\n[Generated by: {res['engine']} | Mode: {res['mode']}]")

    elif args.command == "remembrance":
        print_banner()
        anc = find_ancestor(args.ancestor)
        print(f"[*] Sintetizando Elogio y Memoria para: {anc.name} ({anc.relationship})...\n")
        res = engine.generate_remembrance(anc)
        print(res["remembrance"])
        print(f"\n[Generated by: {res['engine']} | Mode: {res['mode']}]")

    elif args.command == "ask":
        print_banner()
        anc = find_ancestor(args.ancestor)
        print(f"[*] Invocando presencia y sabiduría de: {anc.name} ({anc.relationship})...")
        print(f"[*] Pregunta: \"{args.question}\"\n")
        res = engine.ask_ancestor_wisdom(anc, args.question)
        print(res["answer"])
        print(f"\n[Channeled via: {res['engine']} | Mode: {res['mode']}]")

    elif args.command == "export":
        print_banner()
        cal = engine.generate_calaverita(altar.ancestors[0])["calaverita"] if altar.ancestors else ""
        rem = engine.generate_remembrance(altar.ancestors[0])["remembrance"] if altar.ancestors else ""
        export_path = vault.export_standalone_memorial_html(altar, cal, rem)
        print(f"✅ Memorial autónomo exportado exitosamente:")
        print(f"   {export_path.resolve()}")
        print(f"   (Puedes abrir este archivo HTML en cualquier navegador sin conexión a internet)")

if __name__ == "__main__":
    main()
