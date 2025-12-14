import json
import os
import re
import urllib.request
import sys

PYPY_URL = "https://api.pypy.dance/bundle"
WD_URL = "https://api.udon.dance/Api/Songs/list"

def download_file(url, filename):
    print(f"Downloading {filename} from {url}...")
    try:
        # User-Agent header is often needed to avoid 403s
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        with urllib.request.urlopen(req) as response:
            data = response.read()
            with open(filename, 'wb') as f:
                f.write(data)
        print(f"Successfully downloaded {filename}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        sys.exit(1)

def load_json_db(filename, url):
    if not os.path.exists(filename):
        print(f"File {filename} not found locally.")
        download_file(url, filename)
    
    print(f"Loading {filename}...")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        sys.exit(1)

def clean_string(s):
    if not s:
        return ""
    # Remove things inside brackets [] or ()
    s = re.sub(r'\[.*?\]', '', s)
    s = re.sub(r'\(.*?\)', '', s)
    # Remove non-alphanumeric (keep spaces)
    s = re.sub(r'[^\w\s]', ' ', s)
    # Collapse spaces
    s = re.sub(r'\s+', ' ', s)
    # Lowercase
    s = s.lower().strip()
    return s

def get_tokens(s):
    # Tokenize by splitting on whitespace
    return set(s.split())

def safe_print(s):
    try:
        print(s)
    except UnicodeEncodeError:
        # Fallback for Windows consoles with limited charset support
        try:
            print(s.encode('gbk', 'replace').decode('gbk'))
        except:
            print(s.encode('utf-8', 'replace').decode('utf-8')) # Last resort

