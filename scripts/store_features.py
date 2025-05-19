import os
import pyodbc
import struct

def store_segment_features(dataset_dir, conn_string, segment_duration=5.0):
    conn = pyodbc.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute('''IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Songs')
                      CREATE TABLE Songs (
                          SongID INT PRIMARY KEY IDENTITY(1,1),
                          Filename NVARCHAR(255),
                          SegmentIndex INT,
                          Features VARBINARY(MAX)
                      )''')
    
    from extract_features import extract_segment_features
    for filename in os.listdir(dataset_dir):
        if filename.lower().endswith(('.wav', '.WAV')):
            file_path = os.path.join(dataset_dir, filename)
            try:
                features_list = extract_segment_features(file_path, segment_duration)
                for idx, features in enumerate(features_list):
                    # Chuyển danh sách số thành bytes
                    features_bytes = b''.join(struct.pack('<d', f) for f in features)
                    cursor.execute("INSERT INTO Songs (Filename, SegmentIndex, Features) VALUES (?, ?, ?)",
                                  (filename, idx, features_bytes))
                    print(f"Stored features for {filename}, segment {idx}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    conn.commit()
    conn.close()