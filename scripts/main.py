from store_features import store_segment_features
from search_music import search_music

def main():
    dataset_dir = "C:\\Truong\\nam4\\kì 2\\CSDL-DPT\\BTL_Sound\\dataset\\available_data"
    conn_string = conn_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=TRUONGCUTE;DATABASE=MusicDatabase;Trusted_Connection=yes;"
    segment_duration = 5.0
    input_file = "C:\\Truong\\nam4\\kì 2\\CSDL-DPT\\BTL_Sound\\dataset\\input_data\\test4.WAV"
    
    # Lưu đặc trưng (chạy lần đầu)
    print("Storing features to SQL Server...")
    store_segment_features(dataset_dir, conn_string, segment_duration)
    
    # Tìm kiếm
    print("Searching for similar songs...")
    top_matches = search_music(input_file, conn_string, segment_duration)
    
    print("Top 3 file âm thanh giống nhất:")
    for filename, similarity in top_matches:
        print(f"File: {filename}, Độ tương đồng: {similarity:.4f}")

if __name__ == "__main__":
    main()