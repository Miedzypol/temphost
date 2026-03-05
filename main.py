from bottle import route, run, request, static_file
import sqlite3, threading
import os, time, random, platform, string
import confidential

appVersion = "1.0.4.1 (Small Fix)"

# New things in 1.0.4.1 (small fix):
# Separated JS, CSS from HTML oon front;endd
# Variables were in a bad order, causing the server to not work on every machine
# cleanup.runPeriodically() was set to 3 seconds, I just forgot to change it back. Now it is 480 seconds

# New features that would be in 1.1:
# - Finished Server console
# - Scanning if user was banned
# - More security measures & overall better database security
# - Cleaned and optimized code
# - Server installator for Linux and Windows.

# Planned features in 1.2:
# - Scanning user's files looking for illegal images, videos and other data
# - Better and cleaner Front-End
# - Multiple QoL Features, like automatic key generator for confidential.py

dirChar = '/'
systemNotSupported = False


if platform.system() == "Windows":
    dirChar = '\\'
elif platform.system() == "Linux":
    dirChar = '/'
else:
    print('''[WARNING]: SERVER SYSTEM IS NOT SUPPORTED. PLEASE USE WINDOWS OR LINUX.
          SETTING dirChar TO / (default option. You can change it in code by changing dirChar
          in DEFAULT VARIABLES section on top of the file)

          !!! THIS WARNING WOULD BE LOGGED !!!''')
    systemNotSupported = True

ROOTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
FILE_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'db{dirChar}fileStorage.db')
BAN_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'db{dirChar}banned.db')
LOG_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'db{dirChar}logs.db')

# Here are some variables you can change. Alternatively use 'config {command}' in server console. <<< DOESNT WORK CURRENTLY
logServerInfo = True
uploadDirectory = f'{ROOTDIR}{dirChar}uploadedFiles'






dbLock = threading.Lock()

class DatabaseCleanup:
    def __init__(self, dbPath, uploadFolder):
        self.dbPath = dbPath
        self.uploadFolder = uploadFolder

    def checkAndCleanDatabase(self):
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
                    print(f"File '{fileName}' not found.")
                    cursor.execute("DELETE FROM files WHERE fileID=?", (fileID,))
                    continue

                if expireTime and float(expireTime) < time.time():
                    print(f"File '{fileName}' has expired.")
                    try:
                        os.remove(filePath)
                    except OSError as e:
                        print(f"Error deleting file '{fileName}': {e}")
                    cursor.execute("DELETE FROM files WHERE fileID=?", (fileID,))
            conn.commit()
            conn.close()
            saveToLogDB('INFO', 'DATABASE CLEANUP', 'SUCCESS')

        except sqlite3.Error as e:
            print(f"SQLite Kaput: {e}")

    def runPeriodically(self, interval):
        self.checkAndCleanDatabase()
        threading.Timer(interval, self.runPeriodically, [interval]).start()


def ffo(fileName, ffoType):  # fast file operation
    file = open(f'{ROOTDIR}{dirChar}{fileName}', ffoType)
    content = file.read(10)
    print(content)
    file.close()

def randomStr(nrange, type="letters"):
    randomStrCharSet = {
        "letters": string.ascii_lowercase,
        "rletters": string.ascii_letters,
        "cletters": string.ascii_uppercase,
        "num": string.digits,
        "alphanum": string.ascii_lowercase + string.digits,
        "ralphanum": string.ascii_letters + string.digits,
        "calphanum": string.ascii_uppercase + string.digits,
    }
    randomStrChars = randomStrCharSet.get(type, string.ascii_lowercase)
    return ''.join(random.choice(randomStrChars) for _ in range(nrange))

def saveToLogDB(type, desc, res):
    try:
        with dbLock:
            conn = sqlite3.connect(LOG_DB, check_same_thread=False, timeout=10)
            cursor = conn.cursor()
            if res is None:
                res = "NOT PROVIDED"
            cursor.execute(
                'INSERT INTO logs (type, date, description, result) VALUES (?,?,?,?)',
                (type, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), desc, res)
            )
            conn.commit()
            conn.close()
        return 'LOGGED SUCCESSFULLY'
    except Exception as e:
        return f'ERROR WHILE LOGGING: {str(e)}'

def serverStartup():
    startupResult = saveToLogDB('STARTUP', 'BACKEND SERVER STARTUP', 'FUNCTION TEST')
    if startupResult == 'ERROR WHILE LOGGING':
        print('STARTUP EXIT WITH CODE 1. CHECK saveToLogDB()')
        exit()
    if systemNotSupported==True:
            saveToLogDB('STARTUP', 'MACHINE WARNING', 'SYSTEM NOT SUPPORTED')
    saveToLogDB('STARTUP', 'BACKEND SERVER STARTUP', f'STARTED SUCCESSFULLY ON {platform.system()}')
    saveToLogDB('STARTUP', 'MACHINE SPECS', f'CPU: {platform.machine()} OS: {platform.system()} RELEASE: {platform.release()}')
    return 0




with dbLock:
    conn = sqlite3.connect(FILE_DB, check_same_thread=False, timeout=10)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.close()

    conn = sqlite3.connect(FILE_DB, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fileName TEXT, fileID TEXT, accessToken TEXT, expireTime TEXT, verified TEXT
    )
    ''')
    conn.commit()
    conn.close()

    conn = sqlite3.connect(BAN_DB, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS banned (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        userIP TEXT, banned TEXT
    )
    ''')
    conn.close()

    conn = sqlite3.connect(LOG_DB, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT, date TEXT, description TEXT, result TEXT
    )
    ''')
    conn.close()

serverStartup()

@route("/")
def index():
    return static_file(f'html{dirChar}index.html', root='.')

@route('/download')
def download():
    downloadFileID = request.query.get('id')
    downloadFileToken = request.query.get('token')
    if downloadFileID == '/dbTest banMyIP':
        uploadUserIP = request.environ.get('REMOTE_ADDR')
        with dbLock:
            conn = sqlite3.connect(BAN_DB, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO banned (userIP, banned) VALUES (?, '1')", (confidential.encrypt(uploadUserIP.encode()),))
            conn.commit()
            conn.close()
        return "aight bro ur baned"
    if not downloadFileID or not downloadFileToken:
        saveToLogDB('DOWNLOAD','TRYING TO DOWNLOAD A FILE','ERROR: MISSING FIELDS')
        return 'downloadFileID or downloadFileToken is blank'
    conn = sqlite3.connect(FILE_DB, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT accessToken, fileName FROM files WHERE fileID = ?", (int(downloadFileID),))
    downloadDBSearchResult = cursor.fetchone()
    conn.close()
    print(downloadDBSearchResult)
    if downloadDBSearchResult:
        if downloadFileToken==downloadDBSearchResult[0]:
            saveToLogDB('DOWNLOAD','TOKEN MATCHES DB RECORD CONDITION', f'SUCCESS {downloadDBSearchResult[1]}')
            return static_file(
                downloadDBSearchResult[1],
                root=f'{ROOTDIR}{dirChar}uploadedFiles{dirChar}',
                download=downloadDBSearchResult[1]
            )
        else:
            saveToLogDB('DOWNLOAD','TOKEN MATCHES DB RECORD CONDITION', f'FAILURE {downloadDBSearchResult[1]}')
            return 'TOKEN DOES NOT MATCH DB RECORD'
    else:
        saveToLogDB('DOWNLOAD','TRYING TO DOWNLOAD A FILE', 'ERROR: FILE NOT FOUND')
        return 'FILE NOT FOUND ERROR'

@route('/upload', method='POST')
def upload():

    uploadUserIP = request.environ.get('REMOTE_ADDR')
    try:
        banConn = sqlite3.connect('db/banned.db')
        banCursor = banConn.cursor()
        banCursor.execute("SELECT userIP FROM banned WHERE banned = '1'")
        bannedIPs = banCursor.fetchall()
        banConn.close()
        
        for bannedIP in bannedIPs:
            foundIP = bannedIP[0]
            IPScanResult = confidential.checkUser(foundIP, uploadUserIP)
            if IPScanResult == "User banned":
                return "bradar ur banned bradar pak ju bradar"
    except Exception as e:
        saveToLogDB('UPLOAD', 'CHECKING BANNED IPS', f'ERROR: {str(e)}')
    
    file = request.files.get('file')
    if not file:
        return "No file uploaded."

    max_size = 150 * 1024 * 1024
    file.file.seek(0, os.SEEK_END)
    file_length = file.file.tell()
    file.file.seek(0)

    if file_length > max_size:
        saveToLogDB('INFO', f'FILE UPLOAD IN SIZE {file_length}B', 'FAILURE; FILE EXCEEDS 150MB')
        return 'File size exceeds 150MB.'

    originalName = file.filename
    trashVariable, ext = os.path.splitext(originalName)
    newFilename = f"{randomStr(16, 'alphanum')}{ext}"
    savePath = os.path.join(uploadDirectory, newFilename)
    os.makedirs(uploadDirectory, exist_ok=True)
    file.save(savePath)

    dbFileID = randomStr(8, 'num')
    dbFileToken = randomStr(12, 'ralphanum')

    with dbLock:
        conn = sqlite3.connect(FILE_DB, check_same_thread=False, timeout=10)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO files (fileName, fileID, accessToken, expireTime, verified) VALUES (?,?,?,?,?)',
            (newFilename, dbFileID, dbFileToken, time.time() + 86400, False)
        )
        conn.commit()
        conn.close()

    saveToLogDB('INFO', f'FILE UPLOAD IN SIZE {file_length}B', 'SUCCESS')
    return f'File ID: {dbFileID} | File Token (PASSWORD FOR FILE): {dbFileToken}'

isServerRunning = True

def runServer():
    try:
        run(host='0.0.0.0', port=3138, quiet=True)
    except KeyboardInterrupt:
        pass

uploadFolder = os.path.join(ROOTDIR, "uploadedFiles")
os.makedirs(uploadFolder, exist_ok=True)
cleanup = DatabaseCleanup(FILE_DB, uploadFolder)
cleanup.runPeriodically(480)

serverThread = threading.Thread(target=runServer, daemon=True)
serverThread.start()
print("Server started on http://localhost:3138")
print(f'NanoCloud Initiative | TempHost v{appVersion} is running. Use "help" for command\'s list\n')
try:
    while isServerRunning:
        try:
            command = input(">> ").strip().lower()
            if command == "help":
                print(f'''Available commands (warning - most of them don't work currently):
                      server stop - stops the server
                      config allowLogging [true/false] - turn on server's logging
                      config logDetailedInfo [true/false] - allow logging more detailed info
                      user ban [IP] - banns user's IP adress
                      ''')
            pass
        except KeyboardInterrupt:
            print("\nByeeeee!")
            isServerRunning = False
            exit()
except Exception as e:
    print(f"Error in command loop: {e}")
    isServerRunning = False
