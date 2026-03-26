import sqlite3
import json

conn = sqlite3.connect('attendance_db.sqlite')
cursor = conn.cursor()
cursor.execute("SELECT id, name, face_encoding FROM students")
rows = cursor.fetchall()
found_128 = False
for row in rows:
    id, name, enc_json = row
    if enc_json:
        encs = json.loads(enc_json)
        if encs:
            size_set = {len(enc) for enc in encs}
            if 128 in size_set:
                print(f"FOUND 128D student: {name} (ID {id}) uses 128D encodings!")
                found_128 = True
            if 512 in size_set:
                 print(f"Student {name} (ID {id}) uses 512D.")
if not found_128:
    print("NO 128D students found.")
conn.close()
