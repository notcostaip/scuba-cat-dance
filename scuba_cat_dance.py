"""
SCUBA CAT DANCE - Detecta o gesto e mostra o vídeo do gatinho!
Controles: Q/ESC=Sair | D=Debug | S=Sensibilidade
"""
import cv2
import mediapipe as mp
import numpy as np
import os, time, math

# Caminhos dos arquivos (relativos ao diretório do script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_PATH = os.path.join(SCRIPT_DIR, "assets", "scuba_cat_video.mp4")
MODEL_PATH = os.path.join(SCRIPT_DIR, "assets", "pose_landmarker_lite.task")

# Resolução da janela
W, H = 1280, 720

# Índices dos pontos do corpo (landmarks do MediaPipe Pose)
NOSE = 0
L_SHOULDER, R_SHOULDER = 11, 12
L_ELBOW, R_ELBOW = 13, 14
L_WRIST, R_WRIST = 15, 16
L_INDEX, R_INDEX = 19, 20
L_HIP, R_HIP = 23, 24

# Níveis de sensibilidade (thresholds para cada dificuldade)
SENSITIVITIES = [
    {"nose_dist": 0.18, "wave_dist": 0.15, "sway": 0.02, "frames": 5,  "label": "FACIL"},
    {"nose_dist": 0.13, "wave_dist": 0.20, "sway": 0.03, "frames": 10, "label": "MEDIO"},
    {"nose_dist": 0.10, "wave_dist": 0.25, "sway": 0.04, "frames": 15, "label": "DIFICIL"},
]


class ScubaCatDance:
    """Classe principal que gerencia detecção de pose, overlay do vídeo e efeitos visuais."""

    def __init__(self):
        # MediaPipe e câmera
        self.pose = None
        self.cap = None

        # Vídeo do gatinho e controle de transparência (fade in/out)
        self.cat_video = None
        self.cat_alpha = 0.0
        self.cat_target = 0.0
        self.cat_playing = False

        # Estado da detecção
        self.scuba_on = False
        self.det_count = 0       # Contador de frames com gesto detectado
        self.deact_count = 0     # Contador de frames sem gesto (para desativar)
        self.nose_ok = False     # Mão no nariz?
        self.wave_ok = False     # Mão acenando?
        self.sway_ok = False     # Corpo balançando?

        # Histórico de posições para análise de movimento
        self.wave_hist = []      # Posições X do pulso (aceno)
        self.sway_hist = []      # Posições X do centro dos quadris (balanço)

        # Interface e configurações
        self.debug = False
        self.sens_idx = 0
        self.sens = SENSITIVITIES[0]

        # Efeito de bolhas
        self.particles = []
        self.bubble_t = 0

        # Último esqueleto detectado
        self.latest_landmarks = None

    def _select_camera(self):
        """Escaneia câmeras disponíveis e deixa o usuário escolher."""
        print("\n📷 Escaneando câmeras disponíveis...")
        available = []
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                name = f"Camera {i}"
                if i == 0:
                    name += " (provavelmente webcam do Mac)"
                else:
                    name += " (pode ser iPhone / camera externa)"
                available.append((i, name, w, h))
                cap.release()
            else:
                cap.release()

        if not available:
            return None

        if len(available) == 1:
            idx = available[0][0]
            print(f"  ✅ Camera encontrada: {available[0][1]} ({available[0][2]}x{available[0][3]})")
        else:
            print(f"\n  Cameras encontradas ({len(available)}):")
            for i, name, w, h in available:
                print(f"    [{i}] {name} - {w}x{h}")
            print()
            try:
                choice = input("  👉 Digite o numero da camera (ou Enter para 0): ").strip()
                idx = int(choice) if choice else available[0][0]
            except (ValueError, EOFError):
                idx = available[0][0]

        print(f"  🎥 Usando camera {idx}")
        cap = cv2.VideoCapture(idx)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)
        return cap if cap.isOpened() else None

    def start(self):
        """Inicializa todos os componentes e roda o loop principal."""

        # Configuração do MediaPipe Pose Landmarker
        BaseOptions = mp.tasks.BaseOptions
        PoseLandmarker = mp.tasks.vision.PoseLandmarker
        PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        RunningMode = mp.tasks.vision.RunningMode

        self.pose = PoseLandmarker.create_from_options(
            PoseLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=MODEL_PATH),
                running_mode=RunningMode.VIDEO,
                num_poses=1,
                min_pose_detection_confidence=0.6,
                min_tracking_confidence=0.5,
            )
        )

        # Seleção de câmera
        self.cap = self._select_camera()
        if self.cap is None:
            print("❌ Nenhuma câmera encontrada!"); return

        # Carrega o vídeo do gatinho
        if not os.path.exists(VIDEO_PATH):
            print(f"❌ Vídeo não encontrado: {VIDEO_PATH}"); return
        self.cat_video = cv2.VideoCapture(VIDEO_PATH)

        print("\n🐱 SCUBA CAT DANCE 🐱")
        print("Tampa o nariz + balança a mão!")
        print("Q=Sair | D=Debug | S=Sensibilidade\n")

        cv2.namedWindow("Scuba Cat Dance", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Scuba Cat Dance", W, H)

        # ───── Loop principal (~30fps) ─────
        ts = 0
        while True:
            ret, frame = self.cap.read()
            if not ret: break
            frame = cv2.flip(frame, 1)       # Espelha (modo selfie)
            frame = cv2.resize(frame, (W, H))

            # Detecção de pose via MediaPipe
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            ts += 33  # Incremento de timestamp (~30fps)
            results = self.pose.detect_for_video(mp_img, ts)

            # Reseta indicadores a cada frame
            self.nose_ok = self.wave_ok = self.sway_ok = False
            self.latest_landmarks = None

            if results.pose_landmarks and len(results.pose_landmarks) > 0:
                lm = results.pose_landmarks[0]
                self.latest_landmarks = lm
                self._detect(lm)

                if self.debug:
                    self._draw_landmarks(frame, lm)

            # Lógica de ativação / desativação do Scuba Dance
            if self.nose_ok and (self.wave_ok or self.sway_ok):
                self.det_count += 1; self.deact_count = 0
            else:
                self.deact_count += 1
                if self.deact_count > 15:
                    self.det_count = max(0, self.det_count - 2)

            thresh = self.sens["frames"]
            if self.det_count >= thresh and not self.scuba_on:
                self.scuba_on = True; self.cat_playing = True; self.cat_target = 1.0
            elif self.scuba_on and self.det_count <= 0:
                self.scuba_on = False; self.cat_target = 0.0

            # Efeito de bolhas subindo
            self._update_bubbles(frame)

            # Overlay do vídeo do gatinho (com fade)
            if self.cat_playing or self.cat_alpha > 0.01:
                self._overlay_cat(frame)

            # HUD (indicadores + barra de progresso)
            self._draw_hud(frame)

            cv2.imshow("Scuba Cat Dance", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27): break
            elif key == ord('d'): self.debug = not self.debug
            elif key == ord('s'):
                self.sens_idx = (self.sens_idx + 1) % len(SENSITIVITIES)
                self.sens = SENSITIVITIES[self.sens_idx]

        # Libera recursos
        self.cap.release()
        if self.cat_video: self.cat_video.release()
        if self.pose: self.pose.close()
        cv2.destroyAllWindows()

    def _dist(self, a, b):
        """Calcula a distância euclidiana 2D entre dois landmarks."""
        return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

    def _detect(self, lm):
        """Analisa os landmarks e atualiza os 3 indicadores de gesto."""
        nose = lm[NOSE]

        # ① Verifica qual mão está perto do nariz (tampando)
        plugging = None
        for side, wi, ii in [("L", L_WRIST, L_INDEX), ("R", R_WRIST, R_INDEX)]:
            d = min(self._dist(nose, lm[wi]), self._dist(nose, lm[ii]))
            if d < self.sens["nose_dist"]:
                plugging = side; break

        self.nose_ok = plugging is not None
        if not plugging: return

        # ② Verifica se a OUTRA mão está acenando (estendida + oscilando)
        if plugging == "L":
            ww, ws = R_WRIST, R_SHOULDER
        else:
            ww, ws = L_WRIST, L_SHOULDER

        # Mão precisa estar distante do ombro (estendida)
        ext = self._dist(lm[ww], lm[ws]) > self.sens["wave_dist"]

        # Histórico de posições X para detectar oscilação
        self.wave_hist.append(lm[ww].x)
        if len(self.wave_hist) > 15: self.wave_hist.pop(0)
        waving = False
        if len(self.wave_hist) >= 6:
            diffs = [self.wave_hist[i+1]-self.wave_hist[i] for i in range(len(self.wave_hist)-1)]
            changes = sum(1 for i in range(len(diffs)-1) if diffs[i]*diffs[i+1] < 0)
            waving = changes >= 2  # 2+ mudanças de direção = acenando
        self.wave_ok = ext and waving

        # ③ Verifica se o corpo está balançando (amplitude do centro dos quadris)
        cx = (lm[L_HIP].x + lm[R_HIP].x) / 2
        self.sway_hist.append(cx)
        if len(self.sway_hist) > 15: self.sway_hist.pop(0)
        if len(self.sway_hist) >= 6:
            amp = max(self.sway_hist) - min(self.sway_hist)
            self.sway_ok = amp > self.sens["sway"]

    def _draw_landmarks(self, frame, lm):
        """Desenha o esqueleto no modo debug."""
        fh, fw = frame.shape[:2]
        pts = [(int(l.x * fw), int(l.y * fh)) for l in lm]
        # Conexões do esqueleto (ombros, braços, tronco)
        connections = [
            (L_SHOULDER, R_SHOULDER), (L_SHOULDER, L_ELBOW), (L_ELBOW, L_WRIST),
            (R_SHOULDER, R_ELBOW), (R_ELBOW, R_WRIST),
            (L_SHOULDER, L_HIP), (R_SHOULDER, R_HIP), (L_HIP, R_HIP),
        ]
        for a, b in connections:
            if a < len(pts) and b < len(pts):
                cv2.line(frame, pts[a], pts[b], (0, 255, 0), 2)
        for p in pts[:25]:
            cv2.circle(frame, p, 4, (0, 200, 255), -1)

    def _get_cat_frame(self):
        """Lê o próximo frame do vídeo do gatinho (com loop infinito)."""
        ret, f = self.cat_video.read()
        if not ret:
            self.cat_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, f = self.cat_video.read()
        return f if ret else None

    def _overlay_cat(self, frame):
        """Sobrepõe o vídeo do gatinho no canto inferior direito com fade in/out."""
        # Transição suave da transparência
        spd = 0.08
        if self.cat_alpha < self.cat_target:
            self.cat_alpha = min(self.cat_alpha + spd, self.cat_target)
        else:
            self.cat_alpha = max(self.cat_alpha - spd, self.cat_target)

        if self.cat_alpha <= 0.01:
            self.cat_playing = False; return

        cf = self._get_cat_frame()
        if cf is None: return

        # Calcula dimensões mantendo proporção (max 55% da altura, 50% da largura)
        fh, fw = frame.shape[:2]
        ch = int(fh * 0.55)
        cw = int(ch * cf.shape[1] / cf.shape[0])
        if cw > int(fw * 0.5):
            cw = int(fw * 0.5); ch = int(cw * cf.shape[0] / cf.shape[1])

        cat = cv2.resize(cf, (cw, ch))
        xo = fw - cw - 30; yo = fh - ch - 50  # Canto inferior direito
        xo, yo = max(0, xo), max(0, yo)

        roi = frame[yo:yo+ch, xo:xo+cw]
        if roi.shape[:2] == cat.shape[:2]:
            # Borda brilhante ao redor do vídeo
            cv2.rectangle(frame, (xo-3, yo-3), (xo+cw+3, yo+ch+3), (0, 255, 255), 3)
            cv2.rectangle(frame, (xo-5, yo-5), (xo+cw+5, yo+ch+5), (0, 200, 255), 1)

            # Blend (mistura) com transparência
            blended = cv2.addWeighted(cat, self.cat_alpha, roi, 1.0 - self.cat_alpha, 0)
            frame[yo:yo+ch, xo:xo+cw] = blended

            # Rótulo "SCUBA CAT DANCE" acima do vídeo
            lbl = "SCUBA CAT DANCE"
            sz = cv2.getTextSize(lbl, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            lx = xo + (cw - sz[0]) // 2; ly = yo - 12
            cv2.rectangle(frame, (lx-8, ly-sz[1]-8), (lx+sz[0]+8, ly+8), (0,0,0), -1)
            cv2.rectangle(frame, (lx-8, ly-sz[1]-8), (lx+sz[0]+8, ly+8), (0,255,255), 2)
            cv2.putText(frame, lbl, (lx, ly), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    def _update_bubbles(self, frame):
        """Gera e anima bolhas subindo pela tela (efeito aquático)."""
        self.bubble_t += 1
        # Cria 3 novas bolhas a cada 8 frames enquanto scuba está ativo
        if self.bubble_t % 8 == 0 and self.scuba_on:
            for _ in range(3):
                self.particles.append({
                    'x': np.random.randint(50, W-50),     # Posição X aleatória
                    'y': H,                                # Começa na parte de baixo
                    'sz': np.random.randint(5, 20),        # Tamanho aleatório
                    'sp': np.random.uniform(2, 6),         # Velocidade
                    'w': np.random.uniform(0, 6.28),       # Fase da onda senoidal
                    'ws': np.random.uniform(0.05, 0.15),   # Velocidade da oscilação lateral
                })

        overlay = frame.copy()
        alive = []
        for p in self.particles:
            p['y'] -= p['sp']; p['w'] += p['ws']
            x, y = int(p['x'] + math.sin(p['w'])*15), int(p['y'])
            if y > -20:
                alive.append(p)
                # Contorno da bolha + reflexo de luz
                cv2.circle(overlay, (x,y), p['sz'], (230,180,80), 2)
                cv2.circle(overlay, (x-p['sz']//3, y-p['sz']//3), max(1,p['sz']//4), (255,255,255), -1)
        self.particles = alive
        if alive:
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    def _draw_hud(self, frame):
        """Desenha o painel de informações (HUD) na tela."""
        fh, fw = frame.shape[:2]

        # Painel semitransparente no canto superior esquerdo
        ov = frame.copy()
        cv2.rectangle(ov, (0,0), (320, 140), (0,0,0), -1)
        cv2.addWeighted(ov, 0.6, frame, 0.4, 0, frame)

        cv2.putText(frame, "SCUBA CAT DANCE", (15,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

        # Indicadores de gesto (bolinhas coloridas)
        indicators = [
            ("Nariz tampado", self.nose_ok, (0,150,255)),
            ("Mao acenando", self.wave_ok, (255,200,0)),
            ("Corpo balancando", self.sway_ok, (0,255,150)),
        ]
        y = 58
        for lbl, on, col in indicators:
            cv2.circle(frame, (25, y-5), 8, col if on else (80,80,80), -1)
            cv2.putText(frame, lbl, (42, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255) if on else (150,150,150), 1)
            y += 26

        # Barra de progresso (preenchimento proporcional aos frames detectados)
        prog = min(self.det_count / max(self.sens["frames"], 1), 1.0)
        bx, by, bw, bh = 15, y+2, 280, 12
        cv2.rectangle(frame, (bx,by), (bx+bw, by+bh), (60,60,60), -1)
        if prog > 0:
            cv2.rectangle(frame, (bx,by), (bx+int(bw*prog), by+bh), (0,255,0) if prog>=1 else (0,200,255), -1)
        cv2.rectangle(frame, (bx,by), (bx+bw, by+bh), (200,200,200), 1)

        # Banner pulsante "SCUBA DANCE!" quando ativado
        if self.scuba_on:
            pulse = abs(math.sin(time.time()*4))
            txt = "SCUBA DANCE!"
            sz = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
            tx = (fw - sz[0])//2
            # Sombra + texto principal com efeito de pulso
            cv2.putText(frame, txt, (tx+2, 52), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,int(100+155*pulse)), 4)
            cv2.putText(frame, txt, (tx, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,255), 3)

        # Barra inferior com atalhos de teclado
        ov2 = frame.copy()
        cv2.rectangle(ov2, (0, fh-35), (fw, fh), (0,0,0), -1)
        cv2.addWeighted(ov2, 0.5, frame, 0.5, 0, frame)
        cv2.putText(frame, f"[Q] Sair | [D] Debug | [S] Sens: {self.sens['label']}", (15, fh-12),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180,180,180), 1)


if __name__ == "__main__":
    ScubaCatDance().start()
