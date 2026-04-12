# # import sys
# # import numpy as np
# # from pathlib import Path
# # from scipy.io import wavfile
# # from scipy.signal import spectrogram
# #
# # from PySide6.QtWidgets import (
# #     QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
# #     QWidget, QPushButton, QLabel, QFileDialog, QSizePolicy
# # )
# # from PySide6.QtCore import Qt
# # from PySide6.QtGui import QFont
# #
# # from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
# # from matplotlib.figure import Figure
# # import matplotlib.colors as mcolors
# #
# #
# # class SpectrogramCanvas(FigureCanvas):
# #     def __init__(self, parent=None):
# #         self.fig = Figure(facecolor="#0e0e0e")
# #         super().__init__(self.fig)
# #         self.setParent(parent)
# #         self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
# #         self._draw_empty()
# #
# #     def _draw_empty(self):
# #         self.fig.clear()
# #         ax = self.fig.add_subplot(111, facecolor="#1a1a1a")
# #         ax.text(
# #             0.5, 0.5, "Drop a WAV file or click 'Open WAV'",
# #             ha="center", va="center", color="#555", fontsize=13,
# #             transform=ax.transAxes
# #         )
# #         ax.set_xticks([])
# #         ax.set_yticks([])
# #         self.draw()
# #
# #     def plot_spectrogram(self, file_path: str):
# #         try:
# #             sample_rate, data = wavfile.read(file_path)
# #         except Exception as e:
# #             print(f"Error reading WAV: {e}")
# #             return
# #
# #         # Convert to mono if stereo
# #         if data.ndim == 2:
# #             data = data.mean(axis=1)
# #
# #         # Normalize
# #         data = data.astype(np.float32)
# #         data /= np.max(np.abs(data)) if np.max(np.abs(data)) > 0 else 1
# #
# #         # Compute spectrogram
# #         nperseg = 1024
# #         f, t, Sxx = spectrogram(data, fs=sample_rate, nperseg=nperseg, noverlap=nperseg // 2)
# #
# #         # Convert to dB
# #         Sxx_db = 10 * np.log10(Sxx + 1e-10)
# #
# #         # --- Plot ---
# #         self.fig.clear()
# #         ax = self.fig.add_subplot(111, facecolor="#0d0d0d")
# #
# #         img = ax.pcolormesh(
# #             t, f / 1000, Sxx_db,
# #             shading="gouraud",
# #             cmap="inferno",
# #             vmin=Sxx_db.max() - 80,   # dynamic range: 80 dB
# #             vmax=Sxx_db.max()
# #         )
# #
# #         cbar = self.fig.colorbar(img, ax=ax, pad=0.01)
# #         cbar.set_label("Intensity (dB)", color="#aaa", fontsize=9)
# #         cbar.ax.yaxis.set_tick_params(color="#aaa")
# #         plt_tick_color = "#aaa"
# #         for label in cbar.ax.get_yticklabels():
# #             label.set_color(plt_tick_color)
# #
# #         duration = len(data) / sample_rate
# #         ax.set_xlim(0, t[-1])
# #         ax.set_ylim(0, f[-1] / 1000)
# #         ax.set_xlabel("Time (s)", color="#aaa", fontsize=10)
# #         ax.set_ylabel("Frequency (kHz)", color="#aaa", fontsize=10)
# #         ax.tick_params(colors="#aaa")
# #         for spine in ax.spines.values():
# #             spine.set_edgecolor("#333")
# #
# #         filename = Path(file_path).name
# #         ax.set_title(f"{filename}  |  {sample_rate} Hz  |  {duration:.2f}s",
# #                      color="#ddd", fontsize=11, pad=10)
# #
# #         self.fig.tight_layout()
# #         self.draw()
# #
# #
# # class MainWindow(QMainWindow):
# #     def __init__(self):
# #         super().__init__()
# #         self.setWindowTitle("WAV Spectrogram Viewer")
# #         self.resize(1000, 600)
# #         self.setStyleSheet("background-color: #121212; color: #ddd;")
# #
# #         # --- Central widget ---
# #         central = QWidget()
# #         self.setCentralWidget(central)
# #         layout = QVBoxLayout(central)
# #         layout.setContentsMargins(12, 12, 12, 12)
# #         layout.setSpacing(8)
# #
# #         # --- Toolbar ---
# #         toolbar = QHBoxLayout()
# #         self.open_btn = QPushButton("Open WAV")
# #         self.open_btn.setFixedHeight(34)
# #         self.open_btn.setStyleSheet("""
# #             QPushButton {
# #                 background: #2a2a2a; color: #eee;
# #                 border: 1px solid #444; border-radius: 6px;
# #                 padding: 0 16px; font-size: 13px;
# #             }
# #             QPushButton:hover { background: #3a3a3a; }
# #             QPushButton:pressed { background: #1a1a1a; }
# #         """)
# #         self.open_btn.clicked.connect(self.open_file)
# #
# #         self.info_label = QLabel("No file loaded")
# #         self.info_label.setStyleSheet("color: #666; font-size: 12px;")
# #
# #         toolbar.addWidget(self.open_btn)
# #         toolbar.addWidget(self.info_label)
# #         toolbar.addStretch()
# #         layout.addLayout(toolbar)
# #
# #         # --- Canvas ---
# #         self.canvas = SpectrogramCanvas(self)
# #         # Enable drag & drop on the main window
# #         self.setAcceptDrops(True)
# #         layout.addWidget(self.canvas)
# #
# #     def open_file(self):
# #         path, _ = QFileDialog.getOpenFileName(
# #             self, "Open WAV File", "", "WAV Files (*.wav)"
# #         )
# #         if path:
# #             self.load_file(path)
# #
# #     def load_file(self, path: str):
# #         self.info_label.setText(f"Loading {Path(path).name}...")
# #         QApplication.processEvents()
# #         self.canvas.plot_spectrogram(path)
# #         self.info_label.setText(f"Loaded: {Path(path).name}")
# #
# #     # --- Drag & drop support ---
# #     def dragEnterEvent(self, event):
# #         if event.mimeData().hasUrls():
# #             urls = event.mimeData().urls()
# #             if any(u.toLocalFile().lower().endswith(".wav") for u in urls):
# #                 event.acceptProposedAction()
# #                 return
# #         event.ignore()
# #
# #     def dragMoveEvent(self, event):
# #         if event.mimeData().hasUrls():
# #             event.acceptProposedAction()
# #
# #     def dropEvent(self, event):
# #         for url in event.mimeData().urls():
# #             path = url.toLocalFile()
# #             if path.lower().endswith(".wav"):
# #                 self.load_file(path)
# #                 break
# #
# #
# # if __name__ == "__main__":
# #     app = QApplication(sys.argv)
# #     window = MainWindow()
# #     window.show()
# #     sys.exit(app.exec())
#
# import sys
# import numpy as np
# from pathlib import Path
# from scipy.io import wavfile
# from scipy.signal import spectrogram
#
# from PySide6.QtWidgets import (
#     QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
#     QWidget, QPushButton, QLabel, QFileDialog, QSizePolicy
# )
# from PySide6.QtCore import Qt
# from PySide6.QtGui import QFont
#
# from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure
#
#
# class AudioCanvas(FigureCanvas):
#     def __init__(self, parent=None):
#         self.fig = Figure(facecolor="#0e0e0e")
#         super().__init__(self.fig)
#         self.setParent(parent)
#         self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#         self._draw_empty()
#
#     def _draw_empty(self):
#         self.fig.clear()
#
#         ax_wave = self.fig.add_subplot(211, facecolor="#1a1a1a")
#         ax_wave.text(0.5, 0.5, "Drop a WAV file or click 'Open WAV'",
#                      ha="center", va="center", color="#555", fontsize=13,
#                      transform=ax_wave.transAxes)
#         ax_wave.set_xticks([])
#         ax_wave.set_yticks([])
#
#         self.fig.tight_layout(pad=2.0)
#         self.draw()
#
#     def plot(self, file_path: str):
#         try:
#             sample_rate, data = wavfile.read(file_path)
#         except Exception as e:
#             print(f"Error reading WAV: {e}")
#             return
#
#         # --- Stereo → mono ---
#         if data.ndim == 2:
#             data = data.mean(axis=1)
#
#         # --- Normalize to [-1, 1] ---
#         data = data.astype(np.float32)
#         peak = np.max(np.abs(data))
#         if peak > 0:
#             data /= peak
#
#         duration   = len(data) / sample_rate
#         time_axis  = np.linspace(0, duration, num=len(data))
#
#         # --- Downsample waveform for display (max 50 000 points) ---
#         MAX_PTS  = 50_000
#         step     = max(1, len(data) // MAX_PTS)
#         t_plot   = time_axis[::step]
#         d_plot   = data[::step]
#
#         # --- Spectrogram ---
#         nperseg = 1024
#         f, t, Sxx = spectrogram(data, fs=sample_rate,
#                                  nperseg=nperseg, noverlap=nperseg // 2)
#         Sxx_db = 10 * np.log10(Sxx + 1e-10)
#
#         # ── Layout: 2 rows, shared x-axis ──────────────────────────────────
#         self.fig.clear()
#
#         ax_wave = self.fig.subplots(
#             1, 1,
#             sharex=False,           # x-axes are linked by range but different units
#             gridspec_kw={"height_ratios": [1], "hspace": 0.35},
#         )
#         self.fig.patch.set_facecolor("#0e0e0e")
#
#         # ── Waveform ───────────────────────────────────────────────────────
#         ax_wave.set_facecolor("#0d0d0d")
#         ax_wave.plot(t_plot, d_plot, color="#1DB954", linewidth=0.6, alpha=0.85)
#
#         # RMS envelope overlay
#         rms_window = max(1, len(data) // 500)
#         rms_frames = len(data) // rms_window
#         rms_vals   = np.array([
#             np.sqrt(np.mean(data[i*rms_window:(i+1)*rms_window]**2))
#             for i in range(rms_frames)
#         ])
#         rms_times  = np.linspace(0, duration, rms_frames)
#         ax_wave.fill_between(rms_times,  rms_vals, -rms_vals,
#                              color="#1DB954", alpha=0.18)
#         ax_wave.fill_between(rms_times,  rms_vals,  0, color="#1DB954", alpha=0.25)
#         ax_wave.fill_between(rms_times, -rms_vals,  0, color="#1DB954", alpha=0.25)
#
#         ax_wave.axhline(0, color="#333", linewidth=0.8)
#         ax_wave.set_xlim(0, duration)
#         ax_wave.set_ylim(-1.05, 1.05)
#         ax_wave.set_ylabel("Amplitude", color="#aaa", fontsize=9)
#         ax_wave.set_xlabel("Time (s)", color="#aaa", fontsize=9)
#         ax_wave.tick_params(colors="#aaa", labelsize=8)
#         for spine in ax_wave.spines.values():
#             spine.set_edgecolor("#333")
#
#         filename = Path(file_path).name
#         ax_wave.set_title(
#             f"{filename}  |  {sample_rate} Hz  |  {duration:.2f} s",
#             color="#ddd", fontsize=10, pad=8
#         )
#
#         # # ── Spectrogram ────────────────────────────────────────────────────
#         # ax_spec.set_facecolor("#0d0d0d")
#         # img = ax_spec.pcolormesh(
#         #     t, f / 1000, Sxx_db,
#         #     shading="gouraud",
#         #     cmap="inferno",
#         #     vmin=Sxx_db.max() - 80,
#         #     vmax=Sxx_db.max(),
#         # )
#         #
#         # cbar = self.fig.colorbar(img, ax=ax_spec, pad=0.01)
#         # cbar.set_label("dB", color="#aaa", fontsize=8)
#         # cbar.ax.yaxis.set_tick_params(color="#aaa", labelsize=7)
#         # for lbl in cbar.ax.get_yticklabels():
#         #     lbl.set_color("#aaa")
#         #
#         # ax_spec.set_xlim(0, t[-1])
#         # ax_spec.set_ylim(0, f[-1] / 1000)
#         # ax_spec.set_xlabel("Time (s)", color="#aaa", fontsize=9)
#         # ax_spec.set_ylabel("Frequency (kHz)", color="#aaa", fontsize=9)
#         # ax_spec.tick_params(colors="#aaa", labelsize=8)
#         # for spine in ax_spec.spines.values():
#         #     spine.set_edgecolor("#333")
#         # ax_spec.set_title("Spectrogram", color="#bbb", fontsize=9, pad=6)
#
#         self.fig.tight_layout(pad=1.5)
#         self.draw()
#
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("WAV Viewer — Waveform & Spectrogram")
#         self.resize(1100, 700)
#         self.setStyleSheet("background-color: #121212; color: #ddd;")
#         self.setAcceptDrops(True)
#
#         central = QWidget()
#         self.setCentralWidget(central)
#         layout = QVBoxLayout(central)
#         layout.setContentsMargins(12, 12, 12, 12)
#         layout.setSpacing(8)
#
#         # ── Toolbar ────────────────────────────────────────────────────────
#         toolbar = QHBoxLayout()
#
#         self.open_btn = QPushButton("Open WAV")
#         self.open_btn.setFixedHeight(34)
#         self.open_btn.setStyleSheet("""
#             QPushButton {
#                 background: #2a2a2a; color: #eee;
#                 border: 1px solid #444; border-radius: 6px;
#                 padding: 0 16px; font-size: 13px;
#             }
#             QPushButton:hover  { background: #3a3a3a; }
#             QPushButton:pressed{ background: #1a1a1a; }
#         """)
#         self.open_btn.clicked.connect(self.open_file)
#
#         self.info_label = QLabel("No file loaded")
#         self.info_label.setStyleSheet("color: #666; font-size: 12px;")
#
#         toolbar.addWidget(self.open_btn)
#         toolbar.addWidget(self.info_label)
#         toolbar.addStretch()
#         layout.addLayout(toolbar)
#
#         # ── Canvas ─────────────────────────────────────────────────────────
#         self.canvas = AudioCanvas(self)
#         layout.addWidget(self.canvas)
#
#     # ── File loading ───────────────────────────────────────────────────────
#     def open_file(self):
#         path, _ = QFileDialog.getOpenFileName(
#             self, "Open WAV File", "", "WAV Files (*.wav)"
#         )
#         if path:
#             self.load_file(path)
#
#     def load_file(self, path: str):
#         self.info_label.setText(f"Loading {Path(path).name} …")
#         QApplication.processEvents()
#         self.canvas.plot(path)
#         self.info_label.setText(f"Loaded: {Path(path).name}")
#
#     # ── Drag & drop ────────────────────────────────────────────────────────
#     def dragEnterEvent(self, event):
#         if event.mimeData().hasUrls():
#             if any(u.toLocalFile().lower().endswith(".wav")
#                    for u in event.mimeData().urls()):
#                 event.acceptProposedAction()
#                 return
#         event.ignore()
#
#     def dragMoveEvent(self, event):
#         if event.mimeData().hasUrls():
#             event.acceptProposedAction()
#
#     def dropEvent(self, event):
#         for url in event.mimeData().urls():
#             path = url.toLocalFile()
#             if path.lower().endswith(".wav"):
#                 self.load_file(path)
#                 break
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec())


import sys
import numpy as np
from pathlib import Path
from scipy.io import wavfile
import sounddevice as sd

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QScrollBar, QSizePolicy, QSlider
)
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF
from PySide6.QtGui import (
    QPainter, QPen, QColor, QBrush, QPainterPath, QFont, QLinearGradient
)


# ─────────────────────────────────────────────────────────────────────────────
#  Waveform Widget
# ─────────────────────────────────────────────────────────────────────────────
class WaveformWidget(QWidget):
    BG          = QColor("#1a1a1a")
    WAVE_TOP    = QColor("#1DB954")
    WAVE_BOT    = QColor("#158a3e")
    RMS_COLOR   = QColor(29, 185, 84, 80)
    CURSOR_CLR  = QColor("#ffffff")
    GRID_CLR    = QColor("#2a2a2a")
    RULER_BG    = QColor("#111111")
    RULER_TXT   = QColor("#888888")
    SEL_COLOR   = QColor(255, 255, 255, 25)

    RULER_H     = 24        # pixels for time ruler
    PADDING     = 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(120)

        # audio data
        self.samples     = None   # float32 numpy array, mono, [-1,1]
        self.sample_rate = 44100
        self.duration    = 0.0

        # view state
        self.view_start  = 0.0   # seconds visible at left edge
        self.zoom        = 1.0   # seconds per pixel  (lower = zoomed in)
        self._zoom_px    = 100   # pixels per second (inverse)

        # playback
        self.cursor_pos  = 0.0   # seconds

        # selection
        self.sel_start   = None
        self.sel_end     = None
        self._drag_start = None

        self.setMouseTracking(True)

    # ── public API ────────────────────────────────────────────────────────
    def load(self, samples, sample_rate):
        self.samples     = samples
        self.sample_rate = sample_rate
        self.duration    = len(samples) / sample_rate
        self.view_start  = 0.0
        self._zoom_px    = self.width() / self.duration   # fit whole file
        self.cursor_pos  = 0.0
        self.sel_start   = None
        self.sel_end     = None
        self.update()

    def set_cursor(self, seconds):
        self.cursor_pos = seconds
        # auto-scroll to keep cursor visible
        if self.samples is not None:
            visible_dur = self._visible_duration()
            if seconds < self.view_start or seconds > self.view_start + visible_dur:
                self.view_start = max(0, seconds - visible_dur * 0.3)
        self.update()

    def set_view_start(self, seconds):
        self.view_start = seconds
        self.update()

    def get_selection(self):
        if self.sel_start is not None and self.sel_end is not None:
            a, b = sorted([self.sel_start, self.sel_end])
            return a, b
        return None

    # ── geometry helpers ──────────────────────────────────────────────────
    def _wave_rect(self):
        """Rectangle for the waveform area (below ruler)."""
        return QRectF(0, self.RULER_H, self.width(), self.height() - self.RULER_H)

    def _visible_duration(self):
        return self.width() / self._zoom_px

    def _time_to_x(self, t):
        return (t - self.view_start) * self._zoom_px

    def _x_to_time(self, x):
        return x / self._zoom_px + self.view_start

    # ── painting ──────────────────────────────────────────────────────────
    def paintEvent(self, event):
        if self.width() == 0:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)

        wr = self._wave_rect()

        # background
        p.fillRect(self.rect(), self.BG)

        # grid
        self._draw_grid(p, wr)

        # selection
        if self.sel_start is not None and self.sel_end is not None:
            a, b = sorted([self.sel_start, self.sel_end])
            xa, xb = self._time_to_x(a), self._time_to_x(b)
            p.fillRect(QRectF(xa, wr.top(), xb - xa, wr.height()), self.SEL_COLOR)

        # waveform
        if self.samples is not None:
            self._draw_waveform(p, wr)

        # ruler
        self._draw_ruler(p)

        # cursor
        cx = self._time_to_x(self.cursor_pos)
        if 0 <= cx <= self.width():
            p.setPen(QPen(self.CURSOR_CLR, 1.5))
            p.drawLine(int(cx), self.RULER_H, int(cx), self.height())

        p.end()

    def _draw_grid(self, p, wr):
        vis = self._visible_duration()
        step = self._nice_step(vis / 8)
        t = (self.view_start // step) * step
        p.setPen(QPen(self.GRID_CLR, 1))
        while t <= self.view_start + vis:
            x = int(self._time_to_x(t))
            p.drawLine(x, int(wr.top()), x, int(wr.bottom()))
            t += step

    def _draw_ruler(self, p):
        p.fillRect(0, 0, self.width(), self.RULER_H, self.RULER_BG)
        vis   = self._visible_duration()
        step  = self._nice_step(vis / 8)
        t     = (self.view_start // step) * step
        font  = QFont("Monospace", 8)
        p.setFont(font)
        p.setPen(self.RULER_TXT)
        while t <= self.view_start + vis + step:
            x = int(self._time_to_x(t))
            p.drawLine(x, self.RULER_H - 6, x, self.RULER_H)
            label = self._format_time(t)
            p.drawText(x + 2, 4, 80, self.RULER_H - 4, Qt.AlignLeft | Qt.AlignVCenter, label)
            t += step

    def _draw_waveform(self, p, wr):
        w, h   = self.width(), int(wr.height())
        cy     = wr.center().y()
        half   = wr.height() / 2 - self.PADDING

        sr     = self.sample_rate
        t0     = max(0.0, self.view_start)
        t1     = min(self.duration, self.view_start + self._visible_duration())
        i0     = int(t0 * sr)
        i1     = min(len(self.samples), int(t1 * sr) + 1)

        if i1 <= i0:
            return

        chunk  = self.samples[i0:i1]
        pixels = max(1, int((t1 - t0) * self._zoom_px))
        bins   = np.array_split(chunk, min(pixels, len(chunk)))

        # RMS fill path (top + bottom symmetric)
        path_rms = QPainterPath()
        rms_top, rms_bot = [], []
        peak_top, peak_bot = [], []

        x_start = self._time_to_x(t0)

        for idx, b in enumerate(bins):
            if len(b) == 0:
                continue
            x  = x_start + idx * (pixels / len(bins)) if len(bins) > 1 else x_start
            pk = float(np.max(np.abs(b)))
            rm = float(np.sqrt(np.mean(b ** 2)))
            peak_top.append((x, cy - pk * half))
            peak_bot.append((x, cy + pk * half))
            rms_top.append((x, cy - rm * half))
            rms_bot.append((x, cy + rm * half))

        if not peak_top:
            return

        # draw peak (dark fill)
        peak_path = QPainterPath()
        peak_path.moveTo(*peak_top[0])
        for pt in peak_top[1:]:
            peak_path.lineTo(*pt)
        for pt in reversed(peak_bot):
            peak_path.lineTo(*pt)
        peak_path.closeSubpath()
        p.fillPath(peak_path, QColor("#0d5c28"))

        # draw RMS (bright fill)
        rms_path = QPainterPath()
        rms_path.moveTo(*rms_top[0])
        for pt in rms_top[1:]:
            rms_path.lineTo(*pt)
        for pt in reversed(rms_bot):
            rms_path.lineTo(*pt)
        rms_path.closeSubpath()
        p.fillPath(rms_path, QColor("#1DB954"))

        # center line
        p.setPen(QPen(QColor("#0a3d1a"), 1))
        p.drawLine(0, int(cy), self.width(), int(cy))

    # ── mouse ─────────────────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            t = self._x_to_time(event.position().x())
            self._drag_start = t
            self.sel_start   = t
            self.sel_end     = t
            self.cursor_pos  = t
            self.update()
            self.parentWidget().window().seek_to(t)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self._drag_start is not None:
            t = self._x_to_time(event.position().x())
            self.sel_end = t
            self.update()

    def mouseReleaseEvent(self, event):
        self._drag_start = None

    def wheelEvent(self, event):
        delta  = event.angleDelta().y()
        factor = 1.15 if delta > 0 else 1 / 1.15
        mouse_t = self._x_to_time(event.position().x())
        self._zoom_px = max(10, min(self._zoom_px * factor, 5000))
        # keep the point under the mouse fixed
        self.view_start = mouse_t - event.position().x() / self._zoom_px
        self.view_start = max(0, self.view_start)
        self.update()
        # update scrollbar
        self.parentWidget().window()._sync_scrollbar()

    def resizeEvent(self, event):
        super().resizeEvent(event)

    # ── helpers ───────────────────────────────────────────────────────────
    @staticmethod
    def _nice_step(approx):
        candidates = [0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5,
                      1, 2, 5, 10, 30, 60, 120, 300]
        return min(candidates, key=lambda x: abs(x - approx)) or 1

    @staticmethod
    def _format_time(t):
        if t < 60:
            return f"{t:.2f}s"
        m = int(t) // 60
        s = t - m * 60
        return f"{m}:{s:05.2f}"


# ─────────────────────────────────────────────────────────────────────────────
#  Main Window
# ─────────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audacity-style Waveform Viewer")
        self.resize(1200, 400)
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #1e1e1e; color: #ddd; }
            QPushButton {
                background: #2a2a2a; color: #eee;
                border: 1px solid #444; border-radius: 5px;
                padding: 4px 14px; font-size: 12px; min-height: 28px;
            }
            QPushButton:hover   { background: #363636; }
            QPushButton:pressed { background: #151515; }
            QPushButton:checked { background: #1a5c2e; border-color: #1DB954; }
            QScrollBar:horizontal {
                background: #111; height: 14px; border: none;
            }
            QScrollBar::handle:horizontal {
                background: #444; border-radius: 4px; min-width: 30px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
            QLabel { color: #aaa; font-size: 11px; }
            QSlider::groove:horizontal { background:#333; height:4px; border-radius:2px; }
            QSlider::handle:horizontal {
                background:#1DB954; width:12px; height:12px;
                margin:-4px 0; border-radius:6px;
            }
        """)

        # ── audio state ───────────────────────────────────────────────────
        self.samples     = None
        self.sample_rate = 44100
        self.duration    = 0.0
        self._play_start_sample = 0
        self._stream     = None
        self._play_pos   = 0        # current sample index during playback
        self._playing    = False

        # ── timer for cursor ──────────────────────────────────────────────
        self.timer = QTimer(self)
        self.timer.setInterval(30)   # ~33 fps
        self.timer.timeout.connect(self._tick)

        # ── UI ────────────────────────────────────────────────────────────
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # toolbar
        toolbar = QWidget()
        toolbar.setFixedHeight(48)
        toolbar.setStyleSheet("background:#111; border-bottom:1px solid #333;")
        tb_lay = QHBoxLayout(toolbar)
        tb_lay.setContentsMargins(8, 4, 8, 4)
        tb_lay.setSpacing(6)

        self.btn_open   = QPushButton("📂 Open")
        self.btn_play   = QPushButton("▶  Play")
        self.btn_pause  = QPushButton("⏸  Pause")
        self.btn_stop   = QPushButton("⏹  Stop")
        self.btn_zoom_in  = QPushButton("🔍+")
        self.btn_zoom_out = QPushButton("🔍−")
        self.btn_fit    = QPushButton("Fit")

        self.lbl_time   = QLabel("00:00.00 / 00:00.00")
        self.lbl_time.setStyleSheet("color:#1DB954; font-family:Monospace; font-size:13px;")

        # volume
        lbl_vol = QLabel("Vol:")
        self.sld_volume = QSlider(Qt.Horizontal)
        self.sld_volume.setRange(0, 100)
        self.sld_volume.setValue(80)
        self.sld_volume.setFixedWidth(90)

        for btn in [self.btn_open, self.btn_play, self.btn_pause,
                    self.btn_stop, self.btn_zoom_in, self.btn_zoom_out, self.btn_fit]:
            tb_lay.addWidget(btn)

        tb_lay.addWidget(self.lbl_time)
        tb_lay.addStretch()
        tb_lay.addWidget(lbl_vol)
        tb_lay.addWidget(self.sld_volume)

        root.addWidget(toolbar)

        # track label strip
        track_row = QWidget()
        track_row.setStyleSheet("background:#161616;")
        tr_lay = QHBoxLayout(track_row)
        tr_lay.setContentsMargins(0, 0, 0, 0)
        tr_lay.setSpacing(0)

        # left panel (track info)
        self.track_panel = QWidget()
        self.track_panel.setFixedWidth(160)
        self.track_panel.setStyleSheet("background:#111; border-right:1px solid #333;")
        tp_lay = QVBoxLayout(self.track_panel)
        tp_lay.setContentsMargins(8, 6, 8, 6)
        self.lbl_track_name = QLabel("No file")
        self.lbl_track_name.setStyleSheet("color:#ddd; font-size:11px; font-weight:bold;")
        self.lbl_track_info = QLabel("—")
        self.lbl_track_info.setStyleSheet("color:#666; font-size:10px;")
        tp_lay.addWidget(self.lbl_track_name)
        tp_lay.addWidget(self.lbl_track_info)
        tp_lay.addStretch()

        # waveform
        self.waveform = WaveformWidget()

        tr_lay.addWidget(self.track_panel)
        tr_lay.addWidget(self.waveform, 1)
        root.addWidget(track_row, 1)

        # scrollbar
        self.scrollbar = QScrollBar(Qt.Horizontal)
        self.scrollbar.setRange(0, 10000)
        self.scrollbar.setValue(0)
        self.scrollbar.valueChanged.connect(self._on_scroll)
        root.addWidget(self.scrollbar)

        # status
        self.status = QLabel("  Open a WAV file to begin.")
        self.status.setFixedHeight(22)
        self.status.setStyleSheet("background:#111; color:#555; font-size:11px;"
                                  "border-top:1px solid #2a2a2a; padding-left:6px;")
        root.addWidget(self.status)

        # ── connections ───────────────────────────────────────────────────
        self.btn_open.clicked.connect(self.open_file)
        self.btn_play.clicked.connect(self.play)
        self.btn_pause.clicked.connect(self.pause)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_zoom_in.clicked.connect(lambda: self._zoom(2.0))
        self.btn_zoom_out.clicked.connect(lambda: self._zoom(0.5))
        self.btn_fit.clicked.connect(self._fit)
        self.setAcceptDrops(True)

    # ── file loading ──────────────────────────────────────────────────────
    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open WAV", "", "WAV Files (*.wav)")
        if path:
            self.load_file(path)

    def load_file(self, path):
        self.stop()
        try:
            sr, data = wavfile.read(path)
        except Exception as e:
            self.status.setText(f"  Error: {e}")
            return

        if data.ndim == 2:
            data = data.mean(axis=1)
        data = data.astype(np.float32)
        peak = np.max(np.abs(data))
        if peak > 0:
            data /= peak

        self.samples     = data
        self.sample_rate = sr
        self.duration    = len(data) / sr

        self.waveform.load(data, sr)
        self._fit()
        self._sync_scrollbar()

        name = Path(path).name
        ch   = "Stereo" if data.ndim == 2 else "Mono"
        self.lbl_track_name.setText(name)
        self.lbl_track_info.setText(f"{sr} Hz · {self._fmt(self.duration)}")
        self.status.setText(f"  {path}")
        self._update_time_label()

    # ── playback ──────────────────────────────────────────────────────────
    def play(self):
        if self.samples is None:
            return
        if self._playing:
            return

        # start from cursor or selection start
        sel = self.waveform.get_selection()
        start_t = sel[0] if sel else self.waveform.cursor_pos
        self._play_pos = int(start_t * self.sample_rate)
        self._playing  = True

        vol = self.sld_volume.value() / 100.0
        chunk_size = 1024

        def callback(outdata, frames, time_info, status):
            if not self._playing:
                outdata[:] = 0
                raise sd.CallbackStop()
            end = self._play_pos + frames
            chunk = self.samples[self._play_pos:end]
            if len(chunk) < frames:
                outdata[:len(chunk), 0] = chunk * vol
                outdata[len(chunk):] = 0
                self._playing = False
                raise sd.CallbackStop()
            outdata[:, 0] = chunk * vol
            self._play_pos = end

        self._stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            blocksize=chunk_size,
            callback=callback,
            finished_callback=self._on_playback_finished,
        )
        self._stream.start()
        self.timer.start()

    def pause(self):
        if self._playing and self._stream:
            self._playing = False
            self._stream.stop()
            self.timer.stop()

    def stop(self):
        self._playing = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        self.timer.stop()
        self._play_pos = 0
        if self.samples is not None:
            self.waveform.set_cursor(0.0)
            self._update_time_label()

    def seek_to(self, t):
        if self.samples is None:
            return
        was_playing = self._playing
        if was_playing:
            self.pause()
        self._play_pos = int(np.clip(t, 0, self.duration) * self.sample_rate)
        self.waveform.set_cursor(t)
        self._update_time_label()
        if was_playing:
            self.play()

    def _on_playback_finished(self):
        self._playing = False
        self.timer.stop()

    def _tick(self):
        if self._playing and self.samples is not None:
            t = self._play_pos / self.sample_rate
            self.waveform.set_cursor(t)
            self._update_time_label()
            self._sync_scrollbar()

    # ── zoom / scroll ─────────────────────────────────────────────────────
    def _zoom(self, factor):
        self.waveform._zoom_px = max(10, min(self.waveform._zoom_px * factor, 5000))
        self.waveform.update()
        self._sync_scrollbar()

    def _fit(self):
        if self.duration > 0:
            self.waveform._zoom_px = self.waveform.width() / self.duration
            self.waveform.view_start = 0.0
            self.waveform.update()
            self._sync_scrollbar()

    def _sync_scrollbar(self):
        if self.duration == 0:
            return
        vis   = self.waveform._visible_duration()
        total = self.duration
        if vis >= total:
            self.scrollbar.setRange(0, 0)
            return
        max_val = int((total - vis) * 1000)
        self.scrollbar.blockSignals(True)
        self.scrollbar.setRange(0, max_val)
        self.scrollbar.setValue(int(self.waveform.view_start * 1000))
        self.scrollbar.setPageStep(int(vis * 1000))
        self.scrollbar.blockSignals(False)

    def _on_scroll(self, value):
        self.waveform.set_view_start(value / 1000.0)

    # ── helpers ───────────────────────────────────────────────────────────
    def _update_time_label(self):
        cur = self._play_pos / self.sample_rate if self.samples is not None else 0
        self.lbl_time.setText(f"{self._fmt(cur)} / {self._fmt(self.duration)}")

    @staticmethod
    def _fmt(t):
        m = int(t) // 60
        s = t - m * 60
        return f"{m:02d}:{s:05.2f}"

    # ── drag & drop ───────────────────────────────────────────────────────
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            if any(u.toLocalFile().lower().endswith(".wav")
                   for u in event.mimeData().urls()):
                event.acceptProposedAction()
                return
        event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            p = url.toLocalFile()
            if p.lower().endswith(".wav"):
                self.load_file(p)
                break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())