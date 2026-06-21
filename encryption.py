"""
Encryption Module - AES-256-CBC
===============================================
This module handles all aspect of security and cryptography in the steganography system.
We utilize the AES-256 standard (Cybersecurity grade) to keep secret messages secure.

Author: Student FYP
Purpose: Conceal and encrypt text before embedding into audio
"""

from Crypto.Cipher import AES # type: ignore
from Crypto.Protocol.KDF import PBKDF2 # type: ignore
from Crypto.Random import get_random_bytes # type: ignore
from Crypto.Hash import SHA256 # type: ignore
import base64


class AESEncryption:
    """
    This class handles all encryption operations.
    It uses the AES-256-CBC standard, providing strong security suitable for academic projects.
    Converts plain text into unreadable ciphertext.
    
    Key Features:
    - Uses PBKDF2 (mixes password with salt to prevent dictionary attacks)
    - CBC Mode (for enhanced security)
    - PKCS7 padding (pads blocks to required lengths)
    - Random IV (ensures fresh, unique results for every encryption)
    """
    
    def __init__(self, password: str):
        """
        Receive user password to generate the encryption key.
        """
        if len(password) < 12:
            raise ValueError("Password Policy: Password must be at least 12 characters long.")
        self.password = password
        # Salt to increase difficulty against dictionary and brute-force attacks
        self.salt = b'FYP_Stegano_2024'
        
    def _derive_key(self) -> bytes:
        """
        Converts the text password into a 32-bytes (256-bit) key.
        Utilizes PBKDF2 (Password-Based Key Derivation Function 2).
        Mixes the password with the salt iteratively to mitigate brute-force attacks.
        
        Input: User Password
        Output: 256-bit Secret Key
        """
        # Requires strong encryption, uses SHA-256 with 100k iterations
        key = PBKDF2(
            self.password, 
            self.salt, 
            dkLen=32,  # 32 bytes = 256 bits (standard AES definition)
            count=100000,  # 100,000 iterations for stronger defense
            hmac_hash_module=SHA256
        )
        return key
    
    def _pad(self, data: bytes) -> bytes:
        """
        AES requires data in blocks of 16 bytes.
        If data is less than 16 bytes, padding is required.
        Utilizes the PKCS7 padding standard.
        """
        # Calculate padding length to reach required block size
        padding_length = AES.block_size - (len(data) % AES.block_size)
        # Generate padding bytes
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _unpad(self, data: bytes) -> bytes:
        """
        Removes the padding following decryption.
        """
        # Retrieve the padding length from the last byte
        padding_length = data[-1] # type: ignore
        # Remove the padding bytes
        return data[:-padding_length] # type: ignore
    
    def encrypt(self, plaintext: str) -> str:
        """
        Main function to encrypt the secret message.
        
        Execution flow:
        1. Derive key from password 
        2. Generate random IV (ensures unique encryption instances)
        3. Pad message to 16 byte block lengths
        4. Encrypt using AES-CBC
        5. Concatenate IV and Ciphertext
        6. Encode into Base64 format (copy-pasteable text representation)
        """
        # 1. Derive the encryption key
        key = self._derive_key()
        
        # 2. Generate random Initialisation Vector (IV)
        iv = get_random_bytes(AES.block_size)
        
        # 3. Initialise encryption cipher (AES Mode CBC)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # 4. Encode text into bytes, apply padding
        plaintext_bytes = plaintext.encode('utf-8')
        padded_data = self._pad(plaintext_bytes)
        
        # 5. Encrypt padded data
        ciphertext = cipher.encrypt(padded_data)
        
        # 6. Prepend IV to Ciphertext (required for future decryption)
        encrypted_data = iv + ciphertext
        
        # 7. Encode to Base64 
        encrypted_base64 = base64.b64encode(encrypted_data).decode('utf-8')
        
        return encrypted_base64
    
    def decrypt(self, encrypted_base64: str) -> str:
        """
        Function reverses the encryption process.
        
        Execution flow:
        1. Decode Base64
        2. Separate IV (first 16 bytes) and Ciphertext
        3. Regenerate key (using the same password)
        4. Decrypt message using AES
        5. Remove padding
        6. Retrieve original message
        """
        try:
            # 1. Decode from Base64 into binary data
            encrypted_data = base64.b64decode(encrypted_base64)
            
            # 2. Extract IV (first 16 bytes)
            iv = encrypted_data[:AES.block_size] # type: ignore
            
            # 3. Extract Ciphertext (remaining bytes)
            ciphertext = encrypted_data[AES.block_size:] # type: ignore
            
            # 4. Derive key using user password
            key = self._derive_key()
            
            # 5. Initialise decryption cipher with extracted IV
            cipher = AES.new(key, AES.MODE_CBC, iv)
            
            # 6. Decrypt ciphertext message
            padded_plaintext = cipher.decrypt(ciphertext)
            
            # 7. Discard padding
            plaintext_bytes = self._unpad(padded_plaintext)
            
            # 8. Convert to string
            plaintext = plaintext_bytes.decode('utf-8')
            
            return plaintext
            
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("AES-256-CBC Encryption Module - Test")
    print("=" * 60)
    
    # Test password
    password = "MySecurePassword123!"
    
    # Create encryption handler
    aes = AESEncryption(password)
    
    # Test message
    secret_message = "This is a secret message for FYP demonstration."
    print(f"\nOriginal Message: {secret_message}")
    
    # Encrypt
    encrypted = aes.encrypt(secret_message)
    print(f"\nEncrypted (Base64): {encrypted}")
    print(f"Encrypted Length: {len(encrypted)} characters")
    
    # Decrypt
    decrypted = aes.decrypt(encrypted)
    print(f"\nDecrypted Message: {decrypted}")
    
    # Verify
    if secret_message == decrypted:
        print("\n✓ Encryption/Decryption successful!")
    else:
        print("\n✗ Encryption/Decryption failed!")
    
    # Test with wrong password
    print("\n" + "-" * 60)
    print("Testing with wrong password...")
    wrong_aes = AESEncryption("WrongPassword")
    try:
        wrong_decrypt = wrong_aes.decrypt(encrypted)
        print("✗ Security issue: Wrong password accepted!")
    except:
        print("✓ Correctly rejected wrong password")
    
    print("=" * 60)
