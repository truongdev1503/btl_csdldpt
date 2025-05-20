import os
import pyodbc
import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from sklearn.preprocessing import MinMaxScaler

def search_music(input_file, conn_string, top_k=3, n_mfcc=40, segment_duration=10.0, hop_size=7.5):
    conn = pyodbc.connect(conn_string)
    cursor = conn.cursor()
    
    # Trích xuất đặc trưng từ file truy vấn
    from extract_features import extract_segment_features
    features_list, input_duration = extract_segment_features(input_file, segment_duration=segment_duration, hop_size=hop_size, n_mfcc=n_mfcc, silence_threshold=-50.0)
    if not features_list:
        print(f"Error: No features extracted from {input_file}. Please check the file.")
        conn.close()
        return []
    
    input_mfcc = features_list[0]  # Lấy segment đầu tiên của file truy vấn (ma trận MFCC)
    is_silent = input_mfcc.shape[1] == 1 and np.all(input_mfcc == 0)  # Kiểm tra file silent

    # Chuẩn hóa riêng cho file truy vấn
    scaler_input = MinMaxScaler()
    input_mfcc_normalized = scaler_input.fit_transform(input_mfcc)

    # Lấy tất cả đặc trưng từ database
    cursor.execute("SELECT Filename, SegmentIndex, Features, Duration FROM Songs")
    songs_data = cursor.fetchall()
    
    # Chuẩn bị dữ liệu dataset và chuẩn hóa riêng
    all_mfcc_dataset = [np.frombuffer(features_bytes, dtype=np.float64).reshape(n_mfcc, -1) for _, _, features_bytes, _ in songs_data]
    scaler_dataset = MinMaxScaler()
    all_mfcc_dataset_normalized = [scaler_dataset.fit_transform(mfcc) for mfcc in all_mfcc_dataset]
    
    # Lưu số frame của từng ma trận MFCC
    frame_counts = [mfcc.shape[1] for mfcc in all_mfcc_dataset]
    
    distances = []
    raw_distances = []  # Lưu raw DTW distances trước khi áp ngưỡng
    for i, (filename, segment_idx, _, _) in enumerate(songs_data):
        mfcc = all_mfcc_dataset_normalized[i]
        
        # Nếu file truy vấn là silent, gán độ tương đồng 0
        if is_silent:
            distance = 100.0
            raw_distance = 100.0
        else:
            # Tính DTW với raw distance
            raw_distance, _ = fastdtw(input_mfcc_normalized.T, mfcc.T, dist=euclidean)
            raw_distances.append(raw_distance)
            # Đặt ngưỡng bằng DTW_distance trung bình
            threshold = max(np.mean(raw_distances) if raw_distances else 50.0, 50.0)
            distance = max(raw_distance, threshold)
            distance = min(distance, 1000.0)  # Giới hạn tối đa 1000.0
        distances.append((filename, segment_idx, distance, raw_distance))
    
    # Chuẩn hóa khoảng cách DTW thành độ tương đồng (dựa trên raw_distances)
    if raw_distances and not is_silent:
        dtw_min = min(raw_distances)
        dtw_max = max(raw_distances)
        if dtw_max == dtw_min:
            dtw_max = dtw_min + 1e-10  # Tránh chia cho 0
    else:
        dtw_min = 0.0
        dtw_max = 100.0
    
    similarities = []
    for filename, segment_idx, distance, raw_distance in distances:
        # Chuẩn hóa khoảng cách DTW thành độ tương đồng [0, 1]
        similarity = 1 - (distance - dtw_min) / (dtw_max - dtw_min) if dtw_max > dtw_min else 0.0
        similarities.append((filename, segment_idx, similarity, raw_distance))
    
    # Nhóm theo tên file và chọn segment có độ tương đồng cao nhất
    file_similarities = {}
    for filename, segment_idx, similarity, raw_distance in similarities:
        if filename not in file_similarities or similarity > file_similarities[filename][1]:
            file_similarities[filename] = (segment_idx, similarity, raw_distance)
    
    # Chuyển về danh sách và sắp xếp theo độ tương đồng
    unique_similarities = [(filename, segment_idx, similarity, raw_distance) for filename, (segment_idx, similarity, raw_distance) in file_similarities.items()]
    unique_similarities.sort(key=lambda x: x[2], reverse=True)
    
    # Lấy top k
    top_similar = unique_similarities[:top_k]
    
    # Phân tích lý do độ tương đồng lớn
    if raw_distances and not is_silent:
        avg_raw_distance = np.mean(raw_distances)
        min_raw_distance = min(raw_distances)
        print("\n=== Phân tích độ tương đồng ===")
        if min_raw_distance < 1.0:
            print("Lý do tiềm ẩn: Khoảng cách DTW rất nhỏ (< 1.0), có thể do:")
            print("- File truy vấn (`classical2.WAV`) trùng lặp hoặc gần giống với file trong dataset (ví dụ: blues.00015.wav).")
            print("- Chuẩn hóa làm mất sự khác biệt giữa các file.")
            print("Đề xuất: Kiểm tra thủ công `classical2.WAV` với blues.00015.wav bằng phần mềm âm thanh.")
        elif avg_raw_distance < threshold:
            print("Lý do tiềm ẩn: Khoảng cách DTW trung bình thấp (< threshold), có thể do:")
            print("- Đặc trưng MFCC của `classical2.WAV` và dataset quá tương đồng sau chuẩn hóa.")
            print("- Dataset không đủ đa dạng để phân biệt thể loại.")
            print("Đề xuất: Kiểm tra sự đa dạng của dataset hoặc điều chỉnh ngưỡng DTW.")
        else:
            print("Lý do tiềm ẩn: Ngưỡng DTW_distance (trung bình) có thể không đủ để phân biệt thể loại.")
            print("Đề xuất: Tăng ngưỡng DTW_distance (ví dụ: 800.0) hoặc tăng n_mfcc để cải thiện đặc trưng.")
        print(f"- DTW_distance trung bình: {avg_raw_distance:.2f}")
        print(f"- DTW_distance nhỏ nhất: {min_raw_distance:.2f}")
        print(f"- Ngưỡng DTW_distance động: {threshold:.2f}")

    # Trích xuất thông tin bổ sung cho output
    print(f"\nInput song: {os.path.basename(input_file)}")
    print(f"Duration: {input_duration:.2f} seconds")
    print("Top 3 file âm thanh giống nhất:")
    for filename, segment_idx, similarity, raw_distance in top_similar:
        # Trích xuất thể loại từ tên file
        genre = filename.split('.')[0]
        # Tính khoảng thời gian của segment
        start_time = segment_idx * hop_size
        end_time = start_time + segment_duration
        # Lấy thời lượng từ database
        for db_filename, _, _, duration in songs_data:
            if db_filename == filename:
                file_duration = duration
                break
        else:
            file_duration = 0.0
        print(f"File: {filename}, Genre: {genre}, Segment: {segment_idx} ({start_time:.1f}s - {end_time:.1f}s), "
              f"Duration: {file_duration:.2f}s, Raw DTW Distance: {raw_distance:.2f}, Độ tương đồng: {similarity:.4f}")
    
    conn.close()
    return top_similar