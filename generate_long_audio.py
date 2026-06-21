import numpy as np
import soundfile as sf
import os
import time

def generate_long_audio(filename="test_17.6s.flac", duration_sec=17.6, sr=44100):
    chunk_size_sec = min(120.0, duration_sec)
    num_chunks = max(1, int(duration_sec // chunk_size_sec))
    
    print(f"[*] Starting generation of {duration_sec} seconds of audio...")
    print(f"[*] Target filename: {filename}")
    print(f"[*] Sample rate: {sr} Hz")
    
    start_time = time.time()
    
    with sf.SoundFile(filename, mode='w', samplerate=sr, channels=1, format='FLAC') as f:
        for i in range(num_chunks):
            num_samples = int(sr * chunk_size_sec)
            white_noise = np.random.normal(0, 0.02, num_samples)
            
            t = np.linspace(i * chunk_size_sec, (i + 1) * chunk_size_sec, num_samples, endpoint=False)
            sine_wave = 0.01 * np.sin(2 * np.pi * 440 * t)
            
            chunk = white_noise + sine_wave
            
            max_val = np.max(np.abs(chunk))
            if max_val > 1.0:
                chunk /= max_val
            
            f.write(chunk)
            
            if (i + 1) % 5 == 0:
                elapsed = time.time() - start_time
                print(f"    [~] Written {i + 1}/{num_chunks} chunks... ({elapsed:.1f}s elapsed)")
    
    total_time = time.time() - start_time
    file_size_mb = os.path.getsize(filename) / (1024 * 1024)
    
    print("-" * 50)
    print(f"[✓] Generation complete!")
    print(f"[✓] File: {filename}")
    print(f"[✓] Size: {file_size_mb:.2f} MB")
    print(f"[✓] Duration: {duration_sec} seconds")
    print(f"[✓] Total time taken: {total_time:.1f} seconds")
    print("-" * 50)

if __name__ == "__main__":
    generate_long_audio()
