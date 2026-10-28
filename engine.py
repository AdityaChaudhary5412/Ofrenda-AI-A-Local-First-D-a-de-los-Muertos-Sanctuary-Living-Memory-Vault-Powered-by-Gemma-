"""
Ofrenda AI - Inference Engine
Powered by Google Gemma 2 Open-Weight Models with Deterministic Cultural Fallback
"""

import json
import logging
import random
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from models import Ancestor, Offering

logger = logging.getLogger("ofrenda.engine")

class OfrendaAIEngine:
    def __init__(self, ollama_host: str = "http://localhost:11434", model_name: str = "gemma2:2b"):
        self.ollama_host = ollama_host.rstrip("/")
        self.model_name = model_name
        self.timeout = 8.0

    def is_ollama_available(self) -> bool:
        """Check if local Ollama daemon is active and responsive."""
        try:
            req = urllib.request.Request(f"{self.ollama_host}/api/tags", headers={"User-Agent": "OfrendaAI"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode())
                    models = [m.get("name", "") for m in data.get("models", [])]
                    # Check if gemma is available
                    has_gemma = any("gemma" in m.lower() for m in models)
                    return True
        except Exception:
            pass
        return False

    def query_gemma(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """Query local Gemma open-weight model via Ollama HTTP API."""
        url = f"{self.ollama_host}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.4,
                "top_p": 0.9,
            }
        }
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json", "User-Agent": "OfrendaAI"}
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    result = json.loads(resp.read().decode())
                    return result.get("response", "").strip()
        except Exception as e:
            logger.debug(f"Local Gemma inference skipped/failed: {e}")
        return None

    def generate_calaverita(self, ancestor: Ancestor, language: str = "bilingual") -> Dict[str, Any]:
        """
        Generate a Calaverita Literaria: a traditional satirical, affectionate Día de los Muertos rhyme
        about La Muerte / La Catrina visiting and being charmed by the departed ancestor.
        """
        prompt = (
            f"Write a traditional, affectionate Calaverita Literaria for Día de los Muertos honoring {ancestor.name}.\n"
            f"Relationship: {ancestor.relationship}.\n"
            f"Bio/Personality: {ancestor.bio}.\n"
            f"Favorite foods: {', '.join(ancestor.favorite_foods)}.\n"
            f"Favorite songs: {', '.join(ancestor.favorite_songs)}.\n"
            f"Famous sayings: {', '.join(ancestor.sayings_and_advice)}.\n"
            f"Style: Poetic four-line stanzas with AABB or ABAB rhyme scheme where La Catrina or La Huesuda comes to visit, "
            f"is offered their favorite food or hears their famous saying, and smiles peacefully.\n"
            f"Output language: {language} (Spanish or bilingual Spanish/English)."
        )
        system = (
            "You are a revered Mexican poet crafting traditional Día de los Muertos Calaveritas Literarias. "
            "Write with warmth, reverence, poetic cadence, and a gentle touch of joyful celebration of life."
        )

        ai_response = self.query_gemma(prompt, system)
        if ai_response:
            return {
                "calaverita": ai_response,
                "engine": f"Google Gemma 2 ({self.model_name})",
                "mode": "open_weight_inference"
            }

        # Deterministic Cultural Fallback
        return {
            "calaverita": self._fallback_calaverita(ancestor),
            "engine": "Deterministic Cultural Heuristics Engine",
            "mode": "offline_fallback"
        }

    def generate_remembrance(self, ancestor: Ancestor) -> Dict[str, Any]:
        """Generate a touching, poetic Día de los Muertos remembrance and eulogy."""
        prompt = (
            f"Write a beautiful, moving Día de los Muertos remembrance for {ancestor.name} ({ancestor.relationship}).\n"
            f"Lived: {ancestor.birth_year or 'Unknown'} - {ancestor.passing_year or 'Present'}.\n"
            f"Life story & traits: {ancestor.bio}.\n"
            f"Favorite foods they loved: {', '.join(ancestor.favorite_foods)}.\n"
            f"Songs that moved them: {', '.join(ancestor.favorite_songs)}.\n"
            f"Their wisdom and sayings: {', '.join(ancestor.sayings_and_advice)}.\n"
            f"Include the symbolism of cempasúchil flowers guiding their path back to our ofrenda, "
            f"the glow of candles, and how their legacy lives on."
        )
        system = "You are a master biographer and memorial writer honoring ancestors on Día de los Muertos with dignity and lyrical tenderness."

        ai_response = self.query_gemma(prompt, system)
        if ai_response:
            return {
                "remembrance": ai_response,
                "engine": f"Google Gemma 2 ({self.model_name})",
                "mode": "open_weight_inference"
            }

        return {
            "remembrance": self._fallback_remembrance(ancestor),
            "engine": "Deterministic Cultural Heuristics Engine",
            "mode": "offline_fallback"
        }

    def ask_ancestor_wisdom(self, ancestor: Ancestor, question: str) -> Dict[str, Any]:
        """
        Channel the wisdom of the ancestor based strictly on their recorded life stories,
        sayings, and values.
        """
        prompt = (
            f"You are speaking in the warm, loving, and authentic voice of {ancestor.name} ({ancestor.relationship}).\n"
            f"Your personality & background: {ancestor.bio}.\n"
            f"Your personal mantras, advice, and sayings: {'; '.join(ancestor.sayings_and_advice)}.\n"
            f"Your fondest memories: {[m.story for m in ancestor.memories]}.\n\n"
            f"A beloved family member approaches your ofrenda and asks:\n\"{question}\"\n\n"
            f"Respond to them with deep affection, using your authentic sayings and philosophy of life. "
            f"Remind them that you are watching over them, and guide them with grace."
        )
        system = (
            "You embody the spirit of a cherished ancestor honoring Día de los Muertos. "
            "Speak directly, gently, and warmly. Ground your advice in the ancestor's stated sayings and memories."
        )

        ai_response = self.query_gemma(prompt, system)
        if ai_response:
            return {
                "answer": ai_response,
                "engine": f"Google Gemma 2 ({self.model_name})",
                "mode": "open_weight_inference"
            }

        return {
            "answer": self._fallback_ancestor_wisdom(ancestor, question),
            "engine": "Deterministic Cultural Heuristics Engine",
            "mode": "offline_fallback"
        }

    def recommend_offerings(self, ancestor: Ancestor) -> List[Offering]:
        """Recommend culturally authentic 3-tier ofrenda items personalized to the ancestor."""
        offerings = []

        # Tier 1: Cielo (Top) - Light, Guidance, Spirit
        offerings.append(Offering(
            name="Velas de Cera Bendita (Sacred Candles)",
            category="candle",
            tier="cielo",
            description=f"Candles to illuminate the spiritual path for {ancestor.name} to guide their way home.",
            icon="🕯️"
        ))
        offerings.append(Offering(
            name="Retrato Enmarcado (Framed Portrait)",
            category="personal",
            tier="cielo",
            description=f"Cherished photograph of {ancestor.name} placed in the highest place of honor.",
            icon="🖼️"
        ))
        offerings.append(Offering(
            name="Incienso de Copal (Copal Resin)",
            category="incense",
            tier="cielo",
            description="Fragrant copal smoke cleansing the air of negative spirits and welcoming ancestral peace.",
            icon="💨"
        ))

        # Tier 2: Tierra (Middle) - Comfort, Sustenance, Favorite Earthly Pleasures
        offerings.append(Offering(
            name="Pan de Muerto Tradicional",
            category="food",
            tier="tierra",
            description="Sweet bread topped with bone-shaped dough crossbones and sprinkled with sugar, representing the circle of life.",
            icon="🍞"
        ))

        # Add their favorite foods
        for food in ancestor.favorite_foods[:2]:
            offerings.append(Offering(
                name=f"Plato Favorito: {food}",
                category="food",
                tier="tierra",
                description=f"Freshly prepared {food}, just as {ancestor.name} loved it during their time with us.",
                icon="🍲"
            ))

        # Add favorite music/items
        if ancestor.favorite_songs:
            song = ancestor.favorite_songs[0]
            offerings.append(Offering(
                name=f"Melodía Eterna: \"{song}\"",
                category="personal",
                tier="tierra",
                description=f"The music that filled the home with joy whenever {ancestor.name} was listening.",
                icon="🎵"
            ))

        # Tier 3: Inframundo (Base) - Earth, Purification, Journey
        offerings.append(Offering(
            name="Camino de Pétalos de Cempasúchil",
            category="cempasuchil",
            tier="inframundo",
            description="Golden Aztec marigold petals whose vibrant color and sacred scent guide ancestral souls across the threshold.",
            icon="🌼"
        ))
        offerings.append(Offering(
            name="Vaso de Agua Pura (Fresh Water)",
            category="water",
            tier="inframundo",
            description="Quenches the long thirst of the soul after traveling across the spiritual realms.",
            icon="💧"
        ))
        offerings.append(Offering(
            name="Cruz de Sal Purificadora (Salt)",
            category="salt",
            tier="inframundo",
            description="Element of purification to protect the traveler's spirit along their journey back.",
            icon="🧂"
        ))

        return offerings

    def _fallback_calaverita(self, ancestor: Ancestor) -> str:
        food = ancestor.favorite_foods[0] if ancestor.favorite_foods else "un pan de muerto doradito"
        saying = ancestor.sayings_and_advice[0] if ancestor.sayings_and_advice else "con una sonrisa de oreja a oreja"

        stanzas = [
            f"Estaba la Catrina paseando en el panteón,\n"
            f"buscando a {ancestor.name} con gran devoción.\n"
            f"«Vengo por tu alma», le dijo al pasar,\n"
            f"pero una rica aroma la puso a dudar.",

            f"En la mesa había servido {food},\n"
            f"y la Calaca Flaca se quitó la actitud.\n"
            f"«Prueba este bocado», le dijo {ancestor.name} al son,\n"
            f"y a la calavera se le ablandó el corazón.",

            f"Recordaron juntos aquel gran refrán:\n"
            f"«{saying}», decían sin afán.\n"
            f"La Muerte riendo brindó con mezcal,\n"
            f"«¡Qué hermosa es tu vida, tu risa inmortal!»",

            f"Hoy flores de cempasúchil adornan el hogar,\n"
            f"{ancestor.name} vive siempre en nuestro altar.\n"
            f"Ni el tiempo ni el viento apagan la luz,\n"
            f"que brilla en el pecho con santa quietud."
        ]
        return "\n\n".join(stanzas)

    def _fallback_remembrance(self, ancestor: Ancestor) -> str:
        dates = f"{ancestor.birth_year or ''} - {ancestor.passing_year or ''}".strip(" -")
        dates_str = f" ({dates})" if dates else ""
        foods_str = f", especially over plates of {', '.join(ancestor.favorite_foods)}" if ancestor.favorite_foods else ""
        saying_str = f" We always remember the timeless words: \"{ancestor.sayings_and_advice[0]}\"." if ancestor.sayings_and_advice else ""

        return (
            f"In Loving Remembrance of {ancestor.name}{dates_str}\n\n"
            f"Tonight, as the golden cempasúchil petals form an unbroken golden path from the spirit world to our doorstep, "
            f"we welcome home the presence of {ancestor.name}.\n\n"
            f"{ancestor.bio if ancestor.bio else 'A life rich in purpose, kindness, and devotion to family.'}\n\n"
            f"We remember the warmth of your laughter and the moments we shared together{foods_str}.{saying_str}\n\n"
            f"Death does not take away what love has built; it only moves it into the sacred sanctuary of our hearts. "
            f"Every lit candle on this ofrenda whispers that you are never forgotten, never alone, and forever cherished."
        )

    def _fallback_ancestor_wisdom(self, ancestor: Ancestor, question: str) -> str:
        saying = random.choice(ancestor.sayings_and_advice) if ancestor.sayings_and_advice else "Keep your head up, lead with love, and do what is right."
        name = ancestor.name

        return (
            f"Mi querido corazón,\n\n"
            f"I hear you, and even across the quiet threshold, my love is right beside you. "
            f"Regarding your question about \"{question.strip()}\":\n\n"
            f"Always remember what I used to tell you: \"{saying}\". Life brings wind, rain, and storms, "
            f"but root yourself in love and honesty, and no storm can shake you.\n\n"
            f"Take a deep breath, share a warm meal, and know that whenever you feel unsure, "
            f"I am cheering for you from across the stars.\n\n"
            f"Con todo mi amor siempre,\n{name}"
        )
