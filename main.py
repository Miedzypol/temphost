from bottle import route, run, request, static_file
import sqlite3, threading
import os, time, random, platform, string
import subprocess

# for future: http://localhost:3138/download?id=12987789&token=jkLOsmJM4jfN mam nadzieje że to sie nie spierdoli
# em, nie zjebało się :D

# DEFAULT VARIABLES
dirChar = '/'
logServerInfo = True
uploadDirectory = 'C:\\Users\\olekt\\Desktop\\temphost\\uploadedFiles\\'

# Global database lock
dbLock = threading.Lock()

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
    saveToLogDB('STARTUP', 'BACKEND SERVER STARTUP', f'STARTED SUCCESSFULLY ON {platform.system()}')
    saveToLogDB('STARTUP', 'MACHINE SPECS', f'CPU: {platform.machine()} OS: {platform.system()} RELEASE: {platform.release()}')
    return 0

if platform.system() == "Windows":
    dirChar = '\\'
elif platform.system() == "Linux":
    dirChar = '/'
else:
    print('''[WARNING]: SERVER SYSTEM IS NOT SUPPORTED. PLEASE USE WINDOWS OR LINUX.
          SETTING dirChar TO / (default option. You can change it in code by changing dirChar
          in DEFAULT VARIABLES section on top of the file)

          !!! THIS WARNING WOULD BE LOGGED !!!''')
    saveToLogDB('STARTUP', 'SERVER SYSTEM WARNING', 'SYSTEM NOT SUPPORTED')

ROOTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
FILE_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'db{dirChar}fileStorage.db')
BAN_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'db{dirChar}banned.db')
LOG_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'db{dirChar}logs.db')
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


'''try:
    subprocess.run([f'python3 {ROOTDIR}{dirChar}fileScanner.py', '-l']) 
except FileNotFoundError:
    saveToLogDB('ERROR', 'ERROR RUNNING fileScanner.py', 'FileNotFoundError')
    print(f'python3 {ROOTDIR}{dirChar}fileScanner.py')
except:
    saveToLogDB('ERROR', 'ERROR RUNNING fileScanner.py', 'OTHER ERROR')
    print('error')'''

@route("/")
def index():
    return static_file(f'html{dirChar}index.html', root='.')

@route('/download')
def download():
    downloadFileID = request.query.get('id')
    downloadFileToken = request.query.get('token')
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

@route('/upload', method='POST') #napraw toooooooooooooooooooooooooooooooooooooooooo T-T
def upload():
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
    return f'''File ID: {dbFileID} | File Token (PASSWORD FOR FILE): {dbFileToken}''' #for devs: localhost:3138/download?id={dbFileID}&token={dbFileToken}

run(host='localhost', port=3138)