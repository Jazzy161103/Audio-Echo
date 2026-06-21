import os
import time
import hashlib
import numpy as np # type: ignore
import soundfile as sf # type: ignore
import librosa # type: ignore
from scipy import signal # type: ignore
import binascii
from encryption import AESEncryption # type: ignore
from echo_hiding import EchoHiding # type: ignore

class SecurityTester:
    def __init__(self):
        self.echo = EchoHiding()
        
    def brute_force_simulation(self, stego_path, wordlist):
        """
        Simulate a brute force attack to attempt guessing the encryption password.
        """
        print("\n" + "="*50)
        print(" PHASE 1: CRYPTOGRAPHIC BRUTE FORCE ATTACK")
        print("="*50)
        
        # 1. Extract the hidden payload first
        print(f"[*] Extracting hidden payload from: {os.path.basename(stego_path)}")
        result = self.echo.extract(stego_path)
        
        if result['status'] != 'success':
            print(f"[!] Extraction failed: {result['message']}")
            return
            
        ciphertext = result['secret_text']
        print(f"[*] Payload intercepted (Base64): {ciphertext[:20]}...")
        print(f"[*] Starting brute force search using {len(wordlist)} passwords...")
        
        start_time = time.time()
        found_pass = None
        decoded_msg = None
        
        for i, password in enumerate(wordlist):
            if i % 10 == 0:
                print(f"    [~] Testing attempt {i+1}/{len(wordlist)}: '{password}'")
            
            try:
                aes = AESEncryption(password)
                decoded_msg = aes.decrypt(ciphertext)
                
                # Discard empty results - False positive protection
                if decoded_msg and len(decoded_msg) > 0:
                    found_pass = password
                    break
                else:
                    continue # Empty msg usually means wrong padding/password
            except (ValueError, UnicodeDecodeError):
                continue # Incorrect password, continue attempting
                
        duration = time.time() - start_time
        
        print("-" * 50)
        if found_pass:
            print(f"[!] ATTACK SUCCESSFUL!")
            print(f"[!] Password Found: {found_pass}")
            print(f"[!] Decrypted Content: {decoded_msg}")
        else:
            print("[✓] ATTACK FAILED: All passwords in wordlist rejected.")
            print("[✓] CONCLUSION: System resistant to provided wordlist.")
            
        print(f"[*] Attack Duration: {duration:.2f} seconds")
        print("="*50 + "\n")

    def signal_attack_noise(self, input_path, output_path, noise_factor=0.005):
        """
        Applies Additive White Gaussian Noise (AWGN) to the audio.
        Tests the robustness of our echo bitstream.
        """
        print(f"[*] Applying Signal Attack: AWGN (Noise Level: {noise_factor})")
        audio, sr = sf.read(input_path)
        
        # Superimpose AWGN
        noise = np.random.randn(*audio.shape) * noise_factor
        attacked_audio = audio + noise
        
        sf.write(output_path, attacked_audio, sr, format='FLAC')
        print(f"[*] Attacked file saved to: {output_path}")
        
    def signal_attack_resample(self, input_path, output_path, target_sr=16000):
        """
        Resampling Attack: Downgrade and then upsample audio.
        Simulates audio transmission compression (e.g. via messaging apps).
        """
        print(f"[*] Applying Signal Attack: Resampling (Target: {target_sr}Hz)")
        audio, sr = librosa.load(input_path, sr=None)
        
        # Downsample
        audio_low = librosa.resample(y=audio, orig_sr=sr, target_sr=target_sr)
        # Upsample back to original
        audio_final = librosa.resample(y=audio_low, orig_sr=target_sr, target_sr=sr)
        
        sf.write(output_path, audio_final, sr, format='FLAC')
        print(f"[*] Attacked file saved to: {output_path}")

    def signal_attack_lowpass(self, input_path, output_path, cutoff=4000):
        """
        Low-Pass Filter Attack: Removes high frequencies.
        Tests if embedded echoes survive filtering.
        """
        print(f"[*] Applying Signal Attack: Low-pass Filter (Cutoff: {cutoff}Hz)")
        audio, sr = sf.read(input_path)
        
        # Design Butterworth filter
        nyquist = 0.5 * sr
        normal_cutoff = cutoff / nyquist
        b, a = signal.butter(5, normal_cutoff, btype='low', analog=False)
        
        # Apply filter
        attacked_audio = signal.lfilter(b, a, audio)
        
        sf.write(output_path, attacked_audio, sr, format='FLAC')
        print(f"[*] Attacked file saved to: {output_path}")

    def calculate_ber(self, original_text, extracted_text):
        """
        Calculates Bit Error Rate between original and extracted text.
        """
        def text_to_bits(text):
            return ''.join(format(ord(c), '08b') for c in text)
            
        orig_bits = text_to_bits(original_text)
        extr_bits = text_to_bits(extracted_text)
        
        # Align lengths
        min_len = min(len(orig_bits), len(extr_bits))
        max_len = max(len(orig_bits), len(extr_bits))
        
        errors = sum(1 for i in range(min_len) if orig_bits[i] != extr_bits[i])
        errors += (max_len - min_len) # Extra bits are also errors
        
        ber = (errors / max_len) * 100 if max_len > 0 else 0
        return ber

    def calculate_metrics(self, original_path, stego_path):
        """
        Calculates SNR and MSE between original and stego audio.
        """
        print(f"[*] Calculating Metrics: {os.path.basename(original_path)} vs {os.path.basename(stego_path)}")
        original, sr1 = sf.read(original_path)
        stego, sr2 = sf.read(stego_path)
        
        # Assure identical duration and mono channels
        if len(original.shape) > 1: original = np.mean(original, axis=1)
        if len(stego.shape) > 1: stego = np.mean(stego, axis=1)
        
        min_len = min(len(original), len(stego))
        original = original[:min_len]
        stego = stego[:min_len]
        
        # MSE
        mse = np.mean((original - stego)**2)
        
        # SNR
        signal_power = np.mean(original**2)
        noise_power = np.mean((original - stego)**2)
        
        if noise_power == 0:
            snr = 100 # Infinity
        else:
            snr = 10 * np.log10(signal_power / noise_power)
            
        return {"snr": snr, "mse": mse}

    def run_integrity_test(self, original_text, extracted_text):
        """
        Verify integrity using SHA256 hashing. Strict comparison.
        """
        print(f"[*] Starting Integrity Test (Strict Comparison)")
        
        orig_hash = hashlib.sha256(original_text.encode()).hexdigest()
        extr_hash = hashlib.sha256(extracted_text.encode()).hexdigest()
        
        match = (orig_hash == extr_hash)
        
        print(f"    - Original Hash: {orig_hash[:16]}...") # type: ignore
        print(f"    - Extracted Hash: {extr_hash[:16]}...") # type: ignore
        
        if match:
            print("[✓] INTEGRITY VERIFIED: Hashes match 100%.")
        else:
            print("[✗] INTEGRITY FAILED: Message corruption detected.")
            
        return match

    def run_hex_analysis(self, original_path, stego_path):
        """
        Performs Hex analysis on the files.
        Checks for:
        1. Magic Number (Signature)
        2. File Size anomalies
        3. Appended data at EOF
        """
        print(f"[*] Starting Hex Analysis Validity Test")
        
        with open(original_path, 'rb') as f1, open(stego_path, 'rb') as f2:
            orig_bytes = f1.read()
            stego_bytes = f2.read()
            
        # 1. Check Magic Number (FLAC signature)
        flac_signature = b'fLaC'
        if stego_bytes[:4] == flac_signature: # type: ignore
            print(f"    [✓] Signature Check: Valid FLAC header detected.")
        else:
            print(f"    [✗] Signature Check: INVALID HEADER. File might be corrupted.")

        # 2. Compare file sizes
        orig_size = len(orig_bytes)
        stego_size = len(stego_bytes)
        diff = stego_size - orig_size
        
        print(f"    - Original Size: {orig_size} bytes")
        print(f"    - Stego Size:    {stego_size} bytes")
        
        if diff == 0:
            print(f"    - Size Difference: 0 bytes (Perfectly cloaked size)")
        elif diff > 0:
            print(f"    - Size Difference: +{diff} bytes (Suspicious if too large)")
        else:
            print(f"    - Size Difference: {diff} bytes (File compressed?)")

        # 3. Verify EOF for appended data (Last 16 bytes)
        orig_tail = binascii.hexlify(orig_bytes[-16:]).decode() # type: ignore
        stego_tail = binascii.hexlify(stego_bytes[-16:]).decode() # type: ignore
        
        if orig_tail == stego_tail:
            print(f"    [✓] Tail Consistency: Last 16 bytes are identical. No simple appends.")
        else:
            print(f"    [!] Tail Difference: Stego tail differs. Check for metadata changes.")
            print(f"      - Orig Tail (Hex): {orig_tail}")
            print(f"      - Stego Tail (Hex): {stego_tail}")

        return True

def run_demo():
    tester = SecurityTester()
    echo = EchoHiding()
    
    cover_file = "test_audio.flac"
    stego_file = "test_stego.flac"
    secret_text = "FYP_SECURITY_TEST_2024"
    
    print("\n" + "="*50)
    print(" COMPREHENSIVE SECURITY EVALUATION DEMO")
    print("="*50)
    
    # 1. Setup clean test files
    if not os.path.exists(cover_file):
        # Create synthetic audio if missing (Need at least 17s for EchoHiding)
        print("[*] Creating synthetic 20s test audio...")
        sr = 44100
        t = np.linspace(0, 20, sr * 20)
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)
        sf.write(cover_file, audio, sr, format='FLAC')
    
    print(f"[*] Embedding secret message: '{secret_text}'")
    embed_res = echo.embed(cover_file, secret_text, stego_file)
    if embed_res['status'] != 'success':
        print(f"[✗] Embedding failed: {embed_res['message']}")
        return
    
    # 2. Perceptual Quality Check
    metrics = tester.calculate_metrics(cover_file, stego_file)
    print(f"[✓] METRICS:")
    print(f"    - SNR: {metrics['snr']:.2f} dB (Higher is better)")
    print(f"    - MSE: {metrics['mse']:.8e} (Lower is better)")
    
    # 3. Check Integrity (SHA256)
    print("\n" + "-"*50)
    print(" PHASE 0: MESSAGE INTEGRITY VERIFICATION")
    print("-"*50)
    extract_res = echo.extract(stego_file)
    tester.run_integrity_test(secret_text, extract_res['secret_text'])
    
    # 4. Cryptography Check
    passwords = ["123", "password", "FYP_SECURITY_TEST_2024", "JazzyKey"]
    tester.brute_force_simulation(stego_file, passwords)
    
    # 4. Robustness Check: Noise
    noise_file = "attacked_noise.flac"
    tester.signal_attack_noise(stego_file, noise_file)
    res = echo.extract(noise_file)
    ber = tester.calculate_ber(secret_text, res['secret_text'])
    print(f"[*] NOISE ATTACK RESULT: BER = {ber:.2f}%")
    
    # 5. Robustness Check: Low-pass
    lp_file = "attacked_lowpass.flac"
    tester.signal_attack_lowpass(stego_file, lp_file)
    res = echo.extract(lp_file)
    ber = tester.calculate_ber(secret_text, res['secret_text'])
    print(f"[*] LOW-PASS ATTACK RESULT: BER = {ber:.2f}%")
    
    # 6. Hex Analysis
    print("\n" + "-"*50)
    print(" PHASE 2: HEX ANALYSIS & VALIDITY")
    print("-"*50)
    tester.run_hex_analysis(cover_file, stego_file)

if __name__ == "__main__":
    run_demo()
