"""
Train hybrid model for static + dynamic GSL signs
Handles both single-frame poses and movement sequences
"""
import os
import json
import glob
import numpy as np
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Configuration
SAMPLES_DIR = 'samples'
MODEL_OUTPUT = 'model_hybrid.h5'
LABELS_OUTPUT = 'labels.json'
MAX_SEQUENCE_LENGTH = 30  # Frames per sequence
EPOCHS = 100
BATCH_SIZE = 16
TEST_SPLIT = 0.2
RANDOM_STATE = 42

def load_hybrid_data():
    """Load both static and sequence samples"""
    print("\n📂 Loading training data...")
    
    all_sequences = []
    all_labels = []
    labels_set = set()
    class_counts = {}
    
    # Load static samples (*.jsonl - not _seq)
    static_files = [f for f in glob.glob(f'{SAMPLES_DIR}/*.jsonl') if not f.endswith('_seq.jsonl')]
    
    for jsonl_file in static_files:
        label = os.path.basename(jsonl_file).replace('.jsonl', '')
        labels_set.add(label)
        
        with open(jsonl_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    landmarks = data.get('landmarks', [])
                    
                    if len(landmarks) != 63:
                        continue
                    
                    # Convert static to sequence by repeating same frame
                    sequence = [landmarks] * MAX_SEQUENCE_LENGTH
                    all_sequences.append(sequence)
                    all_labels.append(label)
                    
                    class_counts[label] = class_counts.get(label, 0) + 1
                    
                except json.JSONDecodeError:
                    continue
    
    # Load sequence samples (*_seq.jsonl)
    seq_files = glob.glob(f'{SAMPLES_DIR}/*_seq.jsonl')
    
    for jsonl_file in seq_files:
        label = os.path.basename(jsonl_file).replace('_seq.jsonl', '')
        labels_set.add(label)
        
        with open(jsonl_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    sequence = data.get('sequence', [])
                    
                    if not sequence:
                        continue
                    
                    # Pad or truncate to MAX_SEQUENCE_LENGTH
                    if len(sequence) < MAX_SEQUENCE_LENGTH:
                        # Pad with last frame repeated
                        padding = [sequence[-1]] * (MAX_SEQUENCE_LENGTH - len(sequence))
                        sequence = sequence + padding
                    else:
                        # Truncate
                        sequence = sequence[:MAX_SEQUENCE_LENGTH]
                    
                    # Validate each frame
                    valid = True
                    for frame in sequence:
                        if len(frame) != 63:
                            valid = False
                            break
                    
                    if not valid:
                        continue
                    
                    all_sequences.append(sequence)
                    all_labels.append(label)
                    
                    class_counts[label] = class_counts.get(label, 0) + 1
                    
                except json.JSONDecodeError:
                    continue
    
    label_list = sorted(list(labels_set))
    label_to_idx = {label: idx for idx, label in enumerate(label_list)}
    
    print(f"   ✅ Found {len(label_list)} classes: {label_list}")
    print(f"   ✅ Total samples: {len(all_sequences)}")
    print(f"\n📊 Samples per class:")
    
    for label in sorted(class_counts.keys()):
        count = class_counts[label]
        bar = "█" * min(count, 50)
        print(f"   {label:>10s}: {count:3d} {bar}")
    
    # Convert to numpy
    X = np.array(all_sequences, dtype=np.float32)
    y = np.array([label_to_idx[label] for label in all_labels], dtype=np.int32)
    
    return X, y, label_list

def build_lstm_model(num_classes):
    """Build LSTM model for sequence classification"""
    model = keras.Sequential([
        layers.Input(shape=(MAX_SEQUENCE_LENGTH, 63), name='sequence_input'),
        
        # LSTM layers to capture temporal patterns
        layers.LSTM(128, return_sequences=True, name='lstm_1'),
        layers.Dropout(0.4, name='dropout_1'),
        
        layers.LSTM(64, name='lstm_2'),
        layers.Dropout(0.4, name='dropout_2'),
        
        # Dense layers
        layers.Dense(64, activation='relu', name='dense_1'),
        layers.Dropout(0.3, name='dropout_3'),
        
        layers.Dense(num_classes, activation='softmax', name='output')
    ], name='gsl_hybrid_classifier')
    
    return model

def main():
    print("\n" + "="*70)
    print("🇬🇭 GSL Hybrid Model Training (Static + Dynamic Signs)")
    print("="*70 + "\n")
    
    # Load data
    X, y, labels = load_hybrid_data()
    
    if len(labels) < 2:
        raise ValueError(f"Need at least 2 classes. Found: {len(labels)}")
    
    print(f"\n🔧 Preparing training data...")
    print(f"   X shape: {X.shape} (samples, frames, features)")
    print(f"   y shape: {y.shape} (samples,)")
    
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X, y,
        test_size=TEST_SPLIT,
        random_state=RANDOM_STATE,
        stratify=y
    )
    
    print(f"   Training set: {len(X_train)} samples")
    print(f"   Validation set: {len(X_val)} samples")
    
    # Build model
    print("\n🏗️  Building LSTM model...")
    model = build_lstm_model(len(labels))
    model.summary()
    
    # Compile
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Train
    print(f"\n🚀 Training for up to {EPOCHS} epochs...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        verbose=1,
        callbacks=[
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                verbose=1
            )
        ]
    )
    
    # Evaluate
    print("\n📈 Final Evaluation:")
    train_loss, train_acc = model.evaluate(X_train, y_train, verbose=0)
    val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
    
    print(f"   Training accuracy:   {train_acc*100:.2f}%")
    print(f"   Validation accuracy: {val_acc*100:.2f}%")
    
    if val_acc < 0.7:
        print("\n⚠️  Accuracy could be improved:")
        print("   - Collect more samples (aim for 50+ per class)")
        print("   - Ensure consistent hand positioning")
        print("   - Check for mislabeled data")
    
    # Save model
    print(f"\n💾 Saving model...")
    model.save(MODEL_OUTPUT)
    print(f"   ✅ Saved {MODEL_OUTPUT}")
    
    # Save labels
    with open(LABELS_OUTPUT, 'w') as f:
        json.dump(labels, f, indent=2)
    print(f"   ✅ Saved {LABELS_OUTPUT}")
    
    # Instructions
    print("\n" + "="*70)
    print("📋 Next Steps:")
    print("="*70)
    print("\n1️⃣ Export to TensorFlow.js:")
    print("   python export_hybrid_model.py")
    print("\n2️⃣ Copy to web app:")
    print("   xcopy /E /I web_model ..\\web\\public\\assets\\web_model")
    print("   copy labels.json ..\\web\\public\\")
    print("\n3️⃣ Update web app to use sequence detection")
    print("\n4️⃣ Test:")
    print("   cd ..\\web")
    print("   npm run dev")
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)