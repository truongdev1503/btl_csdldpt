# Music Search Project

Hệ thống tìm kiếm bản nhạc bằng âm thanh sử dụng SQL Server và Cosine Similarity, với kỹ thuật chia segment.

## Yêu cầu

- Python 3.9+
- SQL Server Express
- ODBC Driver 17 for SQL Server
- Thư viện: librosa, numpy, pyodbc, scikit-learn

## Cài đặt

1. Cài đặt Python và SQL Server.
2. Cài đặt thư viện:
   ```bash
   pip install -r requirements.txt
   ```

## Chỉnh sửa trong file main

conn_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=server_name;DATABASE=MusicDatabase;Trusted_Connection=yes;"

chỉnh sửa server_name cho đúng trong SQL server management
