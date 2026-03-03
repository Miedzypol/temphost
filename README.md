<img width="1000" height="350" alt="temphost" src="https://github.com/user-attachments/assets/8d44c84e-2102-4dd3-9793-d731e6381ca3" />
# TempHost

TempHost - My **FIRST** "Good" web service. It functions on `port 3138` and it allows the user to store his files for 24 hours on the server's machine. After that it is deleted.

### Supported Operating Systems:
- Windows 10/11
- Linux Debian/Ubuntu based
- **!! DARWIN BASED SYSTEMS **(such as MacOS and other Apple's products)** ARE NOT SUPPORTED AND WOULDN'T BE !!**

## Important information
TempHost lacks many thing, such as any protection, it uses SQLite3 for Python, it isn't well optimized and still lacks protection, caching etc. Current version's front-end does not even have download abilites, you need to `http://localhost:3138/download?id={file ID}&token={file Token}`.
BUT I swear, I would fix everything. If not, I'll ask for help.
ALSO - THE PROJECT DOESN'T SCAN FILES LOOKING FOR VIRUSES, OR OTHER BANNED CONTENT. 

## About TempHost
The project uses 3 SQLite3 .db files. `banned.db` (it will) store encrypted banned users IPv4. `logs.db` stores logs:
- type - Log's type (like Startup, Info, Download, Upload etc.)
- date - automatically added date of the log. Format: YYYY-MM-DD HH:MM:SS. Example: 2026-01-01 11:45:30
- descripction - Log's description. Example: `BACKEND SERVER STARTUP`, `TRYING TO DOWNLOAD A FILE`
- result: result, like `ERROR: FILE NOT FOUND IN DB`, `STARTED SUCCESSFULLY ON Windows`

 `fileStorage.db` stores crucial information about uploaded files:
- fileName - File's stored name. Example: `p0jfuun6snurxlll.jpeg`
- fileID - File's ID used to search for it. Used for `download` function to search for the file in DB.
- accessToken - Token to access the file. Used in `download` function to auth the request to download the file.
- expireTime - UNIX format time used to identify if the file is expired. If it is, it is automatically deleted. Usually it is upload time + 86400 (seconds). Example: 1772145319.7648
- verified - placeholder. In future used to determine if the file was scanned for any illegal content. 0 means it wasn't scanned and 1 means it was scanned and there wasnt any illegal content found.

<img width="1055" height="783" alt="dfsaedsdfdsfsfd" src="https://github.com/user-attachments/assets/ddf7573d-d181-4d5e-94e1-b853fac77b8e" />
-# logs.db inside "DB Browser for SQLite"

## Installation

### Dependencies installation
For Windows 10/11:
```bash
pip install bcrypt
pip install bottle
```
For Linux Debian/Ubuntu based (using APT):
```bash
apt install python3-bottle python3-bcrypt
```
For Linux (using pipx):
```bash
pipx install bottle
pipx install bcrypt
```



### Download installator from releases tab (RECOMMENDED)
Download `installTH.py` from releases tab, then run in terminal (or double click, matters on the system you use)
run:
```bash
python3 installTH.py
```
### Run raw code (downloaded from branches)
I recommend downloadidng it from MAIN branch

You need to unpack it, and inside Terminal go to TempHost's directory and run:
```bash
python3 main.py
```

# Thanks!
