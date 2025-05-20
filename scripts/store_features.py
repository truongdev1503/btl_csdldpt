import os
import pyodbc
import numpy as np

def store_segment_features(dataset_dir, conn_string, segment_duration=10.0, hop_size=7.5, n_mfcc=20):
    conn = pyodbc.connect(conn_string)
    cursor = conn.cursor()
    
    # Xóa bảng Songs cũ nếu tồn tại và log
    cursor.execute("DROP TABLE IF EXISTS Songs")
    print("Dropped table Songs successfully.")
    
    # Tạo lại bảng Songs với cột Duration
    cursor.execute('''CREATE TABLE Songs (
                        SongID INT PRIMARY KEY IDENTITY(1,1),
                        Filename NVARCHAR(255),
                        SegmentIndex INT,
                        Features VARBINARY(MAX),
                        Duration FLOAT
                     )''')
    print("Created table Songs successfully.")
    conn.commit()
    
    from extract_features import extract_segment_features
    processed_files = set()
    for filename in os.listdir(dataset_dir):
        if filename.lower().endswith(('.wav', '.WAV')) and filename not in processed_files:
            file_path = os.path.join(dataset_dir, filename)
            try:
                features_list, duration = extract_segment_features(file_path, segment_duration, hop_size, n_mfcc=n_mfcc)
                for idx, features in enumerate(features_list):
                    if features.dtype != np.float64:
                        features = features.astype(np.float64)
                    features_bytes = features.tobytes()
                    cursor.execute("INSERT INTO Songs (Filename, SegmentIndex, Features, Duration) VALUES (?, ?, ?, ?)",
                                 (filename, idx, features_bytes, duration))
                    conn.commit()
                processed_files.add(filename)
                print(f"Processed and stored features for {filename} with duration {duration:.2f}s.")
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    cursor.execute("SELECT COUNT(*) FROM Songs")
    final_count = cursor.fetchone()[0]
    if final_count == 0:
        print("Warning: No data was stored in the Songs table.")
    else:
        print(f"Total rows stored in Songs table: {final_count}")
    conn.close()