import os, psutil, platform
from configparser import ConfigParser

if platform.system() == "Windows":
    print('Starting analyticUtils.py on Windows')
elif platform.system() == "Linux":
    print('Starting analyticUtils.py on Linux')
    import glob
elif platform.system() == "Darwin":
    print('MACOS IS NOT SUPPORTED, USING LINUX FUNCTIONS')
else:
    print('UNKNOWN PLATFORM, NOT SUPPORTED, USING LINUX FUNCTIONS')

def getCPUUsage():
    return psutil.cpu_percent(interval=1)

def getCPUTemperatureLinux():
    try:
        temp_files = glob.glob('/sys/class/thermal/thermal_zone*/temp')
        temps = [int(open(f).read()) / 1000 for f in temp_files]
        return max(temps)
    except:
        return None

def getCPUTemperatureWindows():
    try:
        import py360ware
        sensor = py360ware.Sensor()
        return sensor.get_temperature()
    except ImportError:
        return None

def getDirectorySize(path):
    totalSize = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            totalSize += os.path.getsize(fp)
    return totalSize

def getPreparedTable():
    if platform.system() == "Windows":
        return [
            ['cpu usage', getCPUUsage()],
            ['cpu temp', getCPUTemperatureWindows()],
            ['ram usage', psutil.virtual_memory().percent],
            ['disc usage', psutil.disk_usage('/').percent],
            ['uploadedFiles size (in bytes)', getDirectorySize(os.getcwd()) / (1024 * 1024)]
        ]
    else:
        return [
            ['cpu usage', getCPUUsage()],
            ['cpu temp', getCPUTemperatureLinux()],
            ['ram usage', psutil.virtual_memory().percent],
            ['disc usage', psutil.disk_usage('/').percent],
            ['uploadedFiles size (in bytes)', getDirectorySize(os.getcwd()) / (1024 * 1024)]
        ]