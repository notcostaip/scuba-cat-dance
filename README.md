<div align="center">

<!-- HEADER BANNER -->
<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:7f1d1d,50:dc2626,100:991b1b&height=230&section=header&text=Scuba%20Cat%20Dance&fontSize=70&fontColor=ffffff&animation=twinkling&fontAlignY=35&desc=Real-time%20AI%20Gesture%20Recognition&descAlignY=55&descSize=18&descColor=fca5a5" />

<br/>

<!-- BADGES -->
<div>
  <img src="https://img.shields.io/badge/Python_3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/OpenCV_4.8+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV" />
  <img src="https://img.shields.io/badge/MediaPipe_0.10+-00A67E?style=for-the-badge&logo=google&logoColor=white" alt="MediaPipe" />
</div>

<br/>

Detecte o **Scuba Cat Dance** em tempo real usando sua webcam! Quando você faz os movimentos certos — tampar o nariz e acenar com a mão — o vídeo do gatinho scuba aparece dançando na tela. 🎉

</div>

<br/>

<!-- RED ANIMATED DIVIDER -->
<img src="https://raw.githubusercontent.com/notcostaip/notcostaip/main/assets/red-divider.svg" width="100%">

<!-- COMO FUNCIONA -->
<div align="center">

### &nbsp; 🎬 Como funciona

</div>

O app usa **inteligência artificial** (MediaPipe Pose) para detectar 33 pontos do seu corpo pela webcam e analisa **3 gestos simultâneos**:

| Gesto | O que detecta |
|-------|--------------|
| 🤏 **Nariz tampado** | Uma mão próxima ao nariz |
| 👋 **Mão acenando** | A outra mão oscilando lateralmente |
| 💃 **Corpo balançando** | Movimento lateral dos quadris |

Quando **nariz tampado + (aceno OU balanço)** persiste por alguns frames → o gatinho aparece! 🐱

<!-- RED ANIMATED DIVIDER -->
<img src="https://raw.githubusercontent.com/notcostaip/notcostaip/main/assets/red-divider.svg" width="100%">

<!-- COMO RODAR -->
<div align="center">

### &nbsp; 🚀 Como rodar

</div>

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
python3 scuba_cat_dance.py
```

<!-- RED ANIMATED DIVIDER -->
<img src="https://raw.githubusercontent.com/notcostaip/notcostaip/main/assets/red-divider.svg" width="100%">

<!-- CONTROLES & NÍVEIS -->
<div align="center">

### &nbsp; 🎮 Controles & Níveis

</div>

<br/>

<table>
<tr>
<td width="50%" valign="top">

<h4 align="center">🕹️ Teclas</h3>

| Tecla | Ação |
|-------|------|
| `Q` ou `ESC` | Sair |
| `D` | Modo Debug |
| `S` | Sensibilidade |

</td>
<td width="50%" valign="top">

<h4 align="center">🎚️ Sensibilidade</h3>

| Nível | Frames | Descrição |
|-------|--------|-----------|
| **Fácil** | 5 | Ativa rápido |
| **Médio** | 10 | Equilibrado |
| **Difícil** | 15 | Exige precisão |

</td>
</tr>
</table>

<!-- RED ANIMATED DIVIDER -->
<img src="https://raw.githubusercontent.com/notcostaip/notcostaip/main/assets/red-divider.svg" width="100%">

<!-- TECNOLOGIAS -->
<div align="center">

### &nbsp; 🛠️ Tecnologias

<br/>

<img src="https://skillicons.dev/icons?i=python,opencv&theme=dark" alt="Tech" />

<br/><br/>

</div>

- **[OpenCV](https://opencv.org/)** — Captura de vídeo e efeitos visuais
- **[MediaPipe](https://mediapipe.dev/)** — Detecção de pose
- **[NumPy](https://numpy.org/)** — Cálculos e arrays

<!-- RED ANIMATED DIVIDER -->
<img src="https://raw.githubusercontent.com/notcostaip/notcostaip/main/assets/red-divider.svg" width="100%">

<!-- ESTRUTURA -->
<div align="center">

### &nbsp; 📁 Estrutura do Projeto

</div>

```
scuba-cat-dance/
├── scuba_cat_dance.py     ← Script principal
├── requirements.txt       ← Dependências Python
├── README.md              ← Este arquivo
└── assets/
    ├── pose_landmarker_lite.task   ← Modelo de IA
    └── scuba_cat_video.mp4         ← Vídeo do gatinho
```

<br/>

<!-- FOOTER -->
<div align="center">

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:7f1d1d,50:dc2626,100:991b1b&height=130&section=footer" />

<br/>

**Feito por [Costa](https://github.com/notcostaip) com ☕ e muita diversão.**

</div>
