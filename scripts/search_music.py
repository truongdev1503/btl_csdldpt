import pyodbc
import struct

def dot_product(vec1, vec2):
    return sum(a * b for a, b in zip(vec1, vec2))

def magnitude(vec):
    return sum(x * x for x in vec) ** 0.5

def cosine_similarity_manual(vec1, vec2):
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot_prod = dot_product(vec1, vec2)
    mag1 = magnitude(vec1)
    mag2 = magnitude(vec2)
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_prod / (mag1 * mag2)

def search_music(input_file, conn_string, segment_duration=5.0):
    # Trích xuất đặc trưng từ file input
    from extract_features import extract_segment_features
    input_features_list = extract_segment_features(input_file, segment_duration)
    if not input_features_list:
        return []
    
    # Kết nối SQL Server
    conn = pyodbc.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute("SELECT SongID, Filename, SegmentIndex, Features FROM Songs")
    results = cursor.fetchall()
    conn.close()
    
    file_similarities = {}
    for song_id, filename, segment_index, features_blob in results:
        # Giải mã dữ liệu bytes thành danh sách số
        features = []
        byte_data = features_blob
        i = 0
        while i < len(byte_data):
            if i + 8 <= len(byte_data):
                value = struct.unpack('<d', byte_data[i:i+8])[0]
                features.append(value)
                i += 8
            else:
                break
        
        # Tìm độ tương đồng cao nhất với từng đoạn input
        max_similarity = 0
        best_segment_idx = 0  # Lưu index của đoạn có độ tương đồng cao nhất
        for idx, input_features in enumerate(input_features_list):
            similarity = cosine_similarity_manual(input_features, features)
            if similarity > max_similarity:
                max_similarity = similarity
                best_segment_idx = idx
        
        if filename in file_similarities:
            if max_similarity > file_similarities[filename][1]:  # Cập nhật nếu độ tương đồng cao hơn
                file_similarities[filename] = (best_segment_idx, max_similarity, segment_index, features)
        else:
            file_similarities[filename] = (best_segment_idx, max_similarity, segment_index, features)
    
    # Sắp xếp và lấy top 3
    similarities = [(filename, sim_info[1], sim_info[2], sim_info[3]) for filename, sim_info in file_similarities.items()]
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:3]