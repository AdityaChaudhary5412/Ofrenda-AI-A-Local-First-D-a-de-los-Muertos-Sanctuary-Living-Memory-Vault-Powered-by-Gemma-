// Ofrenda AI - Client-Side Controller & Floating Petals Particle Physics

document.addEventListener("DOMContentLoaded", () => {
    let currentAltar = null;
    let candlesLit = true;

    // Initialize Floating Marigold (Cempasúchil) Petals on Canvas
    initPetalsCanvas();

    // Fetch initial system status & altars
    fetchStatus();
    loadAltars();

    // Tab Navigation
    const navTabs = document.querySelectorAll(".nav-tab");
    navTabs.forEach(tab => {
        tab.addEventListener("click", () => {
            navTabs.forEach(t => t.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
            
            tab.classList.add("active");
            const targetId = `tab-${tab.dataset.tab}`;
            const targetPane = document.getElementById(targetId);
            if (targetPane) targetPane.classList.add("active");
        });
    });

    // Toggle Candles
    const toggleCandlesBtn = document.getElementById("toggleCandlesBtn");
    toggleCandlesBtn.addEventListener("click", () => {
        candlesLit = !candlesLit;
        document.querySelectorAll(".candle-glow").forEach(glow => {
            glow.style.display = candlesLit ? "block" : "none";
        });
        toggleCandlesBtn.innerText = candlesLit ? "🕯️ Apagar Velas" : "✨ Encender Velas";
    });

    // Export HTML Memorial
    const exportHtmlBtn = document.getElementById("exportHtmlBtn");
    exportHtmlBtn.addEventListener("click", () => {
        if (!currentAltar) return;
        window.open(`/api/export/${currentAltar.id}`, "_blank");
    });

    // Oracle Consultation (Ask Ancestor)
    const askAncestorBtn = document.getElementById("askAncestorBtn");
    askAncestorBtn.addEventListener("click", async () => {
        const select = document.getElementById("oracleAncestorSelect");
        const questionInput = document.getElementById("oracleQuestionInput");
        const question = questionInput.value.trim();
        if (!question) {
            alert("Por favor escribe una pregunta o pide un consejo.");
            return;
        }

        const ancestor = currentAltar.ancestors.find(a => a.id === select.value);
        if (!ancestor) return;

        askAncestorBtn.disabled = true;
        askAncestorBtn.innerText = "🕊️ Invocando presencia...";

        try {
            const resp = await fetch("/api/ask-ancestor", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ancestor, question })
            });
            const data = await resp.json();

            document.getElementById("oracleSpeakerName").innerText = `${ancestor.name} (${ancestor.relationship})`;
            document.getElementById("oracleMessageText").innerText = data.answer || "El alma susurra con amor y paz.";
            document.getElementById("oracleEngineTag").innerText = `Engine: ${data.engine} (${data.mode})`;
            document.getElementById("oracleResponseArea").style.display = "flex";
        } catch (err) {
            alert("Error al conectar con la bóveda de recuerdos: " + err);
        } finally {
            askAncestorBtn.disabled = false;
            askAncestorBtn.innerText = "🕊️ Invocar Sabiduría del Ancestro";
        }
    });

    // Calaverita Generator
    const generateCalaveritaBtn = document.getElementById("generateCalaveritaBtn");
    generateCalaveritaBtn.addEventListener("click", async () => {
        const select = document.getElementById("calaveritaAncestorSelect");
        const lang = document.getElementById("calaveritaLangSelect").value;
        const ancestor = currentAltar.ancestors.find(a => a.id === select.value);
        if (!ancestor) return;

        generateCalaveritaBtn.disabled = true;
        generateCalaveritaBtn.innerText = "✨ Componiendo versos con Gemma...";

        try {
            const resp = await fetch("/api/generate-calaverita", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ancestor, language: lang })
            });
            const data = await resp.json();

            document.getElementById("calaveritaTitle").innerText = `Calaverita para ${ancestor.name}`;
            document.getElementById("calaveritaVerses").innerText = data.calaverita || "";
            document.getElementById("calaveritaMeta").innerText = `Generado por: ${data.engine} (${data.mode})`;
            document.getElementById("calaveritaDisplayArea").style.display = "block";
        } catch (err) {
            alert("Error al componer calaverita: " + err);
        } finally {
            generateCalaveritaBtn.disabled = false;
            generateCalaveritaBtn.innerText = "✨ Componer Calaverita con Gemma 2";
        }
    });

    // Remembrance Generator
    const generateRemembranceBtn = document.getElementById("generateRemembranceBtn");
    generateRemembranceBtn.addEventListener("click", async () => {
        const select = document.getElementById("remembranceAncestorSelect");
        const ancestor = currentAltar.ancestors.find(a => a.id === select.value);
        if (!ancestor) return;

        generateRemembranceBtn.disabled = true;
        generateRemembranceBtn.innerText = "🏵️ Sintetizando memoria...";

        try {
            const resp = await fetch("/api/generate-remembrance", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ancestor })
            });
            const data = await resp.json();

            document.getElementById("remembranceText").innerText = data.remembrance || "";
            document.getElementById("remembranceMeta").innerText = `Soberanía local: ${data.engine} (${data.mode})`;
            document.getElementById("remembranceDisplayArea").style.display = "block";
        } catch (err) {
            alert("Error al sintetizar elogio: " + err);
        } finally {
            generateRemembranceBtn.disabled = false;
            generateRemembranceBtn.innerText = "🏵️ Escribir Elogio Conmemorativo";
        }
    });

    // Add Ancestor Form
    const addAncestorForm = document.getElementById("addAncestorForm");
    addAncestorForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!currentAltar) return;

        const newAncestor = {
            name: document.getElementById("ancestorName").value.trim(),
            relationship: document.getElementById("ancestorRelationship").value.trim(),
            birth_year: parseInt(document.getElementById("ancestorBirthYear").value) || null,
            passing_year: parseInt(document.getElementById("ancestorPassingYear").value) || null,
            bio: document.getElementById("ancestorBio").value.trim(),
            favorite_foods: document.getElementById("ancestorFoods").value.split(",").map(s => s.trim()).filter(Boolean),
            sayings_and_advice: document.getElementById("ancestorSayings").value.split(";").map(s => s.trim()).filter(Boolean),
            favorite_songs: document.getElementById("ancestorSongs").value.split(",").map(s => s.trim()).filter(Boolean)
        };

        try {
            const resp = await fetch(`/api/altars/${currentAltar.id}/ancestors`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(newAncestor)
            });
            const updatedAltar = await resp.json();
            currentAltar = updatedAltar;
            renderAltar(currentAltar);
            populateAncestorSelects(currentAltar.ancestors);
            addAncestorForm.reset();
            alert(`¡${newAncestor.name} ha sido honrado(a) en el altar con sus ofrendas correspondientes!`);
            
            // Switch to altar view
            document.querySelector('.nav-tab[data-tab="altar"]').click();
        } catch (err) {
            alert("Error al guardar ancestro: " + err);
        }
    });

    // Helper: Fetch status
    async function fetchStatus() {
        try {
            const resp = await fetch("/api/status");
            const data = await resp.json();
            const badge = document.getElementById("aiStatusBadge");
            if (data.ollama_connected) {
                badge.innerText = `🟢 ${data.ai_engine} (Activo)`;
                badge.style.color = "#81c784";
                badge.style.borderColor = "rgba(129, 199, 132, 0.4)";
            } else {
                badge.innerText = `🟠 Heurísticas Culturales Fuera de Línea (Gemma Ready)`;
                badge.style.color = "#ffb74d";
                badge.style.borderColor = "rgba(255, 183, 77, 0.4)";
            }
        } catch (e) {
            console.error("Status check failed", e);
        }
    }

    // Helper: Load Altars
    async function loadAltars() {
        try {
            const resp = await fetch("/api/altars");
            const altars = await resp.json();
            if (altars.length > 0) {
                currentAltar = altars[0];
                renderAltar(currentAltar);
                populateAncestorSelects(currentAltar.ancestors);
            }
        } catch (e) {
            console.error("Failed to load altars", e);
        }
    }

    // Helper: Render Altar Visuals
    function renderAltar(altar) {
        document.getElementById("altarTitle").innerText = altar.title;
        document.getElementById("altarDedication").innerText = altar.dedication_text || "Honrando la memoria eterna de quienes amamos.";

        // Cielo Ancestor Portraits
        const cieloAncestors = document.getElementById("cieloAncestors");
        cieloAncestors.innerHTML = "";
        altar.ancestors.forEach(a => {
            const dates = (a.birth_year || a.passing_year) ? `(${a.birth_year || ''} - ${a.passing_year || ''})` : '';
            const card = document.createElement("div");
            card.className = "ancestor-portrait-badge";
            card.innerHTML = `
                <div class="portrait-frame">
                    <span>🖼️</span>
                    <span class="candle-glow">🕯️</span>
                </div>
                <h4>${a.name}</h4>
                <span>${a.relationship} ${dates}</span>
            `;
            cieloAncestors.appendChild(card);
        });

        // Group Offerings by tier
        const cieloItems = document.getElementById("cieloItems");
        const tierraItems = document.getElementById("tierraItems");
        const inframundoItems = document.getElementById("inframundoItems");
        cieloItems.innerHTML = "";
        tierraItems.innerHTML = "";
        inframundoItems.innerHTML = "";

        altar.offerings.forEach(off => {
            const chip = document.createElement("div");
            chip.className = "offering-chip";
            chip.title = off.description;
            chip.innerHTML = `<span>${off.icon}</span> <strong>${off.name}</strong>`;

            if (off.tier === "cielo") {
                cieloItems.appendChild(chip);
            } else if (off.tier === "tierra") {
                tierraItems.appendChild(chip);
            } else {
                inframundoItems.appendChild(chip);
            }
        });
    }

    // Helper: Populate selects
    function populateAncestorSelects(ancestors) {
        const selects = [
            document.getElementById("oracleAncestorSelect"),
            document.getElementById("calaveritaAncestorSelect"),
            document.getElementById("remembranceAncestorSelect")
        ];

        selects.forEach(sel => {
            if (!sel) return;
            sel.innerHTML = "";
            ancestors.forEach(a => {
                const opt = document.createElement("option");
                opt.value = a.id;
                opt.innerText = `${a.name} (${a.relationship})`;
                sel.appendChild(opt);
            });
        });
    }

    // Floating Petals Canvas Particle Physics
    function initPetalsCanvas() {
        const canvas = document.getElementById("petalsCanvas");
        const ctx = canvas.getContext("2d");

        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight;

        window.addEventListener("resize", () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        });

        const petalColors = [
            "rgba(255, 167, 38, 0.7)",  // Vibrant Marigold
            "rgba(245, 183, 38, 0.65)", // Warm Gold
            "rgba(255, 119, 0, 0.6)",   // Deep Aztec Orange
            "rgba(233, 123, 119, 0.55)" // Mexican Pink Petal
        ];

        const petals = [];
        const PETAL_COUNT = 38;

        for (let i = 0; i < PETAL_COUNT; i++) {
            petals.push({
                x: Math.random() * width,
                y: Math.random() * height,
                size: Math.random() * 8 + 6,
                speedY: Math.random() * 0.9 + 0.4,
                speedX: Math.random() * 0.6 - 0.3,
                angle: Math.random() * Math.PI * 2,
                spin: (Math.random() - 0.5) * 0.03,
                color: petalColors[Math.floor(Math.random() * petalColors.length)]
            });
        }

        function drawPetal(p) {
            ctx.save();
            ctx.translate(p.x, p.y);
            ctx.rotate(p.angle);
            ctx.fillStyle = p.color;
            ctx.beginPath();
            ctx.ellipse(0, 0, p.size, p.size * 0.55, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }

        function animate() {
            ctx.clearRect(0, 0, width, height);

            petals.forEach(p => {
                p.y += p.speedY;
                p.x += Math.sin(p.y * 0.01) * 0.5 + p.speedX;
                p.angle += p.spin;

                if (p.y > height + 20) {
                    p.y = -20;
                    p.x = Math.random() * width;
                }
                if (p.x > width + 20) p.x = -20;
                if (p.x < -20) p.x = width + 20;

                drawPetal(p);
            });

            requestAnimationFrame(animate);
        }

        animate();
    }
});
