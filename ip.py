import os
import requests
import json
from bs4 import BeautifulSoup
from tenacity import retry, wait_exponential, stop_after_attempt
from tqdm import tqdm
import time
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--output_file", type=str, default="../ip_results.json")
args = parser.parse_args()

def parse_ip_info(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Extract the location
    location = soup.find("td", class_="th", string="归属地").find_next_sibling("td").get_text(strip=True).split("上报纠错")[0]
    
    # Extract the IP type
    ip_type = soup.find("td", class_="th", string="iP类型").find_next_sibling("td").get_text(strip=True)
    
    return location, ip_type

@retry(wait=wait_exponential(multiplier=1, min=4, max=10), reraise=True, stop=stop_after_attempt(5))
def get_ip_loc(ip):
    resp = requests.get(f"https://api.ipapi.is/?ip={ip}", headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36", "Referer": "https://www.ipshudi.com/223.72.91.253.htm"}, timeout=180)
    resp = resp.json()

    if "datacenter" in resp:
        is_center = True
    else:
        is_center = False
    return resp, is_center

ip_info = {}
results = {}

if os.path.exists("../ip_info.json"):
    ip_info = json.load(open("../ip_info.json"))


for file in ["/var/log/nginx/access.log"]:
    lines = open(file).readlines()
    line_num = len(lines)
    for line in tqdm(lines, total=line_num):
        if "https://weizechen.com/" not in line or "main.css" not in line:
            continue
        line = line.split()
        ip = line[0]
        acc_time = line[3]
        if ip not in ip_info:
            try:
                info = get_ip_loc(ip)
            except Exception as e:
                print(e)
                continue
            ip_info[ip] = info
            time.sleep(1)
        loc = ip_info[ip][0]
        is_center = ip_info[ip][1]

        if loc['location']['city'] in ['Zhangjiakou', 'Nanjing', 'Dongguan', 'Zhengzhou', 'Changzhou', 'Shijiazhuang']:
            continue
    
        # if type == "城域网":
        if not is_center:
            results[acc_time] = f"{loc}. {is_center}"

with open("../ip_info.json", 'w') as f:
    json.dump(ip_info, f, indent=2)

with open(args.output_file, 'w') as f:
    json.dump(results, f, indent=2)
