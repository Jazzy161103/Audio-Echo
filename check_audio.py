"""
Quick diagnostic: checks ALL flac files in Downloads to show their properties.
Run: python3 check_audio.py
"""
import soundfile as sf
import numpy as np
import glob
import os

files = sorted(glob.glob('/home/jazzy/Downloads/*.flac'))
print(f"{'File':<55} {'SR':>6} {'Ch':>3} {'Dur(s)':>8} {'RMS':>7} {'Peak':>7}")
print("-" * 95)
for path in files:
    try:
        info = sf.info(path)
        audio, sr = sf.read(path)
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)
        # Check first 2 seconds for silence
        first_2s = audio[:sr*2]
        rms = np.sqrt(np.mean(first_2s**2))
        peak = np.max(np.abs(first_2s))
        name = os.path.basename(path)[:54]
        print(f"{name:<55} {sr:>6} {info.channels:>3} {info.duration:>8.1f} {rms:>7.4f} {peak:>7.4f}")
    except Exception as e:
        print(f"{os.path.basename(path)}: ERROR - {e}")
