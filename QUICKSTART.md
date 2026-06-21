# Quick Start Guide
## Secure Audio Steganography System

---

## 📋 Prerequisites

- **Python**: Version 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Audio Files**: FLAC format (lossless)

---

## 🚀 Installation (5 minutes)

### Step 1: Install Python
If you don't have Python installed:
- Download from [python.org](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"

### Step 2: Install Dependencies
Open terminal/command prompt in the project folder and run:

```bash
pip install -r requirements.txt
```

This will install:
- numpy (numerical computing)
- scipy (scientific computing)
- librosa (audio processing)
- soundfile (audio I/O)
- pycryptodome (encryption)
- tensorflow (deep learning)
- scikit-learn (machine learning utilities)
- matplotlib (visualization)

**Installation time**: ~2-5 minutes depending on internet speed

---

## 🎯 Quick Start (3 steps)

### Option 1: Using the GUI (Recommended for Demo)

```bash
python main.py
```

This opens the graphical interface where you can:
1. **Embed Tab**: Hide messages in audio
2. **Extract Tab**: Recover hidden messages

### Option 2: Using Python Code

```python
from encryption import AESEncryption
from echo_hiding import EchoHiding

# Encrypt and embed
aes = AESEncryption("your_password")
encrypted = aes.encrypt("Secret message")

echo = EchoHiding()
echo.embed("input.flac", encrypted, "output_stego.flac")

# Extract and decrypt
result = echo.extract("output_stego.flac")
decrypted = aes.decrypt(result['secret_text'])
print(decrypted)  # "Secret message"
```

### Option 3: Run Complete Tests

```bash
python test_demo.py
```

This runs comprehensive tests of all modules.

---

## 📝 Step-by-Step Tutorial

### Tutorial 1: Hiding a Message

**Scenario**: You want to send a secret message hidden in an audio file.

1. **Prepare your audio file**
   - Format: FLAC (use converter if needed)
   - Duration: At least 5 seconds
   - Quality: Any (higher is better)

2. **Launch the application**
   ```bash
   python main.py
   ```

3. **In the "Embed Message" tab**:
   - Click **Browse** → Select your FLAC file
   - Type your secret message in the text box
   - Enter a strong password (remember this!)
   - Click **"🔐 Encrypt & Embed Message"**

4. **Wait for completion**
   - Status bar shows progress
   - Results appear in the black console area
   - Note the output file location

5. **Result**
   - A new file is created: `yourfile_stego.flac`
   - This file contains your hidden message
   - Looks and sounds like normal audio

### Tutorial 2: Extracting a Message

**Scenario**: You received a stego audio file and need to extract the message.

1. **Launch the application**
   ```bash
   python main.py
   ```

2. **In the "Extract Message" tab**:
   - Click **Browse** → Select the stego FLAC file
   - Enter the password (must be exact same as embedding)
   - Click **"🔓 Extract & Decrypt Message"**

3. **View the message**
   - Extracted message appears in the text area
   - Results show in the console area

### Tutorial 3: CNN Analysis (Advanced)

**Scenario**: You want to evaluate how detectable your steganography is.

1. **Prepare dataset**
   - Collect original audio files (e.g., 20 files)
   - Create stego versions using the system
   - Organize in two folders

2. **Run analysis**
   ```python
   from cnn_analysis import CNNSteganalysis
   
   cnn = CNNSteganalysis()
   
   # Prepare data
   original_files = ['orig1.flac', 'orig2.flac', ...]
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
   cnn.plot_training_history()
   cnn.plot_confusion_matrix(results['confusion_matrix'])
   ```

3. **Interpret results**
   - **High accuracy (>90%)**: Steganography is detectable
   - **Low accuracy (~50%)**: Steganography is well-hidden
   - **Confusion matrix**: Shows classification performance

---

## 🎓 For FYP Demonstration

### Preparation Checklist

- [ ] Install all dependencies
- [ ] Test the GUI (run `python main.py`)
- [ ] Prepare sample FLAC audio files (3-5 files)
- [ ] Prepare demo messages (short, medium, long)
- [ ] Run `test_demo.py` to verify everything works
- [ ] Prepare slides with architecture diagram
- [ ] Practice the demo workflow

### Demo Script (5 minutes)

**Introduction (30 seconds)**
- "I've developed a secure audio steganography system"
- "Combines AES-256 encryption with echo hiding"
- "Includes CNN-based detection analysis"

**Live Demo (3 minutes)**

1. **Show the GUI**
   - "Clean, user-friendly interface"
   - "Two main functions: Embed and Extract"

2. **Embed a message**
   - Select audio file
   - Type: "This is my FYP demonstration message"
   - Enter password
   - Click embed
   - Show results

3. **Play audio comparison** (optional)
   - Play original audio
   - Play stego audio
   - "Sounds identical to human ear"

4. **Extract the message**
   - Switch to Extract tab
   - Select stego file
   - Enter same password
   - Show extracted message

**Technical Explanation (1.5 minutes)**

- "Uses AES-256-CBC for encryption"
- "Echo hiding embeds data using imperceptible echoes"
- "CNN analyzes detection resistance"
- Show architecture diagram

**Q&A Preparation**

Common questions:
- **Q**: "Why FLAC format?"
  - **A**: "Lossless format preserves steganography. MP3 compression would destroy hidden data."

- **Q**: "How secure is it?"
  - **A**: "AES-256 is military-grade. Without password, message is unreadable. Echo hiding is imperceptible."

- **Q**: "What's the capacity?"
  - **A**: "Depends on audio length. 5-second audio can hide ~30-40 characters of encrypted text."

- **Q**: "Can it survive compression?"
  - **A**: "No, lossy compression destroys the hidden data. This is a limitation."

- **Q**: "What's the CNN for?"
  - **A**: "Evaluates detection resistance. Not an attacker, but an evaluation tool."

---

## 🔧 Troubleshooting

### Issue: Dependencies won't install

**Solution**:
```bash
# Try upgrading pip first
python -m pip install --upgrade pip

# Then install dependencies
pip install -r requirements.txt

# If specific package fails, install individually
pip install numpy scipy librosa soundfile pycryptodome tensorflow scikit-learn matplotlib
```

### Issue: "No module named 'tkinter'"

**Solution**:
- **Windows**: Tkinter comes with Python, reinstall Python
- **Linux**: `sudo apt-get install python3-tk`
- **macOS**: Tkinter included with Python

### Issue: Audio file not supported

**Solution**:
Convert to FLAC using ffmpeg:
```bash
# Install ffmpeg first (ffmpeg.org)
ffmpeg -i input.mp3 output.flac
```

### Issue: "Audio file too short for message length"

**Solution**:
- Use shorter message, OR
- Use longer audio file (at least 5 seconds)

### Issue: Extraction gives wrong message

**Solution**:
- Verify you're using the exact same password
- Ensure stego file hasn't been modified
- Check file format is still FLAC

### Issue: CNN training is very slow

**Solution**:
- Reduce number of epochs
- Use smaller dataset for testing
- Consider using GPU (if available)

---

## 📊 Performance Tips

### For Best Audio Quality
- Use high-quality source audio (44.1kHz or higher)
- Keep echo amplitude low (0.3-0.5)
- Use longer audio for shorter messages

### For Maximum Capacity
- Use longer audio files
- Reduce echo delays (but increases detectability)
- Compress message before encryption

### For Best Security
- Use strong passwords (12+ characters, mixed case, numbers, symbols)
- Don't reuse passwords
- Share password through secure channel (not with the audio)

---

## 📚 Learning Resources

### Understanding the Concepts

**Steganography**:
- [Wikipedia: Steganography](https://en.wikipedia.org/wiki/Steganography)
- Paper: "Techniques for Data Hiding" by Bender et al.

**Echo Hiding**:
- Paper: "Echo Hiding" by Gruhl et al. (1996)
- Concept: Uses imperceptible echoes to encode data

**AES Encryption**:
- [NIST FIPS 197](https://csrc.nist.gov/publications/detail/fips/197/final)
- Tutorial: [AES Explained](https://www.youtube.com/results?search_query=aes+encryption+explained)

**CNN for Audio**:
- Paper: "Deep Learning" by Goodfellow et al.
- Tutorial: [Audio Classification with CNN](https://www.tensorflow.org/tutorials/audio/simple_audio)

### Python Libraries Documentation

- [NumPy](https://numpy.org/doc/)
- [Librosa](https://librosa.org/doc/latest/index.html)
- [TensorFlow](https://www.tensorflow.org/api_docs)
- [PyCryptodome](https://www.pycryptodome.org/)

---

## 🎯 Next Steps

After getting familiar with the system:

1. **Experiment**
   - Try different echo parameters
   - Test with various audio types
   - Measure audio quality (SNR)

2. **Extend**
   - Add more steganography techniques
   - Implement file encryption (not just text)
   - Create batch processing

3. **Research**
   - Compare with other methods
   - Analyze robustness
   - Explore adversarial training

4. **Document**
   - Write your FYP report
   - Create presentation slides
   - Prepare demo videos

---

## 📞 Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review DOCUMENTATION.md for technical details
3. Run `test_demo.py` to verify installation
4. Check error messages carefully

---

## ✅ Checklist for FYP Submission

- [ ] Code is complete and commented
- [ ] All modules tested and working
- [ ] GUI is functional
- [ ] Documentation is comprehensive
- [ ] Demo is prepared and practiced
- [ ] Report includes:
  - [ ] Introduction and objectives
  - [ ] Literature review
  - [ ] Methodology
  - [ ] Implementation details
  - [ ] Testing and results
  - [ ] Conclusion
- [ ] Presentation slides ready
- [ ] Source code organized and clean

---

**Good luck with your FYP! 🎓**

---

*Last updated: 2024*  
*Version: 1.0*
