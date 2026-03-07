from bottle import route, run, request, static_file
import sqlite3, threading
import os, time, random, platform, string
import confidential
from configparser import ConfigParser
import analyticUtils as au

config = ConfigParser()
config.read("config.ini")
appVersion = "1.0.4.3"
trashVariable = 'hey im trash'

# New things in 1.0.4.3:
# Migrated fileStorage.db from sqlite3 to PostgreSQL
# Every 1200 seconds it should scan the database looking for files that match NSRL's hash list, banning IP's if it was illegal
# Added config.ini 

# New features that would be in 1.1:
# - [halfly done in 1.0.4.2]Finished Server console
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
FILE_DB = os.path.join(ROOTDIR, f'db{dirChar}fileStorage.db')
IP_DB = os.path.join(ROOTDIR, f'db{dirChar}banned.db')
LOG_DB = os.path.join(ROOTDIR, f'db{dirChar}logs.db')
ANALYTICS_DB = os.path.join(ROOTDIR, f'db{dirChar}analytics.db')
os.makedirs(f'{ROOTDIR}{dirChar}db', exist_ok=True)

logServerInfo = True
uploadDirectory = f'{ROOTDIR}{dirChar}uploadedFiles' 
maxFileSize = 150 * 1024 * 1024 # change this to change upload max size. Default : 150MB






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
    if config['server'].getboolean('allowLogging', fallback=True) == False:
        return 'LOGGING DISABLED'
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

def saveToAnalyticsDB(type, desc, res):
    try:
        with dbLock:
            conn = sqlite3.connect(ANALYTICS_DB, check_same_thread=False, timeout=10)
            cursor = conn.cursor()
            if res is None:
                res = "NOT PROVIDED"
            cursor.execute(
                'INSERT INTO analytics (type, date, description, result, machineStats) VALUES (?,?,?,?,?)',
                (type, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), desc, res, str(au.getPreparedTable()))
            )
            conn.commit()
            conn.close()
        return 'LOGGED SUCCESSFULLY'
    except Exception as e:
        return f'ERROR WHILE LOGGING: {str(e)}'

def analytics(analType):
    if config['server'].getboolean('allowAnalytics', fallback=False) == False:
        return 'LOGGING DISABLED'
    if analType == 'upload':
        return saveToAnalyticsDB('UPLOAD', 'UPLOADED FILE', None)
    elif analType == 'download':
        return saveToAnalyticsDB('DOWNLOAD', 'DOWNLOADED FILE', None)
    elif analType == 'auto':
        return saveToAnalyticsDB('AUTO', 'AUTOLOG', None)
    return 'SUCCESS'
def analyticsInterval():
    while True:
        analytics('auto')
        time.sleep(config['server'].getint('autoAnalyticsInterval', fallback=1800))
        

def serverStartup():
    startupResult = saveToLogDB('STARTUP', 'BACKEND SERVER STARTUP', 'FUNCTION TEST')
    if startupResult == 'ERROR WHILE LOGGING':
        print('STARTUP EXIT WITH CODE 1. CHECK saveToLogDB()')
        exit()
    if systemNotSupported==True:
            saveToLogDB('STARTUP', 'MACHINE WARNING', 'SYSTEM NOT SUPPORTED')
    saveToLogDB('STARTUP', 'BACKEND SERVER STARTUP', f'STARTED SUCCESSFULLY ON {platform.system()}')
    saveToLogDB('STARTUP', 'MACHINE SPECS', f'CPU: {platform.machine()} OS: {platform.system()} RELEASE: {platform.release()}')
    return None




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

    conn = sqlite3.connect(IP_DB, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ipdb (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        userIP TEXT, banned TEXT, canUploadAfter TEXT
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

    conn = sqlite3.connect(ANALYTICS_DB, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT, date TEXT, description TEXT, result TEXT, machineStats TEXT
    )
    ''')
    conn.close()

serverStartup()

@route("/")
def index():
    return static_file(f'html{dirChar}index.html', root='.')\

@route('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root=os.path.join(ROOTDIR, 'html'))

@route('/download')
def download():
    downloadFileID = request.query.get('id')
    downloadFileToken = request.query.get('token')
    if downloadFileID == '/dbTest banMyIP':
         
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
        banConn = sqlite3.connect(IP_DB)
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

    file.file.seek(0, os.SEEK_END)
    file_length = file.file.tell()
    file.file.seek(0)

    if file_length > maxFileSize:
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
            (newFilename, dbFileID, dbFileToken, time.time() + config['user'].getint('deleteFilesAfter', fallback=86400), False)
        )
        conn.commit()
        conn.close()

    saveToLogDB('INFO', f'FILE UPLOAD IN SIZE {file_length}B', 'SUCCESS')
    return f'File ID: {dbFileID} | File Token (PASSWORD FOR FILE): {dbFileToken}'

isServerRunning = True

def runServer():
    try:
        run(
            host=config['server'].get('host', fallback='0.0.0.0'),port=config['server'].getint('port', fallback=3138))
    except KeyboardInterrupt:
        pass

uploadFolder = os.path.join(ROOTDIR, "uploadedFiles")
os.makedirs(uploadFolder, exist_ok=True)
cleanup = DatabaseCleanup(FILE_DB, uploadFolder)
cleanup.runPeriodically(config['server'].getint('databaseScanDelay', fallback=480))

serverThread = threading.Thread(target=runServer, daemon=True) # runServer thread
serverThread.start()

analyticsThread = threading.Thread(target=analyticsInterval, daemon=True) # Auto analytics thread
analyticsThread.start()

print(f"Server started on http://{config['server'].get('host', fallback='0.0.0.0')}:{config['server'].get('port', fallback=3138)}")
print(f'NanoCloud Initiative | TempHost v{appVersion} is running. Use "help" for command\'s list\n')
try:
    while isServerRunning:
        try:
            command = input(">> ").strip().lower()
            if command == "help":
                print(f'''Available commands (warning - most of them don't work currently):
                      server stop - stops the server
                      config allowLogging [true/false] - turn on server's logging
                      config analytics [true/false] - allow logging more detailed info < It doesnt work cuz this project isnt big enough
                      user ban [IP] - banns user's IP adress
                      ''')
            elif command == "server stop":
                print("Stopping server...")
                isServerRunning = False
                exit()
            elif config := command.startswith("config allowLogging "):
                value = command.split(" ")[2]
                if value == "true":
                    logServerInfo = True
                    print("[COMMAND]: Logging enabled")
                elif value == "false":
                    logServerInfo = False 
                    print('[COMMAND]: Logging disabled')
                else:
                    print("Invalid value. Use 'true' or 'false'")
            elif banCommand := command.startswith("user ban "):
                value = command.split(" ")[2]
                with dbLock:
                    conn = sqlite3.connect(IP_DB, check_same_thread=False)
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO banned (userIP, banned) VALUES (?, '1')", (confidential.encrypt(value.encode()),))
                    conn.commit()
                    conn.close()
                    print('[COMMAND]: Bro got banned')
            elif command == "config analytics":
                print("Analytics configuration is not implemented.")
        except KeyboardInterrupt:
            print("\nByeeeee!")
            isServerRunning = False
            exit()
except Exception as e:
    print(f"Error in command loop: {e}")
    isServerRunning = False