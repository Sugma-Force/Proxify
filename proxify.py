import os
import time
import concurrent.futures
import threading
import re
import pathlib
import requests
from datetime import datetime
from colorama import Fore, Style
from pystyle import Write, System, Colors, Colorate, Anime

# color codes
red = Fore.RED
yellow = Fore.YELLOW
green = Fore.GREEN
blue = Fore.BLUE
orange = Fore.RED + Fore.YELLOW
pretty = Fore.LIGHTMAGENTA_EX + Fore.YELLOW
magenta = Fore.MAGENTA
lightblue = Fore.LIGHTBLUE_EX
cyan = Fore.CYAN
gray = Fore.LIGHTBLACK_EX + Fore.WHITE
reset = Fore.RESET
pink = Fore.LIGHTGREEN_EX + Fore.LIGHTMAGENTA_EX
dark_green = Fore.GREEN + Style.BRIGHT

output_lock = threading.Lock()
start_time = time.time()

def get_time_rn():
    now = datetime.now()
    return now.strftime("%H:%M:%S")

def ui():
    System.Clear()
    Write.Print(f"""
\t\t\t (                                           
\t\t\t )\ )                           (            
\t\t\t(()/(   (              )   (    )\ )   (     
\t\t\t /(_))  )(     (    ( /(   )\  (()/(   )\ )  
\t\t\t(_))   (()\    )\   )\()) ((_)  /(_)) (()/(  
\t\t\t| _ \   ((_)  ((_) ((_)\   (_) (_) _|  )(_)) 
\t\t\t|  _/  | '_| / _ \ \ \ /   | |  |  _| | || | 
\t\t\t|_|    |_|   \___/ /_\_\   |_|  |_|    \_, | 
\t\t\t                                       |__/  

    [ Quick and dirty scraper for all sorts of http/s proxies. Not optimized at all! ]
""", Colors.red_to_blue, interval=0.000)
    time.sleep(3)

ui()

REGEX = re.compile(
    r"(?:^|\D)?(("+ r"(?:[1-9]|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    + r"):" + (r"(?:\d|[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{3}"
    + r"|65[0-4]\d{2}|655[0-2]\d|6553[0-5])")
    + r")(?:\D|$)"
)

with open("sources.txt") as f:
    links = f.read().splitlines()

scraped = 0
duplicate = 0
proxies = []

def scrape_proxy_links(link):
    global scraped
    link_proxies = []
    response = requests.get(link)
    if response.status_code == 200:
        with output_lock:
            time_rn = get_time_rn()
            print(f"[ {pink}{time_rn}{reset} ] | ( {lightblue}CHECKED{reset} ) Site " + link[:40] + f"********{reset}\n", end='')
            html = response.text
            if tuple(REGEX.finditer(html)):
                for proxy in tuple(REGEX.finditer(html)):
                    link_proxies.append(proxy.group(1))
                time_rn = get_time_rn()
                print(f"[ {pink}{time_rn}{reset} ] | ( {cyan} FOUND {reset} ) {pretty}{len(link_proxies)}{reset} Proxies\n", end='')
            else:
                time_rn = get_time_rn()
                print(f"[ {pink}{time_rn}{reset} ] | ( {red}FAILED{reset} ) No proxies at {link}{reset}\n", end='')
        scraped += len(link_proxies)
        for proxy in link_proxies:
            proxies.append(proxy)

def cleanup():
    global duplicate
    proxy_seen = set()
    with open("proxies.txt", "w") as outfile:
        for proxy in proxies:
            if proxy not in proxy_seen:
                outfile.write(proxy + "\n")
                proxy_seen.add(proxy)
            else:
                duplicate += 1
    time_rn = get_time_rn()
    print(f"[ {pink}{time_rn}{reset} ] | ( {blue}REMOVED{reset} ) {pretty}{duplicate} {reset}duplicates\n", end='')

def main():
    num_threads = len(links)
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(scrape_proxy_links, links)
    time_rn = get_time_rn()
    print(f"\n[ {pink}{time_rn}{reset} ] | ( {blue}CHECKED{reset} ) {pretty}{len(links)} {reset}Sites\n", end='')
    print(f"[ {pink}{time_rn}{reset} ] | ( {blue}SCRAPED{reset} ) {pretty}{scraped} {reset}potential Proxies\n", end='')
    cleanup()
    time_rn = get_time_rn()
    print(f"[ {pink}{time_rn}{reset} ] | ( {green}WRITTEN{reset} ) {pretty}{scraped - duplicate}{reset} Proxies in {round(time.time() - start_time, 2)} seconds\n", end='')
    print(f"\n[ {pink}{time_rn}{reset} ] | ( {green}EXITING{reset} ) {pink}GLHF{reset}\n\n", end='')

main()
