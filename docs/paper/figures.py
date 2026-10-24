from pathlib import Path

import librosa
import numpy as np
from matplotlib import pyplot as plt

from src.pymbrola import mbrola

path = Path("docs/paper/")
file = path / "kaffE1.wav"

phons = ["k", "a", "f", "f", "E1"]
durations = [100.0, 75, 200, 200, 300]
pitch = [
    50.0,
    [(0.0, 50.0), (0.5, 100), (0.75, 150), (0.9, 200)],
    400.0,
    300.0,
    250.0,
]
kaffE1 = mbrola.MBROLA(phon=phons, durations=durations, pitch=pitch)
kaffE1.to_sound(file, voice="it4")

# load audio
y, sr = librosa.load(file)

# get spectrogram
M = librosa.feature.melspectrogram(y=y, sr=sr)
S_db = librosa.amplitude_to_db(np.abs(M), ref=np.max)
times = librosa.times_like(S_db, sr=sr)

# get pitch contour
f0, voiced_flag, voiced_probs = librosa.pyin(
    y, sr=sr, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7")
)
times = librosa.times_like(f0, sr=sr)

# plot oscillogram and mel spectogram
fig, ax = plt.subplots(2, 1, height_ratios=(0.4, 0.6), figsize=(8, 6))

librosa.display.waveshow(y, sr=sr, ax=ax[0], color="k", linewidth=0.5)
ax[0].set_xticks([])
ax[0].set_ylabel("Amplitude")

img = librosa.display.specshow(
    S_db,
    x_axis="time",
    y_axis="mel",
    ax=ax[1],
    cmap_seq="gray_r",
    sr=sr,
)

ax[1].plot(
    times,
    f0,
    label="F0 (Pitch)",
    path_effects=librosa.display.highlight(ax=ax[1]),
    c="tab:red",
)
ax[1].legend(loc="upper right", frameon=False)
librosa.display.colorbar_db(img, location="bottom", shrink=0.5, pad=0.25)

fig.savefig(path / Path("kaffE1.png"), dpi=800)
