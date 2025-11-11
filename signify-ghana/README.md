# 🇬🇭 Signify Ghana - GSL Recognition Platform

A browser-based Ghanaian Sign Language (GSL) recognition and learning platform using MediaPipe Hands and TensorFlow.js.

## 🎯 Features

- **Sign-to-Text + TTS**: Real-time GSL hand sign detection with text output and text-to-speech
- **Text-to-Sign**: Search and watch prerecorded GSL sign videos
- **Learning Hub**: Browse sign video gallery categorized by alphabet, numbers, and words

## 🏗️ Project Structure

```
signify-ghana/
├── web/                          # Frontend application
│   ├── src/
│   │   ├── pages/
│   │   │   ├── index.jsx         # Landing page
│   │   │   ├── sign.jsx          # Sign detection page
│   │   │   └── learn.jsx         # Learning hub
│   │   ├── components/
│   │   │   ├── WebcamDetector.jsx # MediaPipe + TF.js inference
│   │   │   └── VideoPlayer.jsx    # Text-to-video module
│   │   └── index.css             # Global styles
│   ├── public/
│   │   ├── assets/
│   │   │   ├── web_model/        # TF.js model (after training)
│   │   │   └── videos/           # Sign demonstration videos
│   │   └── labels.json           # Class labels (after training)
│   ├── package.json
│   └── vite.config.js
├── model_training/               # ML training pipeline
│   ├── collect/
│   │   ├── data_collection.html  # Data capture UI
│   │   └── server.py             # Flask upload endpoint
│   ├── train_model.py            # Model training script
│   ├── export_tfjs.sh            # TF.js export script
│   └── samples/                  # Training data (*.jsonl)
└── README.md
```

## 🚀 Quick Start

### Step 1: Collect Training Data

```bash
cd model_training/collect

# Install Python dependencies
pip install flask

# Start the data collection server
python server.py

# Open http://localhost:5000 in your browser
```

**Data Collection Instructions:**

1. Enter a sign label (e.g., "A", "B", "Hello", "Thank you")
2. Click "Start Camera"
3. Position your hand clearly in the frame
4. Click "Capture Sample" repeatedly (30-50 samples per sign)
5. Repeat for all signs you want to recognize

### Step 2: Train the Model

```bash
cd model_training

# Install ML dependencies
pip install tensorflow tensorflowjs scikit-learn numpy

# Train the model (outputs to web/public/)
python train_model.py
```

This will:

- Load samples from `samples/*.jsonl`
- Train a neural network classifier
- Export TF.js model to `../web/public/assets/web_model/`
- Save `labels.json` to `../web/public/`

### Step 3: Add Sign Videos (Optional)

Place demonstration videos in `web/public/assets/videos/`:

- Name format: `{label}.mp4` (lowercase)
- Example: `hello.mp4`, `a.mp4`, `thank_you.mp4`

### Step 4: Run the Web App

```bash
cd web

# Install dependencies
npm install

# Start development server
npm run dev
```

Open http://localhost:5173 in your browser.

## 📊 Model Specifications

### Input

- **Format**: Float32[63] normalized hand landmark vector
- **Structure**: 21 keypoints × 3 coordinates (x, y, z)
- **Source**: MediaPipe Hands

### Architecture

```
Input (63)
  → Dense(128, ReLU) → Dropout(0.3)
  → Dense(64, ReLU) → Dropout(0.3)
  → Dense(N, Softmax)
```

### Output

- **Format**: Softmax probabilities over N classes
- **Prediction**: argmax → class index → label from `labels.json`

### Data Format (JSONL)

```json
{"landmarks": [x1,y1,z1, x2,y2,z2, ..., x21,y21,z21]}
```

## 🎯 Performance Expectations

- **Prototype level**: Reliable for 8–30 classes
- **Recommended samples**: 30-50 per class
- **Confidence threshold**: 0.6 (60%)

## 🔧 Tech Stack

| Component      | Technology       |
| -------------- | ---------------- |
| Hand Detection | MediaPipe Hands  |
| Model Training | TensorFlow/Keras |
| Model Format   | TensorFlow.js    |
| Frontend       | React + Vite     |
| Text-to-Speech | Web Speech API   |
| Styling        | Vanilla CSS      |

## 🛠️ Development

### Building for Production

```bash
cd web
npm run build
npm run preview
```

### Project Commands

```bash
# Data collection
cd model_training/collect && python server.py

# Model training
cd model_training && python train_model.py

# Web development
cd web && npm run dev

# Web production build
cd web && npm run build
```

## 📝 Adding New Signs

1. **Collect data**: Use data collection tool to capture 30-50 samples
2. **Retrain model**: Run `python train_model.py`
3. **Add video**: Place `{sign}.mp4` in `web/public/assets/videos/`
4. **Restart app**: Refresh the browser

## 🐛 Troubleshooting

### Camera not working

- ✅ Grant camera permissions in browser
- ✅ Use HTTPS or localhost
- ✅ Check browser console for errors

### Model not loading

- ✅ Verify `web/public/assets/web_model/model.json` exists
- ✅ Check `web/public/labels.json` exists
- ✅ Check browser network tab for 404 errors

### Low accuracy

- ✅ Collect more samples (50+ per sign recommended)
- ✅ Ensure consistent hand positioning during collection
- ✅ Improve lighting conditions
- ✅ Increase model complexity in `train_model.py`

### Videos not playing

- ✅ Verify video files are in `web/public/assets/videos/`
- ✅ Check filename matches label (lowercase)
- ✅ Ensure video format is MP4

## 📄 License

This project is built for the UNICEF Startup Lab GSL Hackathon.

## 🤝 Contributing

1. Collect diverse training data
2. Test with different lighting conditions
3. Report issues and bugs
4. Improve model architecture
5. Add more sign categories

## 📧 Support

For questions and support, please open an issue in the repository.

---

**Built with ❤️ for the Ghanaian Deaf Community**
