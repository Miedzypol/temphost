import sqlite3
import os
import time
import threading

class DatabaseCleanup:
    def __init__(self, dbPath, uploadFolder):
        self.dbPath = dbPath
        self.uploadFolder = uploadFolder

    def checkAndCleanDatabase(self):
        print(f"[{time.ctime()}] Starting database cleanup...")

        try:
            conn = sqlite3.connect(
                self.dbPath,
                timeout=10,
                isolation_level=None,
                check_same_thread=False
            )
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()
            cursor.execute("SELECT fileID, fileName, expireTime FROM files")
            entries = cursor.fetchall()
            for fileID, fileName, expireTime in entries:
                filePath = os.path.join(self.uploadFolder, fileName)
                if not os.path.exists(filePath):
                    print(f"File '{fileName}' not found. Deleting database entry...")
                    cursor.execute("DELETE FROM files WHERE fileID=?", (fileID,))
                    continue
                if expireTime and float(expireTime) < time.time():
                    print(f"File '{fileName}' has expired. Deleting file and database entry...")
                    try:
                        os.remove(filePath)
                    except OSError as e:
                        print(f"Error deleting file '{fileName}': {e}")
                    cursor.execute("DELETE FROM files WHERE fileID=?", (fileID,))
            conn.commit()
            conn.close()
            print(f"[{time.ctime()}] Database cleanup completed.")

        except sqlite3.Error as e:
            print(f"SQLite error during cleanup: {e}")
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def runPeriodically(self, interval):
        self.checkAndCleanDatabase()
        threading.Timer(interval, self.runPeriodically, [interval]).start()

if __name__ == "__main__":
    baseDir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    dbPath = os.path.join(baseDir, "db/fileStorage.db")
    uploadFolder = os.path.join(baseDir, "uploadedFiles")
    os.makedirs(uploadFolder, exist_ok=True)
    cleanup = DatabaseCleanup(dbPath, uploadFolder)
    cleanup.runPeriodically(240)
    while True:
        time.sleep(1)

