"""
Steganalysis Module using CNN (AI)
==============================
This module utilizes Deep Learning to detect anomalies (stego) within audio files.
It is used to evaluate if an AI can compromise our steganography system.

Author: Student FYP
Purpose: Test the robustness of the steganography system (Security Evaluation)
"""

import os
# Set Keras backend to PyTorch and Force CPU
os.environ['KERAS_BACKEND'] = 'torch'
os.environ["CUDA_VISIBLE_DEVICES"] = "-1" 

import numpy as np # type: ignore
import librosa # type: ignore
import librosa.display # type: ignore
import matplotlib.pyplot as plt # type: ignore
from sklearn.model_selection import train_test_split # type: ignore
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score # type: ignore
import keras # type: ignore
from keras import layers, models # type: ignore
from typing import List, Tuple, Dict, Any, Optional, cast
import soundfile as sf # type: ignore


class CNNSteganalysis:
    """
    This class handles the "Security Check" utilizing AI.
    It uses a CNN (Convolutional Neural Network) - highly effective for image analysis.
    
    Audio is converted into a "Spectrogram" (visual representation of sound).
    The AI analyzes these spectrograms to differentiate between Original and Stego audio.
    
    Architecture:
    - Input: Spectrogram image
    - Conv2D layers: Scans for minute patterns
    - MaxPooling: Downsamples data to reduce computational load
    - Dense layers: Decision making phase (Original or Stego?)
    """
    
    def __init__(self, n_mels=128, n_fft=2048, hop_length=512):
        """
        Configure spectrogram parameters.
        n_mels=128 (Image resolution), n_fft=2048 (Window size).
        """
        self.n_mels = n_mels
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.model: Optional[models.Sequential] = None
        self.history: Optional[Any] = None
        
    def _audio_to_spectrogram(self, audio_path: str, duration=5.0) -> np.ndarray:
        """
        Converts audio to a Mel-Spectrogram.
        This provides the pattern data for the AI to learn.
        """
        # Load the audio file (sr=None is faster as it avoids resampling)
        audio, sr = librosa.load(audio_path, sr=None, duration=duration)
        
        # Convert audio to Mel-Spectrogram
        mel_spec = librosa.feature.melspectrogram(
            y=audio,
            sr=sr,
            n_mels=self.n_mels,
            n_fft=self.n_fft,
            hop_length=self.hop_length
        )
        
        # Convert to dB (To enhance pattern visibility)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        return mel_spec_db

    def get_single_spectrogram(self, audio_path: str, duration=1.0) -> np.ndarray:
        """
        Helper function to obtain a spectrogram for a single file.
        Useful during prediction or SHAP analysis.
        """
        spec = self._audio_to_spectrogram(audio_path, duration=duration)
        
        # We need consistent normalization as used in training
        # Since we don't store global min/max, we'll use a standard range or local normalization
        # In prepare_dataset: X = (X - X.min()) / (X.max() - X.min())
        spec = (spec - spec.min()) / (spec.max() - spec.min())
        
        # Add batch and channel dimensions
        spec = spec[np.newaxis, ..., np.newaxis]
        return spec
    
    def prepare_dataset(self, original_files: list, stego_files: list) -> tuple:
        """
        Prepares the dataset for AI consumption.
        
        Steps:
        1. Take lists of Original and Stego audio files
        2. Convert to spectrograms via `_audio_to_spectrogram`
        3. Assign labels:
           - Original = 0
           - Stego = 1
        4. Split data (80% for Training, 20% for Testing)
        """
        print("Preparing dataset...")
        
        spectrograms = []
        labels = []
        
        # Process original files (label = 0)
        print(f"Processing {len(original_files)} original files...")
        for i, audio_path in enumerate(original_files):
            try:
                spec = self._audio_to_spectrogram(audio_path)
                spectrograms.append(spec)
                labels.append(0)  # Original
                print(f"  [{i+1}/{len(original_files)}] Processed: {os.path.basename(audio_path)}")
            except Exception as e:
                print(f"  Error processing {audio_path}: {e}")
        
        # Process stego files (label = 1)
        print(f"\nProcessing {len(stego_files)} stego files...")
        for i, audio_path in enumerate(stego_files):
            try:
                spec = self._audio_to_spectrogram(audio_path)
                spectrograms.append(spec)
                labels.append(1)  # Stego
                print(f"  [{i+1}/{len(stego_files)}] Processed: {os.path.basename(audio_path)}")
            except Exception as e:
                print(f"  Error processing {audio_path}: {e}")
        
        # Convert list to numpy array
        X = np.array(spectrograms)
        y = np.array(labels)
        
        # Normalize values to be between 0 and 1
        X = (X - X.min()) / (X.max() - X.min())
        
        # Add a channel dimension (Required by Conv2D)
        # e.g., grayscale has 1 channel, RGB has 3
        X = X[..., np.newaxis]
        
        # Split data into 2 parts:
        # 1. Training (80%)
        # 2. Testing (20%)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"\nDataset prepared:")
        print(f"  - Training samples: {len(X_train)}")
        print(f"  - Dataset size: {len(X_train)}")
        print(f"  - Spectrogram shape: {cast(Any, X_train).shape[1:]}")
        
        return X_train, X_test, y_train, y_test
    
    def build_model(self, input_shape: tuple) -> None:
        """
        Constructs the AI Architecture.
        
        Layers used:
        1. Conv2D: Scans for anomalies in spectrograms
        2. MaxPooling: Downsamples to extract larger features and save memory
        3. Dropout: Prevents the model from overfitting
        4. Dense (Output): Final decision - 0 or 1
        """
        print("\nBuilding CNN model...")
        
        self.model = models.Sequential([
            # Vision Layer 1 (Coarse scan)
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
            layers.MaxPooling2D((2, 2)),
            
            # Vision Layer 2 (Detailed scan)
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            
            # Vision Layer 3 (Deepest scan)
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            
            # Flatten data for decision making
            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.5),  # Dropout to prevent overfitting
            
            # Decision Layer (0 = Original, 1 = Stego)
            layers.Dense(1, activation='sigmoid')
        ])
        
        # Compile model
        self.model.compile( # type: ignore
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        if self.model is None:
            raise RuntimeError("Failed to build CNN model!")

        print("Model architecture:")
        self.model.summary() # type: ignore

    def train(self, X_train, y_train, X_test, y_test, epochs=20, batch_size=16) -> None:
        """
        Train the CNN model

        Args:
            X_train: Training spectrograms
            y_train: Training labels
            X_test: Test spectrograms
            y_test: Test labels
            epochs (int): Number of training epochs
            batch_size (int): Batch size for training
        """
        print(f"\nTraining CNN for {epochs} epochs...")

        # Stop training if results don't improve (saves time)
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        )

        # Calculate class weights to handle any imbalance
        from sklearn.utils.class_weight import compute_class_weight # type: ignore
        unique_classes = np.unique(y_train)
        
        if len(unique_classes) > 1:
            class_weights = compute_class_weight(
                class_weight='balanced',
                classes=unique_classes,
                y=y_train
            )
            class_weight_dict = {0: class_weights[0], 1: class_weights[1]}
            print(f"Class weights: {class_weight_dict}")
        else:
            # Fallback if data only has one class
            class_weight_dict = {0: 1.0, 1: 1.0}
            print(f"[WARNING] Single class detected. Skipping balanced weight calculation.")

        # Train model
        if self.model is None:
            raise RuntimeError("Model must be built before training!")
            
        self.history = self.model.fit( # type: ignore
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stopping],
            class_weight=class_weight_dict,
            verbose=0  # Disable progress bar to prevent 'NoneType' write error in EXE
        )
        
        print("\nTraining completed!")
    
    def evaluate(self, X_test, y_test) -> dict:
        """
        Evaluate the AI's performance.
        
        IMPORTANT:
        - If Accuracy ~50%:
          AI is guessing. This means our Steganography is highly effective (hard to detect).
          
        - If Accuracy > 80%:
          AI detects easily. Our Steganography is weak.
        """
        print("\nEvaluating model...")
        
        # Predict on test set
        # Disable progress bar (verbose=0) to prevent 'NoneType' write error in EXE
        y_pred_prob = self.model.predict(X_test, verbose=0) # type: ignore
        y_pred = (y_pred_prob > 0.5).astype(int).flatten()
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        conf_matrix = confusion_matrix(y_test, y_pred)
        class_report = classification_report(y_test, y_pred, 
                                             target_names=['Original', 'Stego'],
                                             output_dict=True)
        
        # Print results
        print(f"\nAccuracy: {accuracy * 100:.2f}%")
        print("\nConfusion Matrix:")
        print(conf_matrix)
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Original', 'Stego']))
        
        return {
            'accuracy': accuracy,
            'confusion_matrix': conf_matrix,
            'classification_report': class_report,
            'predictions': y_pred,
            'true_labels': y_test
        }
    
    def plot_training_history(self, save_path=None) -> None:
        """
        Plot training history (accuracy and loss)
        
        Args:
            save_path (str): Path to save plot (optional)
        """
        if self.history is None:
            print("No training history available")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # Plot Accuracy & Loss
        hist = self.history.history # type: ignore
        
        plt.subplot(1, 2, 1)
        plt.plot(hist['accuracy'])
        plt.plot(hist['val_accuracy'])
        plt.title('Model Accuracy')
        plt.ylabel('Accuracy')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Test'], loc='upper left')

        plt.subplot(1, 2, 2)
        plt.plot(hist['loss'])
        plt.plot(hist['val_loss'])
        plt.title('Model Loss')
        ax2.set_title('Model Loss')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Loss')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Training history saved to {save_path}")
        
        plt.show()
    
    def plot_confusion_matrix(self, conf_matrix, save_path=None) -> None:
        """
        Plot confusion matrix
        
        Args:
            conf_matrix: Confusion matrix from evaluation
            save_path (str): Path to save plot (optional)
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        
        im = ax.imshow(conf_matrix, cmap='Blues')
        
        # Set labels
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(['Original', 'Stego'])
        ax.set_yticklabels(['Original', 'Stego'])
        
        # Add text annotations
        for i in range(2):
            for j in range(2):
                text = ax.text(j, i, conf_matrix[i, j],
                             ha="center", va="center", color="black", fontsize=20)
        
        ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold')
        ax.set_xlabel('Predicted Label', fontsize=12)
        ax.set_ylabel('True Label', fontsize=12)
        
        plt.colorbar(im, ax=ax)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Confusion matrix saved to {save_path}")
        
        plt.show()
    
    def save_model(self, filepath: str) -> None:
        """
        Save trained model
        
        Args:
            model_path (str): Path to save model
        """
        if self.model is None:
            print("No model to save")
            return
        
        # 4. Save model
        self.model.save(filepath) # type: ignore
        print(f"Model saved to {filepath}")
    
    def load_model(self, model_path: str) -> None:
        """
        Load trained model
        
        Args:
            model_path (str): Path to model file
        """
        self.model = keras.models.load_model(model_path)
        print(f"Model loaded from {model_path}")


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("CNN Steganalysis Module - Test")
    print("=" * 60)
    
    print("\nNote: This module requires audio files for training.")
    print("For a complete test, you need:")
    print("  1. Original audio files (clean)")
    print("  2. Stego audio files (with embedded messages)")
    print("\nExample workflow:")
    print("  - Create CNN instance")
    print("  - Prepare dataset from audio files")
    print("  - Build and train model")
    print("  - Evaluate performance")
    print("  - Visualize results")
    
    # Demonstration with synthetic data
    print("\n" + "-" * 60)
    print("Creating synthetic dataset for demonstration...")
    
    # Initialize CNN
    cnn = CNNSteganalysis()
    
    # Create dummy spectrograms (simulating real data)
    n_samples = 40
    spec_shape = (128, 216)  # Typical mel-spectrogram shape
    
    # Generate synthetic spectrograms
    X_original = np.random.randn(n_samples // 2, *spec_shape) * 0.5
    X_stego = np.random.randn(n_samples // 2, *spec_shape) * 0.5 + 0.1  # Slightly different
    
    X = np.concatenate([X_original, X_stego])
    y = np.array([0] * (n_samples // 2) + [1] * (n_samples // 2))
    
    # Normalize
    X = (X - X.min()) / (X.max() - X.min())
    X = X[..., np.newaxis]
    
    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"✓ Created synthetic dataset:")
    # Define input shape (128x128 pixel representation)
    input_shape = (128, 128, 1)
    # Build AI model using this shape
    cnn.build_model(input_shape=cast(Any, input_shape))
    
    # Train model (quick training for demo)
    print("\nTraining model (demo with 5 epochs)...")
    cnn.train(X_train, y_train, X_test, y_test, epochs=5, batch_size=8)
    
    # Evaluate
    results = cnn.evaluate(X_test, y_test)
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
