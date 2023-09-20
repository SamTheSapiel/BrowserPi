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

        # Scroll timer
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.scroll_page)
        self.scroll_timer.start(self.scroll_timer_pms)  # Scroll every 1 millisecond
        
        self.scroll_step = self.scroll_timer_steps  # Adjust the scroll step as needed
        self.scroll_direction = 1  # Initial scroll direction (1 for down, -1 for up)

        self.showFullScreen()



    def index_timer_func(self):
        self.j = (self.j+1) % len(self.paths)
        #print(self.j)


    def init_link(self):
        if self.i == -1:
            print("[*] Initialized first page!")
            self.load_next_link()

    # Function for loading the next page
    def load_next_link(self):

        # If the index i is smaller than the set, increase i and load the next page
        if self.i >= len(self.links):
            self.i = 0
        self.load_page(self.links[self.i])

        # Else, start again at zero

    # Function for scrolling through the page
    def scroll_page(self):
        if self.is_page_loaded():
            # Scroll down or up depending on the current scroll direction
            scroll_position = self.webview.page().scrollPosition().y() + (self.scroll_step * self.scroll_direction)

            # Scroll to the new position
            self.webview.page().runJavaScript(f"window.scrollTo(0, {scroll_position});")

            # Check if we reached the top or bottom of the page
            contents_height = self.webview.page().contentsSize().height() - self.webview.height()

            if scroll_position <= 0:
                if self.webview.page().scrollPosition().y() == 0 and self.scroll_direction == -1 and self.is_page_loaded():
                    self.scroll_direction = 1
                    #print("[!] Sleeping for 3 seconds!")
                    time.sleep(self.wait_after_scrolling)
                    self.load_next_link()
            elif scroll_position >= contents_height and self.is_page_loaded():
                #print("[*] Changing the direction!")
                self.scroll_direction = -1


    def load_page(self, url):
        self.load_finished = False
        self.webview.load(QUrl(url))

    def page_loaded(self, success):
        if success:  # If the page failed to load
            self.load_finished = True
            self.i += 1
        else:
            print(f"[!] Failed to load {self.links[self.i]}.")
            self.i += 1
            print("[!] Sleep 3 seconds.")
            QTimer.singleShot(3000, self.load_next_link)




    def is_page_loaded(self):
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

