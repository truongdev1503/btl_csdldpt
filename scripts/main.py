from store_features import store_segment_features
from search_music import search_music
from extract_features import extract_segment_features
import pyodbc
import os

def main():
    dataset_dir = "C:\\Truong\\nam4\\kì 2\\CSDL-DPT\\BTL_Sound\\dataset\\available_data"
    conn_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=TRUONGCUTE;DATABASE=MusicDatabase;Trusted_Connection=yes;"
    segment_duration = 5.0
    input_file = "C:\\Truong\\nam4\\kì 2\\CSDL-DPT\\BTL_Sound\\dataset\\input_data\\test4.WAV"
    
    # Lưu đặc trưng (chạy lần đầu)
    print("Storing features to SQL Server...")
    store_segment_features(dataset_dir, conn_string, segment_duration)
    
    # Tìm kiếm
    print("Searching for similar songs...")
    top_matches = search_music(input_file, conn_string, segment_duration)
    
    # Trích xuất vector đặc trưng của input file (lấy đoạn đầu để đơn giản)
    input_features_list = extract_segment_features(input_file, segment_duration)
    input_features = input_features_list[0] if input_features_list else []
    
    # In thông tin bài hát input đầu vào
    input_filename = os.path.basename(input_file)
    print(f"\nInput song: {input_filename}")
    print(f"Feature vector: {input_features}")
    
    # In top 3 bài hát giống nhất cùng với vector đặc trưng có độ tương đồng cao nhất
    print("\nTop 3 file âm thanh giống nhất:")
    for filename, similarity, segment_index, features in top_matches:
        print(f"\nFile: {filename}, Độ tương đồng: {similarity:.4f}")
        print(f"Feature vector (segment {segment_index}): {features}")

if __name__ == "__main__":
    main()