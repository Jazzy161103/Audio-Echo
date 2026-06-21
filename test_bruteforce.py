import sys
import os
import time
from security_evaluation import SecurityTester
from encryption import AESEncryption
from echo_hiding import EchoHiding

def load_wordlist(file_path):
    """Load passwords from a text file."""
    if not os.path.exists(file_path):
        print(f"[!] Wordlist file '{file_path}' not found!")
        return None
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        # Load and strip whitespace/newlines
        words = [line.strip() for line in f if line.strip()]
    return words

def main():
    tester = SecurityTester()
    echo = EchoHiding()
    
    # 1. Determine which wordlist to apply
    target_wordlist_file = "wordlist_10000.txt" # Default
    
    if len(sys.argv) > 1:
        target_wordlist_file = sys.argv[1]
        print(f"[*] Using custom wordlist: {target_wordlist_file}")
    else:
        print(f"[*] Using default wordlist: {target_wordlist_file}")
        print("[TIP] You can provide a custom wordlist: python3 test_bruteforce.py my_list.txt")

    wordlist = load_wordlist(target_wordlist_file)
    if not wordlist:
        # Fallback to hardcoded list if the file is missing
        print("[!] Using temporary mini-wordlist...")
        wordlist = ["adminadmin123", "123456789012", "sayangsayang", "jazzyjazzy12", "password1234"]

    # Generate an adequate length (30s) synthetic audio signal
    cover_file = "clean_test_audio.flac"
    if not os.path.exists(cover_file):
        print(f"[*] Generating 30s synthetic audio...")
        import numpy as np
        import soundfile as sf
        sr = 44100
        t = np.linspace(0, 30, sr * 30)
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)
        sf.write(cover_file, audio, sr, format='FLAC')
        
    stego_file = "brute_test_stego.flac"
    
    # Secret password for testing (Must be exactly matched in the wordlist to simulate "success")
    # We retrieve one securely from the wordlist
    weak_password = "password1234" 
    if "password1234" not in wordlist and len(wordlist) > 0:
        weak_password = wordlist[min(5, len(wordlist)-1)] # Sample from the list
        
    message = "SECRET_123"
    
    print(f"\n[*] Secret system password: '{weak_password}'")
    
    # Encrypt & Embed
    aes_weak = AESEncryption(weak_password)
    ciphertext = aes_weak.encrypt(message)
    
    res = echo.embed(cover_file, ciphertext, stego_file)
    if res['status'] == 'error':
        print(f"[!] Embedding failed: {res['message']}")
        return
    
    print(f"\n>>> ADVERSARY SIMULATION STARTED <<<")
    print(f"Adversary is substituting {len(wordlist)} passwords from '{target_wordlist_file}'...")
    
    # Run simulation
    tester.brute_force_simulation(stego_file, wordlist)
    
    # Cleanup
    if os.path.exists(stego_file):
        os.remove(stego_file)

    print("\n[CONCLUSION]")
    print(f"Brute force attacks fundamentally depend on the wordlist '{target_wordlist_file}'.")
    print("If the user's password is absent from the wordlist, the Adversary cannot compromise the system.")

if __name__ == "__main__":
    main()
