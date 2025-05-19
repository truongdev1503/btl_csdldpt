import os
import pyodbc
from extract_features import extract_segment_features

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
    
    for filename in os.listdir(dataset_dir):
        if filename.endswith('.wav') or filename.endswith('.WAV'):
    # Xử lý file
            file_path = os.path.join(dataset_dir, filename)
            features_list = extract_segment_features(file_path, segment_duration)
            for idx, features in enumerate(features_list):
                cursor.execute("INSERT INTO Songs (Filename, SegmentIndex, Features) VALUES (?, ?, ?)",
                              (filename, idx, features.tobytes()))
    conn.commit()
    conn.close()