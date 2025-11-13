"""
Manual export to TensorFlow.js - No tensorflowjs package needed
"""
import os
import json
import shutil
import numpy as np
from tensorflow import keras
import tensorflow as tf

MODEL_PATH = 'model_hybrid.h5'
OUTPUT_DIR = 'web_model'

print("\n" + "="*70)
print("🔄 Manual Export to TensorFlow.js")
print("="*70 + "\n")

# Check model exists
if not os.path.exists(MODEL_PATH):
    print(f"❌ {MODEL_PATH} not found!")
    print("   Run: python train_hybrid_model.py")
    exit(1)

# Load model
print("1️⃣ Loading model...")
model = keras.models.load_model(MODEL_PATH)
print(f"   ✅ Loaded: {model.input_shape} → {model.output_shape}")

# Clean output
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR)

# Get topology
print("\n2️⃣ Extracting topology...")
config = model.get_config()

# Get Keras version safely
try:
    keras_version = keras.__version__
except AttributeError:
    try:
        keras_version = tf.__version__
    except:
        keras_version = "2.15.0"

topology = {
    'class_name': model.__class__.__name__,
    'config': config,
    'keras_version': keras_version,
    'backend': 'tensorflow'
}
print(f"   ✅ Model type: {topology['class_name']}")
print(f"   ✅ Keras version: {keras_version}")
print(f"   ✅ Layers: {len(config.get('layers', []))}")

# Extract weights
print("\n3️⃣ Extracting weights...")
weight_specs = []
weight_data_list = []

for layer in model.layers:
    weights = layer.get_weights()
    if not weights:
        continue
    
    layer_name = layer.name
    
    for idx, w in enumerate(weights):
        # Convert to float32
        w_float32 = w.astype(np.float32)
        
        # Determine weight name
        if hasattr(layer, 'weights') and idx < len(layer.weights):
            try:
                tf_name = layer.weights[idx].name.replace(':0', '')
            except:
                tf_name = f'{layer_name}/weight_{idx}'
        else:
            # Fallback: kernel, bias, recurrent_kernel, etc.
            weight_names = ['kernel', 'bias', 'recurrent_kernel', 'recurrent_bias']
            weight_type = weight_names[idx] if idx < len(weight_names) else f'weight_{idx}'
            tf_name = f'{layer_name}/{weight_type}'
        
        print(f"   {tf_name}: {w_float32.shape}")
        
        # Store
        weight_specs.append({
            'name': tf_name,
            'shape': list(w_float32.shape),
            'dtype': 'float32'
        })
        weight_data_list.append(w_float32.flatten())

# Concatenate all weights
print("\n4️⃣ Creating binary...")
all_weights = np.concatenate(weight_data_list).astype(np.float32)
weights_bytes = all_weights.tobytes()

bin_path = os.path.join(OUTPUT_DIR, 'group1-shard1of1.bin')
with open(bin_path, 'wb') as f:
    f.write(weights_bytes)

print(f"   ✅ Binary: {len(weights_bytes):,} bytes ({len(weights_bytes)/1024/1024:.2f} MB)")

# Create model.json
print("\n5️⃣ Creating model.json...")
model_json = {
    'format': 'layers-model',
    'generatedBy': f'keras v{keras_version}',
    'convertedBy': 'Signify Ghana Manual Export',
    'modelTopology': topology,
    'weightsManifest': [{
        'paths': ['group1-shard1of1.bin'],
        'weights': weight_specs
    }]
}

json_path = os.path.join(OUTPUT_DIR, 'model.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(model_json, f, indent=2)

print(f"   ✅ JSON: {os.path.getsize(json_path):,} bytes")

# Verify
print("\n6️⃣ Verifying...")
with open(json_path, 'r', encoding='utf-8') as f:
    verify = json.load(f)

if 'modelTopology' in verify and 'weightsManifest' in verify:
    print("   ✅ Structure valid")
    print(f"   ✅ Topology: {verify['modelTopology']['class_name']}")
    print(f"   ✅ Weight specs: {len(verify['weightsManifest'][0]['weights'])}")
    
    # Check binary size matches
    total_weights = sum(np.prod(spec['shape']) for spec in verify['weightsManifest'][0]['weights'])
    expected_bytes = total_weights * 4  # 4 bytes per float32
    actual_bytes = os.path.getsize(bin_path)
    
    if expected_bytes == actual_bytes:
        print(f"   ✅ Binary size correct: {actual_bytes:,} bytes")
    else:
        print(f"   ⚠️ Size mismatch: expected {expected_bytes:,}, got {actual_bytes:,}")
else:
    print("   ❌ Structure invalid!")
    exit(1)

# List output
print("\n✅ Export complete!")
print("\nOutput files:")
for fname in sorted(os.listdir(OUTPUT_DIR)):
    fpath = os.path.join(OUTPUT_DIR, fname)
    print(f"   ✅ {fname}: {os.path.getsize(fpath):,} bytes")

print("\n" + "="*70)
print("📋 Next Steps:")
print("="*70)
print("\n1️⃣ Copy to web app:")
print("   Remove-Item -Recurse -Force ..\\web\\public\\assets\\web_model")
print("   xcopy /E /I web_model ..\\web\\public\\assets\\web_model")
print("   copy labels.json ..\\web\\public\\")
print("\n2️⃣ Verify copy:")
print("   dir ..\\web\\public\\assets\\web_model\\")
print("\n3️⃣ Start web server:")
print("   cd ..\\web")
print("   npm run dev")
print("\n4️⃣ IMPORTANT - Clear browser cache:")
print("   • Press Ctrl+Shift+Delete")
print("   • Select 'All time'")
print("   • Check 'Cached images and files'")
print("   • Click 'Clear data'")
print("   • Close browser completely")
print("   • Reopen and visit: http://localhost:5173/sign.html")
print("\n" + "="*70 + "\n")