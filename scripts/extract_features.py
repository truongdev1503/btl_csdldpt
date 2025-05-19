import librosa
import numpy as np

def extract_segment_features(file_path, segment_duration=5.0):
    y, sr = librosa.load(file_path, sr=44100, mono=True)
    segment_samples = int(segment_duration * sr)
    segments = [y[i:i + segment_samples] for i in range(0, len(y), segment_samples)]
    
    features_list = []
    for segment in segments:
        if len(segment) < segment_samples // 2:  # Bỏ qua segment quá ngắn
            continue
        # MFCC
        mfcc = librosa.feature.mfcc(y=segment, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)
        mfcc_std = np.std(mfcc, axis=1)
        
        # Chroma
        chroma = librosa.feature.chroma_stft(y=segment, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        
        # Tempo
        tempo, _ = librosa.beat.beat_track(y=segment, sr=sr)
        
        # Spectral Centroid
        spectral_centroid = librosa.feature.spectral_centroid(y=segment, sr=sr)
        spectral_centroid_mean = np.mean(spectral_centroid)
        
        # Kết hợp đặc trưng
        features = np.concatenate([mfcc_mean, mfcc_std, chroma_mean, [tempo, spectral_centroid_mean]])
        features_list.append(features)
    
    return features_list