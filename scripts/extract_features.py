import wave
import struct

def extract_segment_features(file_path, segment_duration=5.0):
    # Mở file WAV
    with wave.open(file_path, 'rb') as wav_file:
        # Lấy thông số file
        n_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frame_rate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
        
        # Tính số mẫu trong một đoạn
        segment_samples = int(frame_rate * segment_duration)
        n_segments = n_frames // segment_samples
        
        # Đọc toàn bộ dữ liệu thô
        raw_data = wav_file.readframes(n_frames)
        # Chuyển đổi dữ liệu thô thành danh sách giá trị (cho định dạng 16-bit)
        if sample_width == 2:  # 16-bit audio
            samples = [struct.unpack('<h', raw_data[i:i+2])[0] for i in range(0, len(raw_data), 2)]
        else:
            raise ValueError("Chỉ hỗ trợ định dạng 16-bit hiện tại")
        
        # Tính vector đặc trưng thủ công cho từng đoạn
        features_list = []
        for i in range(n_segments):
            start_idx = i * segment_samples
            end_idx = min((i + 1) * segment_samples, n_frames)
            segment = samples[start_idx:end_idx]
            if len(segment) < segment_samples // 2:  # Bỏ qua đoạn quá ngắn
                continue
                
            # Tính trung bình biên độ
            avg_amplitude = sum(abs(s) for s in segment) / len(segment) if segment else 0
            
            # Tính biến thiên biên độ (phương sai đơn giản)
            if len(segment) > 1:
                variance = sum((s - avg_amplitude) ** 2 for s in segment) / len(segment)
            else:
                variance = 0
            
            # Kết hợp đặc trưng (trung bình và biến thiên)
            features = [avg_amplitude, variance]
            features_list.append(features)
        
        return features_list