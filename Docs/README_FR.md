<p align="center">
  <img src="banner-promptiq.jpg" alt="PromptIQ" width="750">
</p>

<h1 align="center">PromptIQ</h1>

<p align="center">
  <strong>Le toolkit intelligent pour l'ingénierie de prompts.<br>
  Versioning + évaluation 4 étapes + tests A/B + amélioration automatique — depuis votre terminal.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/promptiq/"><img src="https://img.shields.io/pypi/v/promptiq?color=blueviolet&style=for-the-badge"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/Licence-MIT-22c55e?style=for-the-badge"></a>
</p>

---

## 💀 Le Problème

Vous avez passé des heures à affiner un prompt. Il fonctionnait parfaitement.
Vous avez fait une petite modification.
Tout s'est cassé.

Pas d'historique. Pas de retour en arrière. Pas de diff. **La version qui marchait a disparu pour toujours.**

---

## ✦ Qu'est-ce que PromptIQ ?

PromptIQ est un système de contrôle de version pour les prompts LLM — avec une vraie intelligence embarquée.

Une seule commande fait tout ça :

```bash
promptiq commit chatbot system.txt -m "amélioration du ton" --judge --test-cases inputs.json
```

1. ✅ Sauvegarde la version avec semver (`v1.2.0`) et un hash
2. ✅ Évalue le texte du prompt sur 5 dimensions
3. ✅ Exécute le prompt sur des entrées réelles et évalue les vraies sorties
4. ✅ Compare à la version précédente et déclare un gagnant
5. ✅ Génère une version améliorée ciblant vos faiblesses spécifiques
6. ✅ Tout stocké localement en JSON — pas de cloud, pas de compte

---

## ⚡ Installation

```bash
# Avec Claude (recommandé)
pip install "promptiq[anthropic]"
export ANTHROPIC_API_KEY=sk-ant-...

# Avec OpenAI
pip install "promptiq[openai]"
export OPENAI_API_KEY=sk-...
```

---

## 🚀 Démarrage rapide

```bash
# Committer une version
promptiq commit chatbot system.txt -m "première ébauche"

# Committer + évaluation complète
promptiq commit chatbot system.txt -m "amélioré" --judge --test-cases inputs.json

# Voir l'historique avec les scores
promptiq log chatbot

# Diff mot par mot entre deux versions
promptiq diff chatbot 1.0.0 1.1.0

# Test A/B de deux versions
promptiq ab chatbot 1.0.0 1.1.0 --test-cases inputs.json

# Version améliorée par IA
promptiq improve chatbot

# Exporter le changelog en Markdown
promptiq export chatbot
```

---

## 🧠 Le Judge en 4 Étapes

```
Étape 1 ── Analyse statique      évaluer le texte du prompt lui-même
Étape 2 ── Évaluation des sorties exécuter sur LLM, juger les vraies sorties
Étape 3 ── Comparaison           tête-à-tête avec la version précédente
Étape 4 ── Auto-amélioration     réécriture ciblant vos faiblesses
```

### Dimensions d'évaluation

| Dimension | Ce qu'elle mesure |
|---|---|
| Clarté | Non ambigu ? Deux ingénieurs l'interpréteraient-ils identiquement ? |
| Spécificité | Instructions concrètes et actionnables ? |
| Concision | Sans redondance ni remplissage ? |
| Qualité des instructions | Guide efficacement le comportement du modèle ? |
| Robustesse | Gère les cas limites et les modes d'échec ? |

---

## 🔬 Test A/B

```bash
promptiq ab chatbot 1.0.0 1.2.0 --test-cases inputs.json
```

Chaque cas de test reçoit un juge indépendant. Un gagnant est déclaré par cas et globalement.

---

## 📖 Toutes les commandes

```bash
promptiq commit <nom> <fichier> -m "message" [--judge] [--test-cases f.json]
promptiq log <nom>
promptiq diff <nom> <ref_a> <ref_b>
promptiq judge <fichier> [--test-cases f.json]
promptiq improve <nom>
promptiq ab <nom> <ref_a> <ref_b> --test-cases f.json
promptiq status <nom>
promptiq checkout <nom> <ref>
promptiq ls
promptiq export <nom> [--format markdown|json|scores]
promptiq branch create|switch|ls <nom>
```

---

## 🗄️ Stockage

```
~/.promptiq/
└── prompts/
    ├── chatbot.json
    └── summarizer.json
```

JSON simple. Lisible par n'importe quel éditeur. Pas de base de données. Pas de vendor lock-in.

---

## 📄 Licence

MIT — utilisez-le, forkez-le, construisez dessus, publiez-le.

---

<p align="center">
  <em>L'ingénierie de prompts ne devrait pas être une affaire de devinettes.<br>
  Chaque changement doit être mesurable. Chaque version doit être améliorable.<br>
  C'est pour ça que PromptIQ existe.</em>
</p>
