import os
import sys

try:
    if 'QT_QPA_PLATFORM' in os.environ:
        del os.environ['QT_QPA_PLATFORM']
except Exception as e:
    print(f"[!] An error occurred: {e}")

from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWidgets import *
import time  # Added time module
from datetime import datetime, timedelta
from icalendar import Calendar
import calendar
from PyQt6.QtGui import *
from PyQt6.QtCore import *


# Reading the link file
def read_text_file(file_path):
    lines = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()  # Remove leading/trailing whitespaces
            if line:  # Exclude empty lines
                lines.append(line)
    return lines

def get_events(file_path):
        with open(file_path, 'rb') as file:
            data = file.read()
        #print(data)
        calendar = Calendar.from_ical(data)
        events = [component for component in calendar.walk() if component.name == 'VEVENT']        
        return events

class BrowserWindow(QMainWindow):
    load_finished = False
    i = -1
    block_list = []
    j = 0

    def __init__(self, scroll_timer_pms, scroll_timer_steps, wait_after_scrolling):
        super(BrowserWindow, self).__init__()

        self.scroll_timer_pms = scroll_timer_pms
        self.scroll_timer_steps = scroll_timer_steps
        self.wait_after_scrolling = wait_after_scrolling
        self.links = read_text_file('links.txt')
        self.loading = False
        # Setting a title
        self.setWindowTitle("Browser Pi")

        # main layout with Top bar
        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # layout for inner stuff
        layout = QHBoxLayout()

        top_bar = QFrame()
        #top_bar.setStyleSheet("background-color: white")

        logo_layout = QHBoxLayout(top_bar)
        logo_layout.setContentsMargins(10, 10, 10, 10)

        left_logo = QLabel(top_bar)
        left_pixmap = QPixmap("logo1.png")
        left_pixmap = left_pixmap.scaledToWidth(top_bar.height() + 20)
        left_logo.setPixmap(left_pixmap)
        left_logo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        left_logo.adjustSize()
        logo_layout.addWidget(left_logo)

        self.right_text = QLabel("Uhrzeit: \n" + datetime.now().strftime("%H:%M"), top_bar)
        self.right_text.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.right_text.setStyleSheet("color: white; font-size: 25px")
        logo_layout.addWidget(self.right_text)

        main_layout.addWidget(top_bar)
        main_layout.addLayout(layout)

        # Scroll area on the left

        # Web view on the right
        self.webview = QWebEngineView()
        self.webview.setStyleSheet("border-radius: 1000px;")
        layout.addWidget(self.webview)
        
        # Load the initial URL
        self.webview.loadFinished.connect(self.page_loaded)
        self.init_link()

        print("[*] Site loaded!")
        # Set the size policy and stretch factor for left and right widgets
        self.webview.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        layout.setStretchFactor(self.webview, 1)
       
        

        # Clock timer
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_time)
        self.clock_timer.start(1000)

        self.showFullScreen()

    def setup_scrolling(self):
        """Setup the timer and scrolling parameters."""
        print("[Attempting to scroll]")
        self.scroll_timer = QTimer()
        self.loading = True
        self.scroll_timer.timeout.connect(self.scroll_page)
        self.scroll_timer.start(self.scroll_timer_pms)
        self.scroll_step = self.scroll_timer_steps
        self.scroll_direction = 1  # 1 for down, -1 for up
        print("[Ended Set up]")

    def index_timer_func(self):
        """Cycle through the paths list."""
        self.j = (self.j+1) % len(self.paths)

    def init_link(self):
        """Initialize the first link if not done already."""
        if self.i == -1:
            print("[*] Initialized first page!")
            self.load_next_link()

    def is_image_url(self, url):
        """Check if the URL points to an image."""
        return url.endswith(('.jpg', '.jpeg', '.png'))


    def load_next_link(self):
        """Load the next link."""
        self.i += 1
        if self.i >= len(self.links):
            self.i = 0

        next_url = self.links[self.i]
        self.load_page(next_url)

    def load_page(self, url):
        """Load a specified URL."""
        self.load_finished = False
        print(f"[*] Load page {url}")
        self.webview.load(QUrl(url))

    def delay_load(self, delay_milliseconds):
        """Delay the loading of the next link."""
        QTimer.singleShot(delay_milliseconds, self.load_next_link)

    def page_loaded(self, success):
        """Callback for when the page has loaded."""
        print("Page Loaded")
        if success:
            current_url = self.webview.url().toString()
            self.load_finished = True
            if not self.is_image_url(current_url):
                print("[*] Page successfully loaded! Setting up scrolling.")
                self.setup_scrolling()  # Start scrolling for web pages
            else:
                print("[*] Image loaded! Waiting for 10 seconds.")
                print("Delay 1")
                self.delay_load(10000)  # Wait for 10 seconds for images
        else:
            print(f"[!] Failed to load {self.links[self.i]}. Waiting for 3 seconds.")
            print("[Delay 2]")
            self.delay_load(3000)  # Wait for 3 seconds if page load failed

   
    def scroll_page(self):
        """Scroll the page."""
        if self.is_page_loaded():
            scroll_position = self.webview.page().scrollPosition().y() + (self.scroll_step * self.scroll_direction)
            self.webview.page().runJavaScript(f"window.scrollTo(0, {scroll_position});")

            contents_height = self.webview.page().contentsSize().height() - self.webview.height()

            if scroll_position <= 0 and self.scroll_direction == -1:
                self.scroll_direction = 1  # Change direction to scroll down
                if self.loading:
                    print("[*] Reached the top. Loading next link in 3 seconds.")
                    print("[*] Delay 3")
                    self.loading = False
                    self.scroll_timer.stop()
                    self.delay_load(3000)  # Wait for 3 seconds then load next link
            elif scroll_position >= contents_height:
                self.scroll_direction = -1  # Change direction to scroll up


    def is_page_loaded(self):
        """Check if the current page is loaded."""
        return self.load_finished


    def update_time(self):
        formatted_time = datetime.now().strftime("%H:%M")
        self.right_text.setText("Uhrzeit: \n" + formatted_time)

            
    
if __name__ == "__main__":
    # Disable IBus integration
    os.environ["QT_IM_MODULE"] = ""
    print("[*] Starting the browser!")
    app = QApplication(sys.argv)
    window = BrowserWindow(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    window.show()
    sys.exit(app.exec())
