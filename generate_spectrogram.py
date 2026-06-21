import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def plot_spectrogram_comparison(clean_path, stego_path, output_filename="spectrogram_comparison_demo.png", auto_open=True, max_duration=10.0):
    print(f"[*] (Optimized) Loading first {max_duration}s of '{clean_path}'...")
    y_clean, sr = librosa.load(clean_path, sr=None, duration=max_duration)
    
    print(f"[*] (Optimized) Loading first {max_duration}s of '{stego_path}'...")
    y_stego, _ = librosa.load(stego_path, sr=sr, duration=max_duration)
    
    print("[*] Aligning audio file sizes...")
    # Ensure audio array sizes are equal before comparison
    min_len = min(len(y_clean), len(y_stego))
    y_clean = y_clean[:min_len]
    y_stego = y_stego[:min_len]
    
    print("[*] Converting audio to frequency domain (STFT)...")
    # Convert audio from time-domain to frequency domain (using STFT)
    D_clean = librosa.stft(y_clean)
    S_db_clean = librosa.amplitude_to_db(np.abs(D_clean), ref=np.max)
    
    D_stego = librosa.stft(y_stego)
    S_db_stego = librosa.amplitude_to_db(np.abs(D_stego), ref=np.max)
    
    # Get absolute FREQUENCY DIFFERENCE
    S_db_diff = S_db_stego - S_db_clean
    
    print("[*] Generating Spectrogram Graph...")
    fig, ax = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
    
    # Graph 1: Original Audio
    img1 = librosa.display.specshow(S_db_clean, sr=sr, x_axis='time', y_axis='log', ax=ax[0])
    ax[0].set_title('1. Original Cover Audio (No Message)', fontsize=14, pad=10)
    fig.colorbar(img1, ax=ax[0], format="%+2.0f dB")
    
    # Graph 2: Stego Audio
    img2 = librosa.display.specshow(S_db_stego, sr=sr, x_axis='time', y_axis='log', ax=ax[1])
    ax[1].set_title('2. Stego Audio (Contains Secret Message)', fontsize=14, pad=10)
    fig.colorbar(img2, ax=ax[1], format="%+2.0f dB")
    
    # Graph 3: Difference (Echo Hiding Visualization)
    # Frequency differences are usually subtle, so we use linear y_axis to see patterns
    img3 = librosa.display.specshow(S_db_diff, sr=sr, x_axis='time', y_axis='linear', ax=ax[2], cmap='coolwarm', vmin=-10, vmax=10)
    ax[2].set_title('3. Frequency Difference (Echo Hiding Algorithm Visualization)', fontsize=14, pad=10)
    fig.colorbar(img3, ax=ax[2], format="%+2.0f dB")
    
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n[SUCCESS] Spectrogram Graph has been successfully saved to '{output_filename}'")
    
    if auto_open:
        # Open image file directly after generation
        try:
            if sys.platform == "win32":
                os.startfile(output_filename)
            elif sys.platform == "darwin":
                os.system(f"open {output_filename}")
            else: # Linux
                os.system(f"xdg-open {output_filename}")
        except Exception as e:
            print(f"Please open '{output_filename}' manually in your folder.")

if __name__ == "__main__":
    # By default, use existing test file
    clean_audio = "Lorde - Royals (US Version).flac"
    stego_audio = "Lorde - Royals (US Version)_stego.flac"
    
    if not os.path.exists(clean_audio) or not os.path.exists(stego_audio):
        print(f"[ERROR] Failed to find files. Please ensure '{clean_audio}' and '{stego_audio}' exist in the folder.")
        sys.exit(1)
        
    plot_spectrogram_comparison(clean_audio, stego_audio)
