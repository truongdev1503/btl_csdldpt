import os
from store_features import store_segment_features
from search_music import search_music

def main():
    dataset_dir = "C:\\Truong\\nam4\\kì 2\\CSDL-DPT\\BTL_Sound\\dataset\\train"
    conn_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=TRUONGCUTE;DATABASE=MusicDatabase;Trusted_Connection=yes;"
    input_file = "C:\\Truong\\nam4\\kì 2\\CSDL-DPT\\BTL_Sound\\dataset\\test\\test5.wav"
    
    # Kiểm tra file input có tồn tại không
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist. Please check the path or use a different file.")
        return
    
    print("Storing features to SQL Server...")
    store_segment_features(dataset_dir, conn_string, segment_duration=10.0, hop_size=7.5, n_mfcc=40)
    
    print("Searching for similar songs...")
    top_matches = search_music(input_file, conn_string, top_k=3, n_mfcc=40, segment_duration=10.0, hop_size=7.5)

if __name__ == "__main__":
    main()