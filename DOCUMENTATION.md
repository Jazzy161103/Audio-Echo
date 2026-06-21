# System Architecture & Documentation
## Secure Audio Steganography System

---

## 1. SYSTEM ARCHITECTURE

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                     (Tkinter GUI - gui.py)                       │
│  - File selection dialogs                                        │
│  - Message input/output                                          │
│  - Password management                                           │
│  - Status updates & results display                              │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ User Actions
                 │
        ┌────────┴────────┬────────────────┬─────────────────┐
        │                 │                │                 │
        ▼                 ▼                ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐
│  Encryption  │  │ Echo Hiding  │  │     CNN      │  │  Utils   │
│    Module    │  │    Module    │  │   Analysis   │  │          │
│              │  │              │  │    Module    │  │          │
│ encryption.py│  │echo_hiding.py│  │cnn_analysis  │  │          │
│              │  │              │  │     .py      │  │          │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────┘
```

### 1.2 Data Flow

#### Embedding Process:
```
1. User Input (GUI)
   ↓
2. Plaintext Message
   ↓
3. AES-256-CBC Encryption (encryption.py)
   ↓
4. Encrypted Ciphertext (Base64)
   ↓
5. Binary Conversion
   ↓
6. Echo Hiding Embedding (echo_hiding.py)
   ↓
7. Stego Audio File (FLAC)
```

#### Extraction Process:
```
1. Stego Audio File (FLAC)
   ↓
2. Echo Detection (echo_hiding.py)
   ↓
3. Binary Data Extraction
   ↓
4. Encrypted Ciphertext (Base64)
   ↓
5. AES-256-CBC Decryption (encryption.py)
   ↓
6. Plaintext Message
   ↓
7. Display to User (GUI)
```

---

## 2. MODULE DESCRIPTIONS

### 2.1 Encryption Module (`encryption.py`)

**Purpose**: Provides cryptographic security for secret messages

**Key Components**:
- **AESEncryption Class**: Main encryption handler
- **Key Derivation**: PBKDF2 with SHA-256 (100,000 iterations)
- **Encryption Mode**: AES-256-CBC
- **Padding**: PKCS7
- **Encoding**: Base64 for text compatibility

**Security Features**:
- 256-bit encryption key
- Random IV for each encryption
- Salt-based key derivation
- Secure padding scheme

**Methods**:
- `encrypt(plaintext)`: Encrypts plaintext message
- `decrypt(ciphertext)`: Decrypts encrypted message
- `_derive_key()`: Derives encryption key from password
- `_pad()` / `_unpad()`: PKCS7 padding operations

**Example Usage**:
```python
from encryption import AESEncryption

aes = AESEncryption("MyPassword123")
encrypted = aes.encrypt("Secret message")
decrypted = aes.decrypt(encrypted)
```

---

### 2.2 Echo Hiding Module (`echo_hiding.py`)

**Purpose**: Embeds encrypted data into audio using echo patterns

**Key Components**:
- **EchoHiding Class**: Main steganography handler
- **Echo Parameters**:
  - `delay_0`: 200 samples (binary '0')
  - `delay_1`: 400 samples (binary '1')
  - `amplitude`: 0.5 (echo strength)
  - `decay`: 0.5 (echo decay rate)

**Technique**:
- Uses imperceptible echoes to encode binary data
- Different delays represent different bit values
- Autocorrelation for echo detection during extraction

**Methods**:
- `embed(audio_path, secret_text, output_path)`: Embeds message
- `extract(stego_audio_path)`: Extracts message
- `_add_echo()`: Adds echo to audio segment
- `_detect_echo_delay()`: Detects echo using autocorrelation
- `_text_to_binary()` / `_binary_to_text()`: Conversion utilities

**Audio Processing**:
- Format: FLAC (lossless)
- Mono conversion for stereo files
- Normalization to prevent clipping
- Segment-based embedding

**Example Usage**:
```python
from echo_hiding import EchoHiding

echo = EchoHiding()
result = echo.embed("input.flac", "encrypted_data", "output.flac")
extracted = echo.extract("output.flac")
```

---

### 2.3 CNN Analysis Module (`cnn_analysis.py`)

**Purpose**: Evaluates detection resistance using deep learning

**Key Components**:
- **CNNSteganalysis Class**: CNN-based analyzer
- **Input**: Mel-spectrograms (128 mel bands)
- **Output**: Binary classification (Original/Stego)

**CNN Architecture**:
```
Input: Mel-spectrogram (128 x time_steps x 1)
    ↓
Conv2D (32 filters, 3x3) + ReLU
    ↓
MaxPooling2D (2x2)
    ↓
Conv2D (64 filters, 3x3) + ReLU
    ↓
MaxPooling2D (2x2)
    ↓
Conv2D (128 filters, 3x3) + ReLU
    ↓
MaxPooling2D (2x2)
    ↓
Flatten
    ↓
Dense (128 units) + ReLU + Dropout(0.5)
    ↓
Dense (1 unit) + Sigmoid
    ↓
Output: Probability [0, 1]
```

**Features**:
- Mel-spectrogram conversion
- Data augmentation support
- Training with early stopping
- Performance metrics (accuracy, confusion matrix)
- Visualization tools

**Methods**:
- `prepare_dataset()`: Prepares training data
- `build_model()`: Constructs CNN architecture
- `train()`: Trains the model
- `evaluate()`: Evaluates performance
- `plot_training_history()`: Visualizes training
- `plot_confusion_matrix()`: Visualizes results

**Example Usage**:
```python
from cnn_analysis import CNNSteganalysis

cnn = CNNSteganalysis()
X_train, X_test, y_train, y_test = cnn.prepare_dataset(
    original_files=['orig1.flac', 'orig2.flac'],
    stego_files=['stego1.flac', 'stego2.flac']
)
cnn.build_model(input_shape=X_train.shape[1:])
cnn.train(X_train, y_train, X_test, y_test, epochs=20)
results = cnn.evaluate(X_test, y_test)
```

---

### 2.4 GUI Module (`gui.py`)

**Purpose**: User-friendly interface for all operations

**Key Components**:
- **SteganographyGUI Class**: Main GUI handler
- **Tabs**:
  - Embed Message
  - Extract Message

**Features**:
- File selection dialogs (FLAC files)
- Text input/output areas
- Password fields (masked)
- Real-time status updates
- Results display
- Threading for non-blocking operations

**Design**:
- Clean, professional layout
- Color-coded feedback (success/error)
- Responsive interface
- Error handling with user-friendly messages

**User Workflow**:

**Embedding**:
1. Select audio file (FLAC)
2. Enter secret message
3. Enter encryption password
4. Click "Encrypt & Embed Message"
5. View results and output file location

**Extraction**:
1. Select stego audio file (FLAC)
2. Enter decryption password
3. Click "Extract & Decrypt Message"
4. View extracted message and results

---

## 3. TECHNICAL SPECIFICATIONS

### 3.1 Cryptography

**Algorithm**: AES (Advanced Encryption Standard)
- **Key Size**: 256 bits
- **Mode**: CBC (Cipher Block Chaining)
- **IV**: 128 bits (random, unique per encryption)
- **Key Derivation**: PBKDF2-HMAC-SHA256
  - Iterations: 100,000
  - Salt: Fixed (16 bytes)
  - Output: 32 bytes (256 bits)
- **Padding**: PKCS7
- **Encoding**: Base64

### 3.2 Steganography

**Technique**: Echo Hiding
- **Carrier**: FLAC audio (lossless)
- **Embedding Method**: Echo patterns
- **Binary Encoding**:
  - '0' → Echo delay of 200 samples
  - '1' → Echo delay of 400 samples
- **Echo Parameters**:
  - Amplitude: 0.5
  - Decay: 0.5
- **Detection**: Autocorrelation analysis
- **Capacity**: Depends on audio length
  - Formula: `max_bits = audio_length / (max_delay * 2)`

### 3.3 Deep Learning

**Model**: Convolutional Neural Network (CNN)
- **Framework**: TensorFlow/Keras
- **Input**: Mel-spectrogram
  - Mel bands: 128
  - FFT size: 2048
  - Hop length: 512
- **Architecture**:
  - 3 Convolutional blocks
  - 1 Dense layer (128 units)
  - Dropout: 0.5
  - Output: Sigmoid activation
- **Training**:
  - Optimizer: Adam
  - Loss: Binary crossentropy
  - Metrics: Accuracy
  - Early stopping: Patience 5
- **Evaluation**:
  - Accuracy score
  - Confusion matrix
  - Classification report

### 3.4 Audio Processing

**Format**: FLAC (Free Lossless Audio Codec)
- **Advantages**:
  - Lossless compression
  - Preserves audio quality
  - Suitable for steganography
- **Sample Rate**: Preserved from original
- **Channels**: Converted to mono if stereo
- **Bit Depth**: Preserved from original

---

## 4. SECURITY ANALYSIS

### 4.1 Encryption Security

**Strengths**:
- AES-256 is military-grade encryption
- PBKDF2 prevents brute-force attacks
- Random IV prevents pattern analysis
- CBC mode provides semantic security

**Considerations**:
- Password strength is critical
- Salt is fixed (should be random in production)
- Key derivation is computationally expensive (intentional)

### 4.2 Steganography Security

**Imperceptibility**:
- Echo delays are below human perception threshold
- Amplitude is carefully tuned
- Changes are subtle and distributed

**Robustness**:
- Works with lossless format (FLAC)
- Vulnerable to lossy compression (MP3, AAC)
- Vulnerable to audio modifications

**Detection Resistance**:
- Evaluated using CNN
- Statistical analysis possible
- Not resistant to advanced steganalysis

### 4.3 System Security

**Strengths**:
- End-to-end encryption
- No key storage (password-based)
- Local processing (no network)

**Limitations**:
- Password must be shared securely
- No authentication mechanism
- No integrity checking (MAC)

---

## 5. PERFORMANCE METRICS

### 5.1 Audio Quality

**Metrics**:
- **SNR (Signal-to-Noise Ratio)**: Measures imperceptibility
- **PSNR (Peak SNR)**: Audio quality metric
- **Perceptual Quality**: Human listening tests

**Expected Results**:
- High SNR (>30 dB)
- Imperceptible to human ear
- Minimal file size increase

### 5.2 CNN Performance

**Metrics**:
- **Accuracy**: Overall classification accuracy
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1-Score**: Harmonic mean of precision and recall

**Interpretation**:
- High accuracy → Easy to detect (less secure)
- Low accuracy → Hard to detect (more secure)
- Goal: Evaluate, not attack

### 5.3 Capacity

**Formula**:
```
Capacity (bits) = Audio_Length_Samples / (Max_Delay * 2)
```

**Example**:
- Audio: 5 seconds at 44100 Hz = 220,500 samples
- Max delay: 400 samples
- Capacity: 220,500 / 800 = 275 bits = 34 characters

---

## 6. USAGE GUIDE

### 6.1 Installation

```bash
# Clone or download the project
cd "Stegano Test 2Fyp"

# Install dependencies
pip install -r requirements.txt
```

### 6.2 Running the Application

```bash
# Launch GUI
python main.py
```

### 6.3 Embedding a Message

1. Click "Embed Message" tab
2. Click "Browse" to select a FLAC audio file
3. Type your secret message in the text area
4. Enter a strong password
5. Click "Encrypt & Embed Message"
6. Wait for completion
7. Note the output file location

### 6.4 Extracting a Message

1. Click "Extract Message" tab
2. Click "Browse" to select the stego FLAC file
3. Enter the same password used for embedding
4. Click "Extract & Decrypt Message"
5. View the extracted message

### 6.5 CNN Analysis (Advanced)

```python
from cnn_analysis import CNNSteganalysis

# Initialize
cnn = CNNSteganalysis()

# Prepare dataset
original_files = ['audio1.flac', 'audio2.flac', ...]
stego_files = ['stego1.flac', 'stego2.flac', ...]

X_train, X_test, y_train, y_test = cnn.prepare_dataset(
    original_files, stego_files
)

# Build and train
cnn.build_model(input_shape=X_train.shape[1:])
cnn.train(X_train, y_train, X_test, y_test, epochs=20)

# Evaluate
results = cnn.evaluate(X_test, y_test)

# Visualize
cnn.plot_training_history(save_path='training.png')
cnn.plot_confusion_matrix(results['confusion_matrix'], 
                          save_path='confusion.png')
```

---

## 7. TROUBLESHOOTING

### 7.1 Common Issues

**Issue**: "Module not found" error
- **Solution**: Install dependencies: `pip install -r requirements.txt`

**Issue**: "Audio file too short for message length"
- **Solution**: Use shorter message or longer audio file

**Issue**: "Decryption failed: Wrong password"
- **Solution**: Ensure you're using the exact same password

**Issue**: GUI doesn't open
- **Solution**: Check tkinter installation (comes with Python)

### 7.2 File Format Issues

**Issue**: "Unsupported audio format"
- **Solution**: Convert audio to FLAC format using:
  ```bash
  ffmpeg -i input.mp3 output.flac
  ```

**Issue**: Stego file is corrupted
- **Solution**: Ensure original file is valid FLAC, not corrupted

---

## 8. ACADEMIC CONTEXT

### 8.1 FYP Suitability

**Level**: Undergraduate Final Year Project

**Complexity**: Appropriate for FYP
- Combines multiple domains (crypto, signal processing, ML)
- Practical implementation
- Research component (CNN evaluation)
- Clear deliverables

**Learning Outcomes**:
- Cryptography implementation
- Audio signal processing
- Deep learning application
- Software engineering
- GUI development

### 8.2 Report Structure Suggestion

1. **Introduction**
   - Background on steganography
   - Problem statement
   - Objectives

2. **Literature Review**
   - Steganography techniques
   - Echo hiding method
   - AES encryption
   - CNN-based steganalysis

3. **Methodology**
   - System design
   - Implementation details
   - Tools and technologies

4. **Implementation**
   - Module descriptions
   - Code snippets
   - Integration

5. **Testing & Evaluation**
   - Functional testing
   - Audio quality analysis
   - CNN performance
   - Security analysis

6. **Results & Discussion**
   - Performance metrics
   - Comparison with existing work
   - Limitations

7. **Conclusion & Future Work**
   - Summary
   - Achievements
   - Future enhancements

### 8.3 Demonstration Points

**For Proposal**:
- System architecture diagram
- Module overview
- Sample encryption/decryption
- GUI mockup

**For Final Demo**:
- Live embedding demonstration
- Live extraction demonstration
- CNN training results
- Performance metrics
- Audio quality comparison

---

## 9. FUTURE ENHANCEMENTS

### 9.1 Potential Improvements

1. **Security**:
   - Random salt generation
   - Message authentication (HMAC)
   - Key exchange protocol

2. **Steganography**:
   - Multiple embedding techniques
   - Adaptive embedding
   - Robustness to compression

3. **CNN**:
   - Larger dataset
   - Data augmentation
   - Transfer learning
   - Real-time detection

4. **GUI**:
   - Batch processing
   - Audio preview
   - Waveform visualization
   - Progress bars

5. **Features**:
   - File encryption (not just text)
   - Multiple audio formats
   - Cloud integration
   - Mobile app

### 9.2 Research Directions

- Hybrid steganography techniques
- Adversarial training for robustness
- Quantum-resistant encryption
- Blockchain-based key management

---

## 10. REFERENCES

### 10.1 Key Papers

1. Cox, I. J., et al. (2007). *Digital Watermarking and Steganography*
2. Bender, W., et al. (1996). "Techniques for Data Hiding"
3. Gruhl, D., et al. (1996). "Echo Hiding"
4. Goodfellow, I., et al. (2016). *Deep Learning*

### 10.2 Standards

- NIST FIPS 197: Advanced Encryption Standard (AES)
- RFC 2898: PKCS #5 - Password-Based Cryptography
- RFC 4648: Base64 Encoding

### 10.3 Libraries

- PyCryptodome: https://www.pycryptodome.org/
- Librosa: https://librosa.org/
- TensorFlow: https://www.tensorflow.org/
- NumPy: https://numpy.org/

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Author**: FYP Student  
**Project**: Secure Audio Steganography System
