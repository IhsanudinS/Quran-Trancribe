import os
from dotenv import load_dotenv
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import logging
import io
import numpy as np
from pydub import AudioSegment
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
from database import save_to_database, get_transcription_data
from utils2 import normalize_text, is_harakat, compare_texts

load_dotenv()

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)

# Load model and audio folder path from .env
AUDIO_FOLDER = os.getenv('AUDIO_FOLDER')
os.makedirs(AUDIO_FOLDER, exist_ok=True)
processor = Wav2Vec2Processor.from_pretrained(os.getenv('MODEL_PATH'))
model = Wav2Vec2ForCTC.from_pretrained(os.getenv('MODEL_PATH'))


@app.route('/get_transcription/<int:id>', methods=['GET'])
def get_transcription(id):
    try:
        # Ambil data dari database berdasarkan ID
        transcription_data = get_transcription_data(id)
        if transcription_data is None:
            return jsonify({"error": "Transcription data not found"}), 404

        # Ambil path file audio dari hasil query
        audio_path = transcription_data['audio_path']

        # Cek apakah file audio ada
        if not os.path.exists(audio_path):
            return jsonify({"error": "Audio file not found"}), 404

        # Siapkan respons
        response = {
            "original_text": transcription_data['original_text'],
            "transcription": transcription_data['transcription'],
            "differences": transcription_data['differences'],
            "accuracy": transcription_data['accuracy'],
            "error_rate": transcription_data['error_rate']
        }

        # Kembalikan file audio dan data transkripsi
        return jsonify({
            "transcription_data": response,
            "audio_url": request.host_url + 'audio/' + os.path.basename(audio_path)
        })

    except Exception as e:
        logging.error("Error retrieving transcription: %s", e)
        return jsonify({"error": str(e)}), 500

@app.route('/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    audio_path = os.path.join(os.getenv('AUDIO_FOLDER'), filename)

    try:
        # Pastikan file audio ada
        if os.path.exists(audio_path):
            return send_file(audio_path, as_attachment=True)
        else:
            return jsonify({"error": "Audio file not found"}), 404

    except Exception as e:
        logging.error("Error serving audio file: %s", e)
        return jsonify({"error": str(e)}), 500

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    original_text = request.form['original_text']

    try:
        # Baca dan proses audio
        audio = AudioSegment.from_file(io.BytesIO(file.read()), format="wav")
        audio = audio.set_frame_rate(16000).set_channels(1)
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)

        # Persiapkan input untuk model
        input_values = processor(samples, sampling_rate=16000, return_tensors="pt").input_values
        with torch.no_grad():
            logits = model(input_values).logits

        # Dapatkan hasil prediksi
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.decode(predicted_ids[0])

        # Bandingkan transkripsi dengan teks asli
        differences, accuracy, error_rate = compare_texts(original_text, transcription)

        # Generate nama file unik dan simpan audio
        audio_filename = f"{uuid.uuid4()}.wav"
        audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
        audio.export(audio_path, format="wav")  # Simpan file audio di folder lokal

        # Simpan data ke database dengan path file
        try:
            save_to_database(audio_path, original_text, transcription, differences, accuracy, error_rate)
        except Exception as db_error:
            logging.error("Error saving to database: %s", db_error)

        # Kembalikan hasil dalam bentuk JSON
        return jsonify({
            "transcription": transcription,
            "differences": differences,
            "accuracy": accuracy,
            "error_rate": error_rate,
            "audio_path": audio_path
        })

    except Exception as e:
        logging.error("Error during transcription: %s", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG') == 'True', host='0.0.0.0')
