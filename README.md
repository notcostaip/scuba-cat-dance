# 🐱 Scuba Cat Dance

Detecte o **Scuba Cat Dance** em tempo real usando sua webcam! Quando você faz os movimentos certos — tampar o nariz e acenar com a mão — o vídeo do gatinho scuba aparece dançando na tela. 🎉

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-00A67E?style=for-the-badge&logo=google&logoColor=white)

---

## 🎬 Como funciona

O app usa **inteligência artificial** (MediaPipe Pose) para detectar 33 pontos do seu corpo pela webcam e analisa **3 gestos simultâneos**:

| Gesto | O que detecta |
|-------|--------------|
| 🤏 **Nariz tampado** | Uma mão próxima ao nariz |
| 👋 **Mão acenando** | A outra mão oscilando lateralmente |
| 💃 **Corpo balançando** | Movimento lateral dos quadris |

Quando **nariz tampado + (aceno OU balanço)** persiste por alguns frames → o gatinho aparece! 🐱

---

## 🚀 Como rodar

### 1. Clone o repositório
```bash
git clone https://github.com/notcostaip/scuba-cat-dance.git
cd scuba-cat-dance
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Garanta que os assets estão na pasta `assets/`

| Arquivo | Descrição |
|---------|-----------|
| `pose_landmarker_lite.task` | Modelo de IA do MediaPipe (~5.5MB) |
| `scuba_cat_video.mp4` | Vídeo do gatinho que aparece na tela |

> O modelo pode ser baixado em: [MediaPipe Pose Landmarker](https://developers.google.com/mediapipe/solutions/vision/pose_landmarker#models)

### 4. Execute
```bash
python scuba_cat_dance.py
```

---

## 🎮 Controles

| Tecla | Ação |
|-------|------|
| `Q` ou `ESC` | Sair |
| `D` | Ativar/desativar modo Debug (mostra o esqueleto) |
| `S` | Trocar sensibilidade (Fácil → Médio → Difícil) |

---

## 🎚️ Níveis de Sensibilidade

| Nível | Detecção | Descrição |
|-------|----------|-----------|
| **Fácil** | 5 frames | Thresholds largos, ativa rápido |
| **Médio** | 10 frames | Equilíbrio entre precisão e facilidade |
| **Difícil** | 15 frames | Precisa de gestos mais precisos e consistentes |

---

## 🛠️ Tecnologias

- **[OpenCV](https://opencv.org/)** — Captura de vídeo, desenho na tela, overlay e efeitos visuais
- **[MediaPipe](https://mediapipe.dev/)** — Detecção de pose em tempo real (33 landmarks do corpo)
- **[NumPy](https://numpy.org/)** — Cálculos auxiliares e geração de partículas

---

## 📁 Estrutura do Projeto

```
scuba-cat-dance/
├── scuba_cat_dance.py     ← Script principal
├── requirements.txt       ← Dependências Python
├── README.md              ← Este arquivo
└── assets/
    ├── pose_landmarker_lite.task   ← Modelo de IA
    └── scuba_cat_video.mp4         ← Vídeo do gatinho
```

---

## 📝 Licença

Feito por [Costa](https://github.com/notcostaip) com ☕ e muita diversão.
