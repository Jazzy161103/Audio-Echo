# -*- coding: utf-8 -*-
"""
Run Security Evaluation Demo
============================
An automated script for running Deep Learning analysis.
Execution Flow:
1. Retrieve target audio
2. Generate stego version (embed hidden message)
3. Slice into dataset segments
4. Train AI to differentiate the robust features
5. Output security level result
"""

import os
import sys
import warnings

# ======================================================================
# CONFIGURATION - KERAS & GPU (Must be set BEFORE imports)
# ======================================================================
# Force CPU training to avoid CUDA OOM on limited hardware
os.environ["KERAS_BACKEND"] = "torch"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1" 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"

import numpy as np # type: ignore
import soundfile as sf # type: ignore
import shutil
import tempfile
import time
from explainability import run_shap_analysis, plot_spectral_difference, generate_detailed_report # type: ignore
# Delay these imports until config is set
from cnn_analysis import CNNSteganalysis # type: ignore
from echo_hiding import EchoHiding # type: ignore
from encryption import AESEncryption # type: ignore

# Ignore standard warnings for cleaner terminal output
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Force CPU training to avoid CUDA OOM on limited hardware
# If you want to use GPU, comment out these lines
os.environ["KERAS_BACKEND"] = "torch" # Keep torch as engine but force CPU
os.environ["CUDA_VISIBLE_DEVICES"] = "-1" 

# Optimize GPU memory for Torch backend (Keras 3)
os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"

try:
    import torch # type: ignore
except ImportError:
    torch = None

def run_analysis(audio_file_path, log_callback=None):
    """
    Main function to run the steganalysis.
    Args:
        audio_file_path (str): Path to the source audio
        log_callback (func): Function to handle print statements (e.g., send to GUI)
    """
    
    # Helper to print to console & GUI simultaneously
    def log(message):
        print(message)
        if log_callback:
            log_callback(message + "\n")

    log("=" * 70)
    log("  STEGANALYSIS SECURITY EVALUATION")
    log("  Evaluating Detection Resistance using CNN")
    log("=" * 70)

    # Configuration
    AUDIO_FILE = audio_file_path
    
    filename_only = os.path.splitext(os.path.basename(AUDIO_FILE))[0]
    
    # Utilize system temp folder to avoid 'Access Denied' issues
    BASE_TEMP = tempfile.gettempdir()
    DATASET_DIR = os.path.join(BASE_TEMP, "stego_fyp_analysis_v2")
    
    # Ensure absolute path is used
    AUDIO_FILE = os.path.abspath(audio_file_path)
    # Use unique name to prevent clashes during consecutive runs (File Busy)
    STEGO_FILE = os.path.join(BASE_TEMP, f"analysis_stego_{int(time.time())}.flac")
    
    ORIGINAL_DIR = os.path.join(DATASET_DIR, "original")
    STEGO_DIR = os.path.join(DATASET_DIR, "stego")
    SLICE_DURATION = 1.0
    
    # 1. Setup Work Directory
    log("\n[1] Preparing analysis environment...")
    
    # Only clear subfolders to avoid "Access Denied" on the main DATASET_DIR
    for d in [ORIGINAL_DIR, STEGO_DIR]:
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
                time.sleep(0.5) # Wait for OS to release the folder
            except Exception as e:
                 log(f"    [WARNING] Could not clear {os.path.basename(d)}: {e}")
        os.makedirs(d, exist_ok=True)
    
    log(f"    [OK] Environment ready at: {DATASET_DIR}")

    # 2. Check File & Explain Methodology
    log("\n[2] Setting up Evaluation Methodology...")
    log("    METHODOLOGY EXPLANATION:")
    log("    ------------------------------------------")
    log("    The system performs a 'Resistance Test' by comparing:")
    log("    (A) Baseline Audio: Your provided file")
    log("    (B) Stego Audio:    A generated version with hidden message")
    log("    ")
    log("    Goal: Can AI distinguish between (A) and (B)?")
    log("    ------------------------------------------")

    if not os.path.exists(AUDIO_FILE):
        log(f"    [ERROR] Original audio not found: {AUDIO_FILE}")
        return

    # A fresh stego file MUST be generated for a fair evaluation
    if os.path.exists(STEGO_FILE):
        try:
            os.remove(STEGO_FILE)
        except:
            pass

    log(f"    [INFO] Generating comparison target (Stego Audio)...")
    try:
        aes = AESEncryption("TestPassword12")
        echo = EchoHiding()
        # Use a short message that fits even smaller audio files
        test_msg = "X"
        encrypted = aes.encrypt(test_msg)
        
        result = echo.embed(AUDIO_FILE, encrypted, STEGO_FILE)
        
        if result['status'] == 'success':
            log(f"    [OK] Comparison target created successfully")
        else:
            log(f"    [ERROR] Embedding failed: {result['message']}")
            return
    except Exception as e:
        log(f"    [ERROR] Unexpected error during embedding: {e}")
        return

    log(f"    [OK] Baseline: {os.path.basename(AUDIO_FILE)}")
    log(f"    [OK] Target:   {os.path.basename(STEGO_FILE)}")

    # 3. Slice Audio Files (Data Augmentation)
    def slice_audio(file_path, output_dir, prefix):
        log(f"    Slicing {os.path.basename(file_path)}...")
        try:
            audio, sr = sf.read(file_path)
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)  # Convert to Mono
            
            samples_per_slice = int(SLICE_DURATION * sr)
            total_samples = len(audio)
            num_slices = total_samples // samples_per_slice
            
            count = 0
            for i in range(num_slices):
                start = i * samples_per_slice
                end = start + samples_per_slice
                segment = audio[start:end]
                
                out_path = os.path.join(output_dir, f"{prefix}_{i:03d}.flac")
                sf.write(out_path, segment, sr, format='FLAC')
                count += 1
            return count
        except Exception as e:
            log(f"    [ERROR] Slicing failed: {e}")
            return 0

    log("\n[3] Creating dataset by slicing audio...")
    
    # Give the filesystem a moment to unlock the file
    time.sleep(1.0)
    
    if os.path.exists(STEGO_FILE):
        log(f"    [DEBUG] Stego file exists. Size: {os.path.getsize(STEGO_FILE)} bytes")
    else:
        log(f"    [ERROR] Stego file NOT found at: {STEGO_FILE}")

    MAX_SAMPLES = 200 # Cap dataset size for speed
    
    n_orig = slice_audio(AUDIO_FILE, ORIGINAL_DIR, "orig")
    n_stego = slice_audio(STEGO_FILE, STEGO_DIR, "stego")
    
    # Cap the number of files to process if there are too many
    orig_files = [os.path.join(ORIGINAL_DIR, f) for f in os.listdir(ORIGINAL_DIR) if f.endswith('.flac')]
    stego_files = [os.path.join(STEGO_DIR, f) for f in os.listdir(STEGO_DIR) if f.endswith('.flac')]
    
    if len(orig_files) > MAX_SAMPLES:
        orig_files = orig_files[:MAX_SAMPLES]
        log(f"    [INFO] Capping original samples to {MAX_SAMPLES} for faster analysis.")
    if len(stego_files) > MAX_SAMPLES:
        stego_files = stego_files[:MAX_SAMPLES]
        log(f"    [INFO] Capping stego samples to {MAX_SAMPLES} for faster analysis.")

    log(f"    [OK] Dataset created:")
    log(f"         - Original samples: {n_orig}")
    log(f"         - Stego samples:    {n_stego}")
    log(f"         - Total samples:    {n_orig + n_stego}")

    if n_orig == 0 or n_stego == 0:
        log("\n[ERROR] Not enough samples to train. Try a longer audio file (min 10s).")
        return

    # 4. Prepare AI Data (Convert to Spectrogram)
    log("\n[4] Preparing data for CNN input (Mel-Spectrograms)...")
    try:
        cnn = CNNSteganalysis()

        # Files are already filtered and capped above

        # Use all available samples
        X_train, X_test, y_train, y_test = cnn.prepare_dataset(orig_files, stego_files)
    except Exception as e:
        log(f"[ERROR] Data preparation failed: {e}")
        return

    # 5. Train AI (Teach pattern recognition)
    log("\n[5] Training CNN Model...")
    try:
        # Clear GPU memory before training
        if torch and torch.cuda.is_available():
            torch.cuda.empty_cache()
            log("    [INFO] GPU memory cache cleared.")
            
        cnn.build_model(input_shape=X_train.shape[1:])
        # Batch size 4 is safer for limited VRAM (e.g. 4GB GPUs)
        cnn.train(X_train, y_train, X_test, y_test, epochs=10, batch_size=4)
    except Exception as e:
        log(f"[ERROR] Training failed: {e}")
        return

    # 6. Test AI Evaluation
    log("\n[6] Evaluating Detection Resistance...")
    try:
        results = cnn.evaluate(X_test, y_test)
    except Exception as e:
        log(f"[ERROR] Evaluation failed: {e}")
        return

    # 7. Visualize
    log("\n[7] Generating visualizations...")
    try:
        cnn.plot_training_history(save_path="steganalysis_history.png")
        cnn.plot_confusion_matrix(results['confusion_matrix'], save_path="steganalysis_confusion_matrix.png")
        
        # 1. First, generate fast scientific metrics and spectral difference
        log("\n[7.1] Generating Scientific Metrics & Spectral Difference...")
        try:
            # Find samples for comparison
            stego_indices = np.where(y_test == 1)[0]
            orig_indices = np.where(y_test == 0)[0]
            
            if len(stego_indices) > 0 and len(orig_indices) > 0:
                target_sample = X_test[stego_indices[0]:stego_indices[0]+1]
                orig_sample = X_test[orig_indices[0]:orig_indices[0]+1]
                
                # Spectral Difference using premium graphing tool (generate_spectrogram.py)
                try:
                    from generate_spectrogram import plot_spectrogram_comparison
                    log("    [INFO] Generating Premium Audio Spectrogram Comparison...")
                    # Generates full graph to be displayed in GUI
                    # Generates fast graph (first 10s) to be displayed in GUI
                    plot_spectrogram_comparison(AUDIO_FILE, STEGO_FILE, output_filename="steganalysis_diff.png", auto_open=False, max_duration=10.0)
                    log("    [OK] Premium Spectral difference plot saved as steganalysis_diff.png")
                except Exception as e:
                    log(f"    [WARNING] Premium Spectrogram failed (fallback to basic): {e}")
                    plot_spectral_difference(orig_sample, target_sample, "steganalysis_diff.png")
                    log("    [OK] Basic Spectral difference plot saved as steganalysis_diff.png")
            else:
                log("    [WARNING] Could not find valid samples for spectral difference plot.")
            
            # Initial Detailed Report (without SHAP data yet)
            log("    [INFO] Calculating acoustic metrics (SNR, PSNR, etc.)...")
            report = generate_detailed_report(AUDIO_FILE, STEGO_FILE, shap_values=None, eval_metrics=results)
            log("    [OK] Initial scientific report generated.")
        except Exception as e:
            log(f"    [WARNING] Initial report/plot failed: {e}")
            report = "Scientific report generation failed."

        # 2. Then, try the heavy SHAP analysis
        log("\n[7.2] Generating SHAP Explainable AI (XAI) Visualization...")
        try:
            # Use small background for speed (10 samples)
            X_background = X_train[:10] if len(X_train) > 10 else X_train
            
            if len(stego_indices) > 0:
                sample_idx = stego_indices[0]
                target_sample = X_test[sample_idx:sample_idx+1]
                
                log(f"    [INFO] Running SHAP analysis on sample {sample_idx}...")
                shap_vals = run_shap_analysis(cnn.model, X_background, target_sample, "steganalysis_explain.png")
                log("    [OK] SHAP visualization saved as steganalysis_explain.png")
                
                # Update report with SHAP attribution data
                log("    [INFO] Finalizing report with AI attribution data...")
                report = generate_detailed_report(AUDIO_FILE, STEGO_FILE, shap_values=shap_vals, eval_metrics=results)
            else:
                log("    [WARNING] No stego samples for SHAP analysis.")
            
            log("\n" + report + "\n")
            log("    [OK] Analysis report finalized and saved as steganalysis_report.txt")
            
        except Exception as e:
            log(f"    [ERROR] SHAP/Final report generation failed: {str(e)}")
            # Show the partial report if SHAP failed
            if 'report' in locals():
                log("\n--- Partial Report (without SHAP) ---\n")
                log(report + "\n")
            
    except Exception as e:
        log(f"[WARNING] Visualization block general failure: {e}")

    log("\n" + "=" * 70)
    log("  ANALYSIS COMPLETE")
    log("=" * 70)
    log("\nINTERPRETATION OF RESULTS:")
    
    accuracy = results['accuracy'] * 100
    log(f"Model Accuracy: {accuracy:.2f}%")

    if accuracy < 60:
        log(">> EXCELLENT RESULT! Accuracy is near 50% (Random Guess).")
        log("   This means the CNN CANNOT distinguish between Original and Stego audio.")
        log("   Your system is HIGHLY RESISTANT to detection.")
    elif accuracy < 80:
        log(">> GOOD RESULT. Some traces are detectable, but not obvious.")
        log("   Typical for Echo Hiding without advanced masking.")
    else:
        log(">> DETECTABLE. The CNN can distinguish stego audio.")
        log("   This is expected for basic Echo Hiding implementations.")
        
    # Cleanup temp file
    if os.path.exists(STEGO_FILE):
        try:
            os.remove(STEGO_FILE)
            log(f"    [INFO] Cleaned up temporary evaluation file.")
        except:
            pass
    
    # Optional: Keep the sliced dataset for viewing, or clean up
    # shutil.rmtree(DATASET_DIR) # Uncomment to fully clean up

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_analysis(sys.argv[1])
    else:
        print("Usage: python run_steganalysis.py <audio_file>")
