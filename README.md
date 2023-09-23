# BrowserPiGW

Digital Signage Browser Project
Description

This project provides a specialized browser designed for the purpose of displaying content - both images and websites. This is particularly useful for digital signage and information display systems. The project is built to run on Manjaro with "dash to panel" activated to deactivate the "Activity start".
Project Structure

    autostart.sh - Shell script to run the program at start.
    execMe.py - The main script responsible for starting the browser, checking for internet connection, updating links, etc.
    browser.py - Script containing the logic for the browser.
    soup.py - A script for scraping and processing the content from specified websites.
    links.txt - A text file containing the links to be displayed.
    logo1.png - Image asset for the project.
    plans/ - Directory containing planning files in the .ics format.
    README.md - The file you are currently reading.

How execMe.py Works

    Variables for Customization:
        sleep_after_scrolling: Time to sleep after scrolling.
        scroll_timer_ms: Timer for scrolling in milliseconds.
        scroll_timer_steps: Number of scroll steps.
        raspi_h1_label: Label used for web scraping.
        raspi_bullet_site_url: URL of the website for web scraping.
        shutdown_time: Time to shutdown the Raspberry Pi (Set to None to disable automatic shutdown).
        room_names: Names of the rooms (should be an array).
        room_paths: Paths for each room's plan.
        show_time_table: Whether or not to show the timetable. Can be "True" or "False".

    Functions:
        is_connected(): Checks if there is an active internet connection.
        start_browser(...): Initiates the browser with given parameters.
        shutdown_rpi_at(stime): Shuts down the Raspberry Pi at a specified time.

    Execution Flow:
        The script checks for an internet connection.
        If a connection exists, it tries to update the link file using the soup.py script.
        The browser is then started in a separate thread using the given parameters.
        If a shutdown_time is specified, another thread is started to shut down the Raspberry Pi at the given time.

Dependencies

The following libraries and modules are used in this project:

    os and sys: Basic Python modules for interacting with the operating system and system-specific parameters.
    ast: Evaluate Python's abstract syntax trees.
    PyQt6 and PyQt6.QtWebEngineWidgets: Comprehensive set of Python bindings for Qt libraries which provides everything needed to create GUI applications as well as multithreaded applications.
    requests: Library for making HTTP requests.
    BeautifulSoup (from bs4): Library for web scraping purposes to pull the data out of HTML and XML files.
    time, datetime, and calendar: Modules for handling time-based actions.
    icalendar: Used to process .ics calendar files.
    re: Regular expression operations.

To install these dependencies, you can use pip

Usage

Make sure you've installed the necessary dependencies. Modify the variables in execMe.py as per your needs. Run the autostart.sh script to start the program.

Note: Always remember to adhere to the terms of service of any website you are scraping.
