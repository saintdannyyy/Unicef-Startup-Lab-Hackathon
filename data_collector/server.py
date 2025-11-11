# server.py
from flask import Flask, request, jsonify
import json, os
app = Flask(__name__)
os.makedirs('samples', exist_ok=True)

@app.route('/upload_sample', methods=['POST'])
def upload_sample():
    data = request.get_json()
    label = data.get('label')
    landmarks = data.get('landmarks')
    if not label or not landmarks:
        return jsonify({'error':'bad payload'}), 400
    # Append to per-label file
    fname = f'samples/{label}.jsonl'
    with open(fname, 'a') as f:
        f.write(json.dumps({'landmarks':landmarks}) + '\n')
    return jsonify({'status':'ok'})

if __name__ == '__main__':
    app.run(port=5000)