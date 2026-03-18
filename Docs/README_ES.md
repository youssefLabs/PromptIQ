<p align="center">
  <img src="../banner-promptiq.jpg" alt="PromptIQ" width="750">
</p>

<h1 align="center">PromptIQ</h1>

<p align="center">
  <strong>El toolkit inteligente para ingeniería de prompts.<br>
  Control de versiones + evaluación en 4 etapas + pruebas A/B + mejora automática — todo desde tu terminal.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/promptiq/"><img src="https://img.shields.io/pypi/v/promptiq?color=blueviolet&style=for-the-badge"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/Licencia-MIT-22c55e?style=for-the-badge"></a>
</p>

<p align="center">
  <a href="../README.md">🇬🇧 English</a> ·
  <a href="./README_AR.md">🇸🇦 العربية</a> ·
  <a href="./README_FR.md">🇫🇷 Français</a> ·
  <a href="./README_ZH.md">🇨🇳 中文</a> ·
  <a href="./README_ES.md">🇪🇸 Español</a> ·
  <a href="./README_DE.md">🇩🇪 Deutsch</a> ·
  <a href="./README_PT.md">🇧🇷 Português</a> ·
  <a href="./README_TR.md">🇹🇷 Türkçe</a> ·
  <a href="./README_RU.md">🇷🇺 Русский</a> ·
  <a href="./README_JA.md">🇯🇵 日本語</a> ·
  <a href="./README_KO.md">🇰🇷 한국어</a> ·
  <a href="./README_HI.md">🇮🇳 हिन्दी</a>
</p>

---

## 💀 El Problema

Pasaste horas ajustando un prompt. Funcionaba perfectamente.
Hiciste un pequeño cambio.
Todo se rompió.

Sin historial. Sin rollback. Sin diff. **La versión que funcionaba desapareció para siempre.**

---

## ✦ ¿Qué es PromptIQ?

PromptIQ es un sistema de control de versiones para prompts de LLM — con inteligencia real integrada.

Un solo comando hace todo esto:

```bash
promptiq commit chatbot system.txt -m "mejora de tono" --judge --test-cases inputs.json
```

1. ✅ Guarda la versión con semver (`v1.2.0`) y un hash
2. ✅ Evalúa el texto del prompt en 5 dimensiones
3. ✅ Ejecuta el prompt en inputs reales y evalúa los outputs del LLM
4. ✅ Compara con la versión anterior y declara un ganador
5. ✅ Genera una versión mejorada atacando tus debilidades específicas
6. ✅ Todo almacenado localmente en JSON — sin cloud, sin cuenta

---

## ⚡ Instalación

```bash
# Con Claude (recomendado)
pip install "promptiq[anthropic]"
export ANTHROPIC_API_KEY=sk-ant-...

# Con OpenAI
pip install "promptiq[openai]"
export OPENAI_API_KEY=sk-...
```

---

## 🚀 Inicio Rápido

```bash
promptiq commit chatbot system.txt -m "primer borrador"
promptiq commit chatbot system.txt -m "mejorado" --judge --test-cases inputs.json
promptiq log chatbot
promptiq diff chatbot 1.0.0 1.1.0
promptiq ab chatbot 1.0.0 1.1.0 --test-cases inputs.json
promptiq improve chatbot
promptiq export chatbot
```

---

## 🧠 El Judge en 4 Etapas

```
Etapa 1 ── Análisis estático     evaluar el texto del prompt
Etapa 2 ── Evaluación de outputs ejecutar en LLM real, juzgar los outputs
Etapa 3 ── Comparación           cara a cara con la versión anterior
Etapa 4 ── Mejora automática     reescritura enfocada en tus debilidades
```

| Dimensión | Qué mide |
|---|---|
| Claridad | ¿Sin ambigüedad? ¿Dos ingenieros lo interpretarían igual? |
| Especificidad | ¿Instrucciones concretas y accionables? |
| Concisión | ¿Sin redundancia ni relleno? |
| Calidad de instrucciones | ¿Guía efectivamente el comportamiento del modelo? |
| Robustez | ¿Maneja casos edge y modos de fallo? |

---

## 📖 Todos los Comandos

```bash
promptiq commit <nombre> <archivo> -m "mensaje" [--judge] [--test-cases f.json]
promptiq log <nombre>
promptiq diff <nombre> <ref_a> <ref_b>
promptiq judge <archivo> [--test-cases f.json]
promptiq improve <nombre>
promptiq ab <nombre> <ref_a> <ref_b> --test-cases f.json
promptiq status <nombre>
promptiq checkout <nombre> <ref>
promptiq ls
promptiq export <nombre> [--format markdown|json|scores]
promptiq branch create|switch|ls <nombre>
```

---

## 📄 Licencia

MIT — úsalo, fórkalo, construye sobre él, publícalo.

---

<p align="center">
  <em>La ingeniería de prompts no debería ser adivinanza.<br>
  Cada cambio debe ser medible. Cada versión, mejorable.<br>
  Para eso existe PromptIQ.</em>
</p>
