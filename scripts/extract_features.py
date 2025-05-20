import librosa
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def extract_segment_features(file_path, segment_duration=10.0, hop_size=7.5, sr=22050, n_mfcc=40, silence_threshold=-50.0):
    try:
        # Load file âm thanh
        audio, sr = librosa.load(file_path, sr=sr, mono=True)
        audio_duration = len(audio) / sr
        
        # Kiểm tra file silent dựa trên mức năng lượng (dB)
        rms = librosa.feature.rms(y=audio)
        energy_db = 20 * np.log10(np.mean(rms) + 1e-10)  # Tránh log(0)
        if energy_db < silence_threshold:  # Ngưỡng -50 dB
            return [np.zeros((n_mfcc, 1))], audio_duration  # Trả về ma trận MFCC rỗng và thời lượng
        
        # Chia thành các segment 10 giây với hop size 7.5 giây
        segment_length = int(segment_duration * sr)  # Số mẫu trong 10 giây
        hop_length = int(hop_size * sr)  # Số mẫu trong 7.5 giây
        segments = []
        for start in range(0, len(audio) - segment_length + 1, hop_length):
            end = start + segment_length
            if end > len(audio):
                break  # Bỏ đoạn cuối nếu không đủ 10 giây
            segment = audio[start:end]
            segments.append(segment)
        
        if not segments:
            return [], audio_duration
        
        features_list = []
        for segment in segments:
            # Trích xuất MFCC chuỗi
            mfcc = librosa.feature.mfcc(y=segment, sr=sr, n_mfcc=n_mfcc)
            # Chuẩn hóa z-score trên từng hệ số MFCC
            mfcc_mean = np.mean(mfcc, axis=1, keepdims=True)
            mfcc_std = np.std(mfcc, axis=1, keepdims=True)
            mfcc_std[mfcc_std == 0] = 1e-10  # Tránh chia cho 0
            mfcc_zscore = (mfcc - mfcc_mean) / mfcc_std
            # Chuẩn hóa Min-Max Scaling
            scaler = MinMaxScaler()
            mfcc_normalized = scaler.fit_transform(mfcc_zscore)
            features_list.append(mfcc_normalized)
        
        return features_list, audio_duration
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return [], 0.0