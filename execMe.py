#!/usr/bin/env python3

import subprocess
import os
import requests
import threading
import time

sleep_after_scrolling = 3
scroll_timer_ms = 2
scroll_timer_steps = 3
raspi_h1_label = "Digital Signage"
raspi_bullet_site_url = "https://typo3.uni-greifswald.de/?id=262261"
shutdown_time = None  # if None, then it won't shut down, e.g. "18:00"


def is_connected():
    try:
        resp = requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False


def start_browser(scroll_timer_ms, scroll_timer_steps, sleep_after_scrolling):
    try:
        result = subprocess.run(f"python3 small_browser.py {scroll_timer_ms} {scroll_timer_steps} {sleep_after_scrolling}", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("[*] Browser Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("[!] Browser Error:", e)


def shutdown_rpi_at(stime):
    while True:
        now = time.strftime("%H:%M")
        if now >= stime:
            os.system("shutdown -h now")
            break
        time.sleep(30)


print("[*] Checking internet connection.")
if is_connected():
    print("[*] Trying to update the link file.")
    soup = subprocess.run(f"python3 soup.py \"{raspi_bullet_site_url}\" \"{raspi_h1_label}\"", shell=True, capture_output=True, text=True)
    if soup.returncode == 0:
        print("[*] Updated links successfully.")
    else:
        print(f"[!] Soup script failed with return code: {soup.returncode}")
        print(f"[*] STDERR: {soup.stderr}")
else:
    print("[!] Failed to establish an internet connection.")
    print("[!] Failed to update the link file")

browser_thread = threading.Thread(target=start_browser, args=(scroll_timer_ms, scroll_timer_steps, sleep_after_scrolling))
browser_thread.start()

if shutdown_time:
    shutdown_thread = threading.Thread(target=shutdown_rpi_at, args=(shutdown_time,))
    shutdown_thread.start()

