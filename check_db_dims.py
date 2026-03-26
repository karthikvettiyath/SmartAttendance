import sqlite3
import json

conn = sqlite3.connect('attendance_db.sqlite')
cursor = conn.cursor()
cursor.execute("SELECT id, name, face_encoding FROM students")
rows = cursor.fetchall()
for row in rows:
    id, name, enc_json = row
    if enc_json:
        encs = json.loads(enc_json)
        if encs:
            sizes = [len(enc) for enc in encs]
            print(f"Student {name} (ID {id}): {len(encs)} encodings, sizes: {set(sizes)}")
        else:
            print(f"Student {name} (ID {id}): No encodings")
    else:
        print(f"Student {name} (ID {id}): No face_encoding (NULL)")
conn.close()
