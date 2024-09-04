import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
from textblob import TextBlob
import wave
import io
from pydub import AudioSegment

app = Flask(__name__)
CORS(app)

def convert_to_wav(audio_file):
    try:
        audio = AudioSegment.from_file(audio_file)
        wav_io = io.BytesIO()
        audio.export(wav_io, format='wav')
        wav_io.seek(0)
        return wav_io
    except Exception as e:
        raise ValueError(f"Error converting file to WAV: {str(e)}")
    
def calculate_audio_duration(audio_file):
    with wave.open(audio_file, 'rb') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        duration = frames / float(rate)
    return duration

def calculate_words_per_minute(transcript, duration):
    words = len(transcript.split())
    minutes = duration / 60.0
    return round(words / minutes)

def calculate_filler_words(transcript):
    filler_words = ['um', 'uh', 'like', 'you know', 'so', 'actually', 'basically']
    words = transcript.lower().split()
    fillers = [word for word in words if word in filler_words]
    return fillers

def calculate_pace(transcript, duration):
    words = len(transcript.split())
    return 'fast' if words / duration > 2.5 else 'slow' if words / duration < 1.5 else 'medium'

def analyze_tone(transcript):
    blob = TextBlob(transcript)
    polarity = blob.sentiment.polarity
    return 'positive' if polarity > 0.1 else 'negative' if polarity < -0.1 else 'neutral'


@app.route('/analyze', methods=['POST'])
def analyze_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    audio_file = request.files['file']

    # Check if the file is a valid WAV file
    if not audio_file.filename.endswith('.wav'):
        return jsonify({'error': 'Invalid file type. Please upload a WAV file.'}), 400

    try:
        # Convert to WAV format if necessary
        audio_file = convert_to_wav(audio_file)

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)

        transcript = recognizer.recognize_google(audio)
        duration = len(audio.frame_data) / (audio.sample_rate * audio.sample_width)

        words_per_minute = calculate_words_per_minute(transcript, duration)
        filler_words = calculate_filler_words(transcript)
        pace = calculate_pace(transcript, duration)
        tone = analyze_tone(transcript)

        analysis = {
            'text': transcript,
            'words_per_minute': words_per_minute,
            'filler_words': filler_words,
            'tone': tone,
            'pace': pace,
        }

        return jsonify(analysis), 200

    except sr.UnknownValueError:
        return jsonify({'error': 'Speech recognition could not understand audio'}), 400
    except sr.RequestError:
        return jsonify({'error': 'Could not request results from Google Speech Recognition service'}), 500
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze_microphone', methods=['POST'])
def analyze_microphone():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    audio_file = request.files['file']

    # Check if the file is a valid WAV file
    if not audio_file.filename.endswith('.wav'):
        return jsonify({'error': 'Invalid file type. Please upload a WAV file.'}), 400

    try:
        # Convert to WAV format if necessary
        audio_file = convert_to_wav(audio_file)

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)

        transcript = recognizer.recognize_google(audio)
        duration = len(audio.frame_data) / (audio.sample_rate * audio.sample_width)

        words_per_minute = calculate_words_per_minute(transcript, duration)
        filler_words = calculate_filler_words(transcript)
        pace = calculate_pace(transcript, duration)
        tone = analyze_tone(transcript)

        analysis = {
            'text': transcript,
            'words_per_minute': words_per_minute,
            'filler_words': filler_words,
            'tone': tone,
            'pace': pace,
        }

        return jsonify(analysis), 200

    except sr.UnknownValueError:
        return jsonify({'error': 'Speech recognition could not understand audio'}), 400
    except sr.RequestError:
        return jsonify({'error': 'Could not request results from Google Speech Recognition service'}), 500
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
