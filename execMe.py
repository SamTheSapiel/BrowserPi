#!/usr/bin/env python3

import subprocess
import os
import requests
import threading
import time

print_command_for_debugging = False
sleep_after_scrolling = 3
scroll_timer_ms = 2
scroll_timer_steps = 3
raspi_h1_label = "Digital Signage"
raspi_bullet_site_url = "https://typo3.uni-greifswald.de/?id=262261"
shutdown_time = None  # if None, then it won't shut down, e.g. "18:00"
room_names = "['SR 1', 'SR 2', 'SR 1', 'SR 1', 'SR 1', 'SR 1', 'SR 1']"
room_paths = "['plans/sr1.ics', 'plans/sr2.ics', 'plans/sr1.ics', 'plans/sr1.ics', 'plans/sr1.ics', 'plans/sr1.ics', 'plans/sr1.ics']"
show_time_table = "True" # "True" or "False"
timetable_change_ms = 10000
lower_left_font_color = "white"
lower_left_font_size = "21px"
table_font_color = "white"
table_font_size = "18px"
text_block_font_color = "white"
text_block_font_size = "24px"



def is_connected():
    try:
        resp = requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False


def start_browser(scroll_timer_ms, scroll_timer_steps, sleep_after_scrolling, show_time_table, room_names, room_paths, timetable_change_ms, lower_left_font_color, lower_left_font_size, table_font_color, table_font_size, text_block_font_color, text_block_font_size, print_command_for_debugging):
    try:
        cmd = f'python3 browser.py {scroll_timer_ms} {scroll_timer_steps} {sleep_after_scrolling} "{show_time_table}" "{room_names}" "{room_paths}" {timetable_change_ms} "{lower_left_font_color}" "{lower_left_font_size}" "{table_font_color}" "{table_font_size}" "{text_block_font_color}" "{text_block_font_size}"'
        if print_command_for_debugging:
            print(cmd)
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("[*] Browser Output:", result.stdout, result.stderr)

    except subprocess.CalledProcessError as e:
        print("[!] Browser Error:", e)
        print("[*] Try debugging browser with setting 'print_command_for_debugging = True' and hitting the output to the commandline for further information.")


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

browser_thread = threading.Thread(target=start_browser, args=(scroll_timer_ms, scroll_timer_steps, sleep_after_scrolling, show_time_table, room_names, room_paths, timetable_change_ms, lower_left_font_color, lower_left_font_size, table_font_color, table_font_size, text_block_font_color, text_block_font_size, print_command_for_debugging))
browser_thread.start()

if shutdown_time:
    shutdown_thread = threading.Thread(target=shutdown_rpi_at, args=(shutdown_time,))
    shutdown_thread.start()

