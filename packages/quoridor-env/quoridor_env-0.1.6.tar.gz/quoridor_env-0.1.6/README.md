[![Claude Code Review](https://github.com/chrisjcc/quoridor/actions/workflows/claude-code-review.yml/badge.svg)](https://github.com/chrisjcc/quoridor/actions/workflows/claude-code-review.yml)

# 🧠 Quoridor-RL: A Multi-Agent RL Environment for the Quoridor Board Game

**Quoridor-RL** is a Python-based simulation environment for the Quoridor board game, compatible with the Gymnasium API and multi-agent RL training using Ray RLlib. It also includes a 3D interactive web viewer built with Three.js, and supports human interaction, imitation learning, and deployment on Hugging Face Spaces.

---

## ✨ Features

- ✅ Fully rule-compliant 2- and 4-player Quoridor engine
- ♻️ Multi-agent training support (Ray RLlib)
- 🎮 Human-agent interaction mode
- 📈 Episode logging for imitation learning
- 🧠 Gymnasium-compatible environment
- 🌐 3D visualization in the browser (Three.js)
- 🚀 Hugging Face Space ready

---

## 📦 Installation

### Python Game Engine

```bash
pip install quoridor-sim
```

JavaScript Viewer
```bash
cd web-viewer/
npm install
npm run dev
```

🧪 Quick Start: Training with Ray RLlib
```python

from ray.rllib.algorithms.ppo import PPOConfig
from quoridor.env import QuoridorEnv

config = PPOConfig().environment(env=QuoridorEnv, env_config={...})
algo = config.build()
algo.train()
See training_examples/ for full MARL setups.
```

🌍 Web Viewer
The web UI is built with Three.js and supports:
- Live replay of RL episodes
- Human-vs-agent gameplay
- Drag-and-drop wall placement
- API polling or WebSocket update

Launch
```bash
cd web-viewer/
npm run dev
```

📊 Observation & Action Spaces
Observation
Shape: (C, 9, 9)
Channels:
- Player positions
- Opponent positions
- Goal rows
- Horizontal/vertical walls

Action
Discrete:
- 0–3: move in cardinal directions
- 4–N: place wall at encoded location and orientation

See docs/observation_action.md for details.

🧠 Imitation Learning Support
Episodes are logged to JSONL or `.npz` with:
- `observations`, `actions`, `rewards`, `next_observations`, `dones`

Compatible with `HumanCompatibleAI/imitation`:

```bash
imitation-train expert_demos.npz --algo=bc
```

🚀 Hugging Face Space
You can deploy the environment and viewer together on Hugging Face Spaces.

Example layout:

```bash
huggingface-space/
├── app.py     # Gradio or Flask API server
├── assets/    # Quoridor model data
└── web/       # Built JS assets
📜 License
MIT License. See `LICENSE`.
```

🤝 Contributing
Pull requests and feature suggestions are welcome! Please open an issue to discuss major changes first.
