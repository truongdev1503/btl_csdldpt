import pyodbc
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from extract_features import extract_segment_features

def search_music(input_file, conn_string, segment_duration=5.0):
    input_features_list = extract_segment_features(input_file, segment_duration)
    if not input_features_list:
        return []
    
    conn = pyodbc.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute("SELECT SongID, Filename, SegmentIndex, Features FROM Songs")
    results = cursor.fetchall()
    conn.close()
    
    file_similarities = {}
    for song_id, filename, segment_index, features_blob in results:
        features = np.frombuffer(features_blob, dtype=np.float64).reshape(1, -1)
        max_similarity = 0
        for input_features in input_features_list:
            input_features = input_features.reshape(1, -1)
            similarity = cosine_similarity(input_features, features)[0][0]
            max_similarity = max(max_similarity, similarity)
        
        if filename in file_similarities:
            file_similarities[filename] = max(file_similarities[filename], max_similarity)
        else:
            file_similarities[filename] = max_similarity
    
    similarities = [(filename, sim) for filename, sim in file_similarities.items()]
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:3]