"""
Echo Hiding Steganography Module
=================================
This module hides data within FLAC audio files using echo hiding techniques.
The audio sounds normal to the human ear, but contains a hidden message.

Author: Student FYP (Jazzy)
Purpose: Covert communication mechanism.
"""

import numpy as np # type: ignore
import soundfile as sf # type: ignore
from typing import List, Dict, Any, cast
from scipy import signal # type: ignore
from scipy.fft import fft, ifft # type: ignore
import os


class EchoHiding:
    """
    This class handles the Echo Hiding technique.
    
    Concept:
    We introduce a small "echo" into the audio signal.
    - For binary '0', we apply a short delay echo.
    - For binary '1', we apply a slightly longer delay echo.
    
    The human ear typically cannot perceive this echo as it blends into the original audio,
    but it can be computationally detected.
    """
    
    def __init__(self, delay_0_ms=4.5, delay_1_ms=9.1, amplitude=0.8, decay=0.8, redundancy=5):
        """
        Initialise echo hiding parameters.
        Delays are specified in MILLISECONDS and converted to samples at runtime,
        so the algorithm works correctly regardless of audio sample rate (44.1kHz, 48kHz, etc).
        Signal strength is boosted to 0.8 to ensure data resilience against noise.
        """
        # Store delays in milliseconds - converted to samples per-file during embed/extract
        self.delay_0_ms = delay_0_ms  # ~4.5ms -> 200 samples @ 44.1kHz, 216 @ 48kHz
        self.delay_1_ms = delay_1_ms  # ~9.1ms -> 400 samples @ 44.1kHz, 436 @ 48kHz
        self.amplitude = amplitude
        self.decay = decay
        # Store redundancy level
        self.redundancy = redundancy
        self.SEGMENT_SIZE = 2048  # Optimal segment size balancing capacity and reliability.
        self.OFFSET_MS = 500  # Skip first 500ms of audio to avoid fade-in/silence
        # Minimum audio duration robustly required for embedding.
        self.MIN_AUDIO_DURATION = 17.0 

    def _get_delays(self, sample_rate: int):
        """ Convert millisecond delays to sample counts for a given sample rate. """
        delay_0 = max(10, int(self.delay_0_ms * sample_rate / 1000))
        delay_1 = max(20, int(self.delay_1_ms * sample_rate / 1000))
        offset_segments = max(1, int(self.OFFSET_MS * sample_rate / 1000 / self.SEGMENT_SIZE))
        return delay_0, delay_1, offset_segments
        
    def _detect_echo_delay(self, segment: np.ndarray, delay_0: int, delay_1: int) -> tuple:
        """ 
        Core logic - Detect echo using Cepstrum Analysis.
        Accepts actual sample-based delays so this works at any sample rate.
        Returns the detected bit (0/1) and the confidence level.
        """
        try:
            # 1. Normalize the volume of this segment
            max_seg = np.max(np.abs(segment))
            if max_seg > 0:
                segment = segment / max_seg
                
            # 2. Apply Hamming Window to smooth the signal
            windowed_segment = segment * np.hamming(len(segment))
            
            # 3. Apply Real Cepstrum phase to find echo peaks
            spectrum = fft(windowed_segment)
            log_spectrum = np.log(np.abs(spectrum) + 1e-10)
            cepstrum = ifft(log_spectrum).real
            
            # 4. Perform Peak Search for the echo
            window = 15 
            peak_0 = np.max(cepstrum[delay_0-window : delay_0+window])
            peak_1 = np.max(cepstrum[delay_1-window : delay_1+window])
            
            # Calculate confidence based on the peak difference against the noise floor
            local_noise = np.std(cepstrum[min(delay_0, delay_1)-20 : max(delay_0, delay_1)+20]) + 1e-10
            
            diff = abs(peak_0 - peak_1)
            confidence = min(1.0, (diff / local_noise) / 5.0)
            
            bit = 1 if peak_1 > peak_0 else 0
            return bit, confidence
        except Exception:
            return 0, 0.0
            
    def _text_to_binary(self, text: str) -> str:
        """ Converts text string into binary string (0/1) """
        binary = ''.join(format(ord(char), '08b') for char in text)
        binary += '1111111111111110' # End-of-message delimiter (0xFFFE)
        return binary

    def _binary_to_text(self, binary: str) -> str:
        """ Converts binary string back into text string """
        delimiter_pos = -1
        binary_str = str(binary)
        # 1. Try new 16-bit delimiter (0xFFFE)
        for i in range(0, len(binary_str) - 15, 8):
            if binary_str[i:i+16] == '1111111111111110':
                delimiter_pos = i
                break
        
        # 2. Fallback to legacy 8-bit delimiter (0xFF) if 16-bit not found
        if delimiter_pos == -1:
            for i in range(0, len(binary_str) - 7, 8):
                if binary_str[i:i+8] == '11111111':
                    delimiter_pos = i
                    break
        
        if delimiter_pos != -1:
            binary_str = binary_str[:delimiter_pos]
            found = True
            print(f"DEBUG: Delimiter found at bit {delimiter_pos}")
        else:
            found = False
            print("DEBUG: Delimiter NOT FOUND in binary stream")

        # Log first few bits for debugging
        print(f"DEBUG: Binary Start: {binary_str[:64]}...")

        text = ''
        for i in range(0, len(binary_str), 8):
            byte = binary_str[i:i+8]
            if len(byte) == 8:
                try:
                    b_int = int(byte, 2)
                    text += chr(b_int)
                except:
                    pass
        return text, found

    def _validate_extraction(self, text: str) -> bool:
        """
        Validate if extracted text looks like valid encrypted base64.
        """
        if not text or len(text) < 10:
            return False
        
        # Base64 contains only specific characters
        import re
        if not re.match(r'^[A-Za-z0-9+/=]+$', text):
            return False
            
        return True
    
    def _add_echo(self, audio: np.ndarray, delay: int) -> np.ndarray:
        """ Manually adds an echo to the audio array. """
        echo = np.zeros_like(audio)
        echo[delay:] = audio[:-delay] * self.amplitude * self.decay
        audio_with_echo = audio + echo
        max_val = np.max(np.abs(audio_with_echo))
        if max_val > 1.0:
            audio_with_echo = audio_with_echo / max_val
        return audio_with_echo
    
    def embed(self, audio_path: str, secret_text: str, output_path: str) -> dict:
        """
        Embed message with 3x Redundancy and Differential Echoes.
        Dynamically adjusts for short audio files and any audio sample rate.
        """
        try:
            audio, sample_rate = sf.read(audio_path)
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)

            # --- NEW: Audio Normalization ---
            # Boosts volume to 0.9 peak to ensure echoes are clear in quiet songs
            peak = np.max(np.abs(audio))
            if peak > 0 and peak < 0.5: # Only boost if it's noticeably quiet
                audio = audio * (0.9 / peak)
                print(f"DEBUG: Audio normalized (Peak: {peak:.4f} -> 0.9)")

            # Derive sample-rate-aware delays
            delay_0, delay_1, offset_segments = self._get_delays(sample_rate)

            # Validate minimum duration
            duration = len(audio) / sample_rate
            if duration < self.MIN_AUDIO_DURATION:
                return {
                    'status': 'error',
                    'message': f'Audio file too short ({duration:.1f}s). Minimum {self.MIN_AUDIO_DURATION}s required.'
                }

            binary_data = self._text_to_binary(secret_text)

            # --- Pre-processing ---
            # 1. Validate audio is not silent (e.g. failed YT download)
            peak = np.max(np.abs(audio))
            if peak < 1e-6:
                return {
                    'status': 'error',
                    'message': 'Audio file appears to be silent. Please check the file is valid.'
                }

            # 2. Normalize audio to consistent peak level before embedding.
            #    This ensures echo hiding works equally well on quiet AND loud songs.
            audio = audio / peak * 0.9
            stego_audio = audio.copy()
            # ---------------------

            redundant_bits = ''
            for bit in binary_data:
                redundant_bits += bit * self.redundancy

            num_bits = len(redundant_bits)
            required_samples = (num_bits + offset_segments) * self.SEGMENT_SIZE

            # For audio shorter than required, use single redundancy (no redundancy)
            actual_redundancy = self.redundancy
            if len(audio) < required_samples:
                # Rebuild with no redundancy for short audio
                actual_redundancy = 1
                redundant_bits = binary_data  # No duplication
                num_bits = len(redundant_bits)
                required_samples = (num_bits + offset_segments) * self.SEGMENT_SIZE

                if len(audio) < required_samples:
                    return {
                        'status': 'error',
                        'message': f'Audio too short. Need {required_samples/sample_rate:.1f}s, have {duration:.1f}s.' # type: ignore
                    }

            amp = self.amplitude * self.decay

            # Embed using Standard Positive Echoes (More stable)
            for i, bit in enumerate(cast(Any, redundant_bits)): # type: ignore
                start = (i + offset_segments) * self.SEGMENT_SIZE
                end = start + self.SEGMENT_SIZE
                segment_data = cast(Any, stego_audio)[start:end] # type: ignore

                delay = delay_1 if bit == '1' else delay_0

                # Calculate echo gain
                echo_gain = amp
                # Shift data for echo hiding
                shifted_data = np.zeros_like(cast(Any, segment_data))
                shifted_data[delay:] = cast(Any, segment_data)[:-delay]
                
                # Apply echo combining
                segment_data = segment_data + (echo_gain * shifted_data) # type: ignore
                stego_audio[start:end] = segment_data # type: ignore

            # Normalize volume to avoid clipping
            max_abs = np.max(np.abs(stego_audio))
            if max_abs > 1.0:
                stego_audio /= max_abs # type: ignore

            sf.write(output_path, stego_audio, sample_rate, format='FLAC')

            return {
                'status': 'success',
                'message': f'Embedding successful (Redundancy {actual_redundancy}x)',
                'bits_embedded': len(binary_data),
                'total_segments': num_bits,
                'characters_embedded': len(secret_text),
                'original_size_kb': os.path.getsize(audio_path) / 1024,
                'stego_size_kb': os.path.getsize(output_path) / 1024,
                'sample_rate': sample_rate,
                'audio_duration_sec': len(audio) / sample_rate,
                'segment_size': self.SEGMENT_SIZE
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _validate_extraction(self, text: str) -> bool:
        """
        Check if extracted text looks like valid Base64 data.
        This is crucial because we extracted AES-encrypted payloads.
        """
        if not text or len(text) < 10:
            return False
        
        # Base64 contains only specific characters
        import re
        if not re.match(r'^[A-Za-z0-9+/=]+$', text):
            return False
            
        # Base64 length should be reasonable for FYP use case
        # If it's thousands of characters, it's probably garbage from a long song
        if len(text) > 3000:
            return False
            
        return True
    
    def extract(self, stego_audio_path: str) -> dict:
        """ 
        Extraction with Auto-Redundancy Detection.
        Attempts 5x (High Stability) first, then falls back to 1x (High Capacity).
        """
        try:
            stego_audio, sample_rate = sf.read(stego_audio_path)
            if len(stego_audio.shape) > 1:
                stego_audio = np.mean(stego_audio, axis=1)

            # Derive sample-rate-aware delays
            delay_0, delay_1, offset_segments = self._get_delays(sample_rate)
            max_segments = len(stego_audio) // self.SEGMENT_SIZE

            # 1. First-pass: Extract raw bits from all available segments
            raw_bits = []
            raw_conf = []
            for i in range(offset_segments, max_segments):
                s = i * self.SEGMENT_SIZE
                e = s + self.SEGMENT_SIZE
                bit, conf = self._detect_echo_delay(stego_audio[s:e], delay_0, delay_1)
                raw_bits.append(bit)
                raw_conf.append(conf)

            # 2. Multi-Redundancy Attempt
            possible_redundancies = [self.redundancy, 1] # Usually [5, 1]
            best_result = None
            
            for red in possible_redundancies:
                if red > len(raw_bits): continue
                
                final_binary = ""
                confidences = []
                
                # Majority vote or direct bit extraction
                for i in range(0, len(raw_bits) - (red - 1), red):
                    chunk = raw_bits[i:i+red]
                    conf_chunk = raw_conf[i:i+red]
                    # Vote if red > 1, else direct bit
                    bit_vote = "1" if sum(chunk) > (red // 2) else "0"
                    final_binary += bit_vote
                    confidences.append(np.mean(conf_chunk))
                    
                    # Early break if delimiter found
                    if len(final_binary) % 8 == 0 and len(final_binary) >= 16:
                        if final_binary[-16:] == '1111111111111110':
                            break

                text, found = self._binary_to_text(final_binary)
                quality = np.mean(confidences) if confidences else 0
                
                res = {
                    'status': 'success',
                    'message': 'Extraction successful',
                    'secret_text': text,
                    'bits_extracted': len(final_binary),
                    'quality': float(quality),
                    'delimiter_found': found,
                    'detected_redundancy': red
                }
                
                if found:
                    return res
                
                if best_result is None or (found == False and len(text) > len(best_result['secret_text'])):
                    best_result = res
                    
            return best_result # Return best attempt even if EOM marker missing
            
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'secret_text': '', 'detected_redundancy': 0}


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("Echo Hiding Steganography Module - Test")
    print("=" * 60)
    
    # Note: This test requires a FLAC audio file
    # For demonstration, we'll create a synthetic audio signal
    
    print("\nCreating synthetic audio for testing...")
    
    # Generate 20 seconds of audio at 44100 Hz
    sample_rate = 44100
    duration = 20  # seconds
    t = np.linspace(0, duration, sample_rate * duration)
    
    # Create a simple tone (440 Hz - A note)
    frequency = 440
    audio = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # Save as FLAC
    test_audio_path = "test_audio.flac"
    sf.write(test_audio_path, audio, sample_rate, format='FLAC')
    print(f"✓ Created test audio: {test_audio_path}")
    
    # Initialize echo hiding
    echo = EchoHiding(delay_0_ms=4.5, delay_1_ms=9.1, amplitude=0.5, decay=0.5)
    
    # Secret message
    secret_message = "FYP Test"
    print(f"\nSecret Message: '{secret_message}'")
    
    # 1. Test standard 5x redundancy
    print("\n[Test 1] Standard 5x Redundancy...")
    stego_path_5x = "test_stego_5x.flac"
    echo_5x = EchoHiding(redundancy=5)
    echo_5x.embed(test_audio_path, secret_message, stego_path_5x)
    res_5x = echo_5x.extract(stego_path_5x)
    print(f"  - Extracted: '{res_5x['secret_text']}'")
    print(f"  - Redundancy Detected: {res_5x.get('detected_redundancy')}x")

    # 2. Test Cross-Redundancy (5x object extracting 1x file)
    print("\n[Test 2] Cross-Redundancy (5x Object -> 1x File)...")
    stego_path_1x = "test_stego_1x.flac"
    # Create 1x embedder manually
    echo_1x = EchoHiding(redundancy=1) 
    echo_1x.embed(test_audio_path, secret_message, stego_path_1x)
    
    # Extract with 5x extractor (default) - should fallback to 1x
    echo_default = EchoHiding() # redundancy 5
    res_1x = echo_default.extract(stego_path_1x)
    print(f"  - Extracted: '{res_1x['secret_text']}'")
    print(f"  - Redundancy Detected: {res_1x.get('detected_redundancy')}x")
    
    # Verify both
    if res_5x['secret_text'] == secret_message and res_1x['secret_text'] == secret_message:
        print("\n✓ Both redundancy levels verified successfully!")
    else:
        print("\n✗ Verification failed!")

    # Cleanup
    print("\nCleaning up test files...")
    for f in [test_audio_path, stego_path_5x, stego_path_1x]:
        if os.path.exists(f): os.remove(f)
    
    print("=" * 60)
