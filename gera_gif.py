import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading
import shutil
import json
import time
from PIL import Image, ImageSequence

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class GIFLabel(ctk.CTkLabel):
    def __init__(self, master, **kwargs):
        super().__init__(master, text="", **kwargs)
        self.ctk_images = []
        self.current = 0
        self.delay = 50
        self.animation_id = None

    def load_gif(self, path, fps):
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
        self.ctk_images = []
        try:
            gif = Image.open(path)
            self.delay = max(20, int(1000 / fps))
            for frame in ImageSequence.Iterator(gif):
                frame = frame.convert("RGBA")
                ctk_img = ctk.CTkImage(light_image=frame, dark_image=frame, size=frame.size)
                self.ctk_images.append(ctk_img)
            if self.ctk_images:
                self.show_frame(0)
        except Exception as e:
            print("Erro ao carregar GIF:", e)

    def show_frame(self, idx):
        if not self.ctk_images:
            return
        try:
            self.configure(image=self.ctk_images[idx % len(self.ctk_images)], text="")
            self.current = (idx + 1) % len(self.ctk_images)
            self.animation_id = self.after(self.delay, lambda: self.show_frame(self.current))
        except:
            pass

    def stop_animation(self):
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GIFSKI GUI")
        self.geometry("1160x790")
        self.resizable(True, True)

        self.ffmpeg_path = "ffmpeg"
        self.gifski_path = "gifski"
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.temp_dir = os.path.join(self.script_dir, "temp_frames")
        self.config_file = os.path.join(self.script_dir, "config.json")

        self.current_video = None
        self.png_frames = []
        self.original_width = 1280
        self.original_height = 720
        self.video_duration = 0.0
        self.total_frames = 0

        # Variáveis de configuração
        self.start_frame_var = ctk.IntVar(value=0)
        self.end_frame_var = ctk.IntVar(value=100)
        self.skip_var = ctk.IntVar(value=1)
        self.fps_var = ctk.IntVar(value=20)
        self.quality_var = ctk.IntVar(value=85)
        self.motion_var = ctk.IntVar(value=100)
        self.lossy_var = ctk.IntVar(value=100)
        self.width_var = ctk.IntVar(value=1280)
        self.height_var = ctk.IntVar(value=720)
        self.ratio_var = ctk.BooleanVar(value=True)
        self.fast_var = ctk.BooleanVar(value=True)

        self.load_config()
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_config(self):
        default = {
            "fps": 20, "quality": 85, "motion_quality": 100, "lossy_quality": 100,
            "skip": 1, "width": 1280, "height": 720, "maintain_ratio": True, "fast": True
        }
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                for key, value in saved.items():
                    if key in default:
                        default[key] = value
        except:
            pass

        self.fps_var.set(default["fps"])
        self.quality_var.set(default["quality"])
        self.motion_var.set(default["motion_quality"])
        self.lossy_var.set(default["lossy_quality"])
        self.skip_var.set(default["skip"])
        self.width_var.set(default["width"])
        self.height_var.set(default["height"])
        self.ratio_var.set(default["maintain_ratio"])
        self.fast_var.set(default["fast"])

    def save_config(self):
        config = {
            "fps": self.fps_var.get(),
            "quality": self.quality_var.get(),
            "motion_quality": self.motion_var.get(),
            "lossy_quality": self.lossy_var.get(),
            "skip": self.skip_var.get(),
            "width": self.width_var.get(),
            "height": self.height_var.get(),
            "maintain_ratio": self.ratio_var.get(),
            "fast": self.fast_var.get()
        }
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except:
            pass

    def create_widgets(self):
        left = ctk.CTkScrollableFrame(self, width=390, corner_radius=12)
        left.pack(side="left", fill="y", padx=(16, 8), pady=16)

        ctk.CTkLabel(left, text="🎥 GIFSKI", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(8, 2))
        ctk.CTkLabel(left, text="Conversor de Vídeo para GIF", 
                     font=ctk.CTkFont(size=13), text_color="gray").pack(pady=(0, 16))

        ctk.CTkButton(left, text="📄 Selecionar Vídeo (.mp4)", height=50,
                      font=ctk.CTkFont(size=15, weight="bold"),
                      command=self.select_video).pack(pady=8, padx=20, fill="x")

        self.lbl_video = ctk.CTkLabel(left, text="Nenhum vídeo selecionado", 
                                      wraplength=350, font=ctk.CTkFont(size=13))
        self.lbl_video.pack(pady=(0, 16))

        self.tabview = ctk.CTkTabview(left, height=480, corner_radius=10)
        self.tabview.pack(pady=8, padx=16, fill="both", expand=True)

        tab1 = self.tabview.add("Corte & FPS")
        tab2 = self.tabview.add("Qualidade")
        tab3 = self.tabview.add("Dimensões")

        self.create_compact_slider(tab1, "Frame Inicial", self.start_frame_var, self.update_info, 0, 500)
        self.create_compact_slider(tab1, "Frame Final", self.end_frame_var, self.update_info, 0, 500)

        ctk.CTkLabel(tab1, text="Skip a cada X frames", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(14, 2))
        ctk.CTkSlider(tab1, from_=1, to=12, variable=self.skip_var, number_of_steps=11,
                      command=self.update_info).pack(padx=15, fill="x", pady=(0, 4))
        self.lbl_skip = ctk.CTkLabel(tab1, text="1 (sem skip)", font=ctk.CTkFont(size=13))
        self.lbl_skip.pack(anchor="w", padx=15, pady=(0, 12))

        self.create_compact_slider(tab1, "FPS", self.fps_var, self.update_info, 5, 60)

        self.create_compact_slider(tab2, "Qualidade (-Q)", self.quality_var, self.update_info, 1, 100)
        self.create_compact_slider(tab2, "Motion Quality", self.motion_var, self.update_info, 1, 100)
        self.create_compact_slider(tab2, "Lossy Quality", self.lossy_var, self.update_info, 1, 100)

        ctk.CTkCheckBox(tab2, text="--fast (recomendado)", variable=self.fast_var,
                        font=ctk.CTkFont(size=14)).pack(anchor="w", padx=15, pady=12)

        self.create_compact_slider(tab3, "Largura Máx (px)", self.width_var, self.on_width_change, 300, 1920)
        self.create_compact_slider(tab3, "Altura Máx (px)", self.height_var, self.on_height_change, 300, 1920)

        ctk.CTkCheckBox(tab3, text="🔗 Manter proporção", variable=self.ratio_var,
                        font=ctk.CTkFont(size=14)).pack(anchor="w", padx=15, pady=12)

        # ==================== PAINEL DIREITO ====================
        right = ctk.CTkFrame(self, corner_radius=12)
        right.pack(side="right", fill="both", expand=True, padx=(8, 16), pady=16)

        ctk.CTkLabel(right, text="👀 Preview do GIF", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(12, 8))

        gif_container = ctk.CTkFrame(right, fg_color="#1a1a1a", corner_radius=10)
        gif_container.pack(pady=8, padx=16, fill="both", expand=True)
        gif_container.pack_propagate(False)

        self.lbl_gif = GIFLabel(gif_container)
        self.lbl_gif.pack(pady=12, padx=12, fill="both", expand=True)

        self.lbl_info = ctk.CTkLabel(right, text="Selecione um vídeo para começar...",
                                     font=ctk.CTkFont(size=15, weight="bold"), text_color="#00FFAA")
        self.lbl_info.pack(pady=10)

        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.pack(pady=12)

        ctk.CTkButton(btn_frame, text="▶️ Gerar Preview", fg_color="#00AA00", height=48,
                      font=ctk.CTkFont(size=15, weight="bold"), width=200,
                      command=self.manual_preview).pack(side="left", padx=8)

        ctk.CTkButton(btn_frame, text="💾 Salvar GIF", fg_color="#FF8800", height=48,
                      font=ctk.CTkFont(size=15, weight="bold"), width=200,
                      command=self.save_gif).pack(side="left", padx=8)

    def create_compact_slider(self, parent, text, variable, command, from_val, to_val):
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=14)).pack(anchor="w", padx=16, pady=(10, 2))
        ctk.CTkSlider(parent, from_=from_val, to=to_val, variable=variable, command=command).pack(padx=16, fill="x", pady=(0, 3))
        ctk.CTkLabel(parent, textvariable=variable, font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=16, pady=(0, 10))

    # ====================== FUNÇÕES ======================
    def update_info(self, _=None):
        if not self.png_frames:
            return
        start = self.start_frame_var.get()
        end = min(self.end_frame_var.get(), self.total_frames)
        if end <= start:
            end = start + 1
            self.end_frame_var.set(end)

        skip = self.skip_var.get()
        self.lbl_skip.configure(text=f"{skip} ({'sem skip' if skip == 1 else f'1 a cada {skip}'})")

        used_frames = end - start
        effective_frames = max(1, (used_frames + skip - 1) // skip)

        fps = self.fps_var.get()
        estimated_duration = effective_frames / fps
        est_str = f"{estimated_duration:.1f}s" if estimated_duration < 60 else f"{estimated_duration/60:.1f}min"

        self.lbl_info.configure(
            text=f"✅ {effective_frames} frames | Duração: {est_str} (Skip: {skip})",
            text_color="#00FFAA"
        )

    def get_video_info(self, video_path):
        try:
            result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                     "-of", "default=noprint_wrappers=1:nokey=1", video_path],
                                    capture_output=True, text=True, timeout=10)
            duration = float(result.stdout.strip() or 0)

            result2 = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                                      "-show_entries", "stream=width,height", "-of", "csv=p=0", video_path],
                                     capture_output=True, text=True, timeout=10)
            if result2.stdout.strip():
                w, h = map(int, result2.stdout.strip().split(','))
                return duration, w, h
            return duration, 1280, 720
        except:
            return 0.0, 1280, 720

    def select_video(self):
        self.current_video = filedialog.askopenfilename(filetypes=[("MP4", "*.mp4")])
        if not self.current_video:
            return

        self.lbl_video.configure(text=os.path.basename(self.current_video))
        self.lbl_info.configure(text="⏳ Analisando e extraindo frames...")

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.png_frames = []

        threading.Thread(target=self.extract_frames, daemon=True).start()

    def extract_frames(self):
        try:
            self.video_duration, self.original_width, self.original_height = self.get_video_info(self.current_video)
            self.width_var.set(self.original_width)
            self.height_var.set(self.original_height)

            os.makedirs(self.temp_dir, exist_ok=True)
            fps = self.fps_var.get()
            width = self.width_var.get()

            frame_pattern = os.path.join(self.temp_dir, "frame_%06d.png")
            cmd = [self.ffmpeg_path, "-y", "-i", self.current_video,
                   "-vf", f"scale={width}:-1:flags=lanczos", "-r", str(fps), frame_pattern]

            subprocess.run(cmd, timeout=50, check=True)

            self.png_frames = sorted([os.path.join(self.temp_dir, f) for f in os.listdir(self.temp_dir) if f.endswith(".png")])
            self.total_frames = len(self.png_frames)

            self.start_frame_var.set(0)
            self.end_frame_var.set(self.total_frames)
            self.skip_var.set(1)

            self.update_info()

            # ✅ NOVO: Preview automático após extrair os frames
            self.after(300, self.auto_preview)   # pequeno delay para UI atualizar

        except Exception as e:
            self.lbl_info.configure(text=f"❌ Erro ao processar vídeo: {str(e)[:60]}")

    def auto_preview(self):
        """Chama o preview automaticamente após selecionar o vídeo"""
        if self.png_frames:
            self.manual_preview()

    def generate_gif(self, is_preview):
        try:
            self.lbl_info.configure(text="⏳ Gerando GIF...")

            start = self.start_frame_var.get()
            end = self.end_frame_var.get()
            skip = self.skip_var.get()

            selected_frames = self.png_frames[start:end:skip]

            fps = self.fps_var.get()
            width = self.width_var.get()

            default_name = os.path.splitext(os.path.basename(self.current_video))[0] + ".gif"

            if is_preview:
                output_path = os.path.join(self.script_dir, "preview_" + default_name)
            else:
                output_path = filedialog.asksaveasfilename(
                    initialfile=default_name,
                    defaultextension=".gif",
                    filetypes=[("GIF files", "*.gif")],
                    title="Salvar GIF como..."
                )
                if not output_path:
                    self.lbl_info.configure(text="Salvamento cancelado")
                    return

            cmd = [self.gifski_path, "-q", "--fps", str(fps),
                   "-Q", str(self.quality_var.get()),
                   "--motion-quality", str(self.motion_var.get()),
                   "--lossy-quality", str(self.lossy_var.get()),
                   "-W", str(width), "-o", output_path] + selected_frames

            if self.fast_var.get():
                cmd.append("--fast")

            subprocess.run(cmd, timeout=80, check=True)

            with Image.open(output_path) as img:
                w, h = img.size
            size_kb = os.path.getsize(output_path) / 1024

            self.lbl_info.configure(
                text=f"✅ {w}x{h} | {size_kb:.1f} KB | {len(selected_frames)} frames",
                text_color="#00FFAA"
            )

            if is_preview:
                self.lbl_gif.load_gif(output_path, fps)

        except Exception as e:
            self.lbl_info.configure(text=f"❌ Erro: {str(e)[:70]}")

    def on_width_change(self, value):
        if self.ratio_var.get() and self.original_width > 0:
            ratio = self.original_height / self.original_width
            new_height = int(float(value) * ratio)
            self.height_var.set(max(300, min(1920, new_height)))

    def on_height_change(self, value):
        if self.ratio_var.get() and self.original_height > 0:
            ratio = self.original_width / self.original_height
            new_width = int(float(value) * ratio)
            self.width_var.set(max(300, min(1920, new_width)))

    def manual_preview(self):
        if not self.png_frames:
            messagebox.showwarning("Aviso", "Selecione um vídeo primeiro!")
            return
        threading.Thread(target=self.generate_gif, args=(True,), daemon=True).start()

    def save_gif(self):
        if not self.png_frames:
            messagebox.showwarning("Aviso", "Selecione um vídeo primeiro!")
            return
        threading.Thread(target=self.generate_gif, args=(False,), daemon=True).start()

    def on_closing(self):
        self.save_config()
        self.lbl_gif.stop_animation()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()