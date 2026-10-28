"""
Unit Tests for Ofrenda AI
Covers data models, inference engine, vault persistence, and HTML export.
"""

import unittest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import Altar, Ancestor, Offering, Memory
from engine import OfrendaAIEngine
from vault import Vault

class TestOfrendaModels(unittest.TestCase):
    def test_offering_creation_and_dict(self):
        off = Offering(name="Pan de Muerto", category="food", tier="tierra", description="Traditional sweet bread", icon="🍞")
        d = off.to_dict()
        self.assertEqual(d["name"], "Pan de Muerto")
        self.assertEqual(d["tier"], "tierra")
        
        recreated = Offering.from_dict(d)
        self.assertEqual(recreated.name, "Pan de Muerto")
        self.assertEqual(recreated.icon, "🍞")

    def test_ancestor_and_memories(self):
        anc = Ancestor(
            name="Elena Morales",
            relationship="Abuela",
            birth_year=1938,
            passing_year=2021,
            bio="Loving matriarch and chef.",
            favorite_foods=["Mole", "Tamales"],
            sayings_and_advice=["Where one eats, two eat."]
        )
        mem = Memory(title="Tamale Morning", story="Making tamales at dawn.")
        anc.memories.append(mem)

        d = anc.to_dict()
        self.assertEqual(len(d["memories"]), 1)
        self.assertEqual(d["memories"][0]["title"], "Tamale Morning")

        recreated = Ancestor.from_dict(d)
        self.assertEqual(recreated.name, "Elena Morales")
        self.assertEqual(len(recreated.memories), 1)
        self.assertIsInstance(recreated.memories[0], Memory)

    def test_altar_tiers(self):
        altar = Altar(title="Altar Test")
        altar.add_offering(Offering(name="Vela", tier="cielo"))
        altar.add_offering(Offering(name="Pan", tier="tierra"))
        altar.add_offering(Offering(name="Agua", tier="inframundo"))

        by_tier = altar.get_offerings_by_tier()
        self.assertEqual(len(by_tier["cielo"]), 1)
        self.assertEqual(len(by_tier["tierra"]), 1)
        self.assertEqual(len(by_tier["inframundo"]), 1)


class TestOfrendaEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OfrendaAIEngine(ollama_host="http://localhost:99999") # Non-existent port to test fallback reliability
        self.ancestor = Ancestor(
            name="Elena Morales",
            relationship="Abuela",
            birth_year=1938,
            passing_year=2021,
            bio="Grandmother who loved cooking and gardening.",
            favorite_foods=["Mole Poblano", "Pan de muerto"],
            sayings_and_advice=["Donde come uno, comen dos."]
        )

    def test_recommend_offerings(self):
        offerings = self.engine.recommend_offerings(self.ancestor)
        self.assertTrue(len(offerings) >= 5)
        tiers = {o.tier for o in offerings}
        self.assertIn("cielo", tiers)
        self.assertIn("tierra", tiers)
        self.assertIn("inframundo", tiers)
        # Check that favorite food is included
        food_names = [o.name for o in offerings]
        self.assertTrue(any("Mole Poblano" in n for n in food_names))

    def test_generate_calaverita_fallback(self):
        res = self.engine.generate_calaverita(self.ancestor)
        self.assertIn("calaverita", res)
        self.assertIn("Elena Morales", res["calaverita"])
        self.assertIn("Catrina", res["calaverita"])
        self.assertEqual(res["mode"], "offline_fallback")

    def test_generate_remembrance_fallback(self):
        res = self.engine.generate_remembrance(self.ancestor)
        self.assertIn("remembrance", res)
        self.assertIn("Elena Morales", res["remembrance"])
        self.assertIn("cempasúchil", res["remembrance"].lower())
        self.assertEqual(res["mode"], "offline_fallback")

    def test_ask_ancestor_wisdom_fallback(self):
        res = self.engine.ask_ancestor_wisdom(self.ancestor, "How do I deal with doubt?")
        self.assertIn("answer", res)
        self.assertIn("Donde come uno, comen dos", res["answer"])
        self.assertEqual(res["mode"], "offline_fallback")


class TestOfrendaVault(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.vault = Vault(storage_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_save_and_retrieve_altar(self):
        altar = Altar(id="altar_test_01", title="Familia Test")
        altar.add_ancestor(Ancestor(name="Arturo Pérez"))
        saved_path = self.vault.save_altar(altar)
        self.assertTrue(saved_path.exists())

        retrieved = self.vault.get_altar("altar_test_01")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.title, "Familia Test")
        self.assertEqual(len(retrieved.ancestors), 1)

    def test_list_and_delete_altar(self):
        altar1 = Altar(id="altar_1", title="Altar One")
        altar2 = Altar(id="altar_2", title="Altar Two")
        self.vault.save_altar(altar1)
        self.vault.save_altar(altar2)

        altars = self.vault.list_altars()
        self.assertEqual(len(altars), 2)

        deleted = self.vault.delete_altar("altar_1")
        self.assertTrue(deleted)
        self.assertEqual(len(self.vault.list_altars()), 1)

    def test_export_standalone_html(self):
        altar = Altar(id="altar_html_test", title="Ofrenda Sagrada")
        altar.add_ancestor(Ancestor(name="Abuela Elena", relationship="Abuela"))
        altar.add_offering(Offering(name="Pan de Muerto", tier="tierra"))

        export_file = self.vault.export_standalone_memorial_html(altar, "Versos de calaverita", "Hermoso elogio")
        self.assertTrue(export_file.exists())

        with open(export_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Ofrenda Sagrada", content)
        self.assertIn("Abuela Elena", content)
        self.assertIn("Versos de calaverita", content)
        self.assertIn("Hermoso elogio", content)

if __name__ == "__main__":
    unittest.main()
