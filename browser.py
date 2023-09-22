import os
import sys
import ast

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
    room_names = []
    paths = []
    load_finished = False
    i = -1
    block_list = []
    j = 0
    show_time_table = False

    def __init__(self, scroll_timer_pms, scroll_timer_steps, wait_after_scrolling, show_time_table, rn, ps):
        super(BrowserWindow, self).__init__()
        
        self.show_time_table = ast.literal_eval(show_time_table)
        if rn != "" or self.show_time_table:
            self.room_names = ast.literal_eval(rn)
        
        if ps != "" or self.show_time_table:
            self.paths = ast.literal_eval(ps)

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
        if show_time_table == "True":
            print("Show timetbale", show_time_table)
            scroll_area = self.create_scroll_area()

            # Left side layout
            self.left_layout = QVBoxLayout()
            self.left_layout.addWidget(scroll_area)
            self.lower_left_widget = self.create_lower_left_widget()
            self.left_layout.addWidget(self.lower_left_widget)

            # Set the left layout as the widget for the left side
            left_widget = QWidget()
            left_widget.setLayout(self.left_layout)
            layout.addWidget(left_widget)

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
       
        if show_time_table == "True":
            left_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
            layout.setStretchFactor(left_widget, 1)

        # Clock timer
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_time)
        self.clock_timer.start(1000)

        if show_time_table == "True":
            # Box timer
            self.box_timer = QTimer()
            self.box_timer.timeout.connect(self.update_boxes)
            self.box_timer.start(1000)


            self.index_timer = QTimer()
            self.index_timer.timeout.connect(self.index_timer_func)
            self.index_timer.timeout.connect(self.table_update)
            self.index_timer.start(10000)


        self.showFullScreen()

    
    def table_update(self):
        if isinstance(self.lower_left_widget, QWidget):
            self.lower_left_widget.deleteLater()
        self.lower_left_widget = self.create_lower_left_widget()
        self.left_layout.addWidget(self.lower_left_widget)
        #print("updated?")

    def update_boxes(self):
        #print(datetime.now().time())
        for i in range(0, len(self.block_list)):
            self.block_list[i].setText(self.room_names[i] + ":  " + self.get_current_event(self.paths[i]))

    def create_scroll_area(self):
        if(len(self.paths) != len(self.room_names)):
            raise ValueError("Length of paths and room_names does not match!")

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # Enable widget to resize with the scroll area
        scroll_area.setStyleSheet("QScrollArea { border: none; }")  # Remove the border

        # Upper left corner (Text blocks)
        upper_left = QVBoxLayout()


        # Create text blocks
        for i in range(0, len(self.paths)):
            text = self.room_names[i] + ":  " + self.get_current_event(self.paths[i])
            block = self.create_text_block(text, i + 1)
            upper_left.addWidget(block)
            self.block_list.append(block)

        # Create a separate layout for the upper_left blocks
        upper_left_layout = QVBoxLayout()
        upper_left_layout.addLayout(upper_left)
        upper_left_layout.addStretch()

        # Add the upper left corner to the scroll area
        scroll_widget = QWidget()
        scroll_widget.setLayout(upper_left_layout)
        scroll_area.setWidget(scroll_widget)

        return scroll_area

    def create_text_block(self, text, position):
        block = QLabel(text)
        if position % 2 == 0:  # Even position
            block.setStyleSheet("background-color: lightblue; color: white; font-size: 25px; padding: 10px; border-radius: 10px;")
        else:  # Odd position
            block.setStyleSheet("background-color: blue; color: white; font-size: 25px; padding: 10px; border-radius: 10px;")
        block.setWordWrap(True)  # Enable text wrapping
        return block

    
    def create_lower_left_widget(self):
        lower_left = QFrame()
        #lower_left.setStyleSheet("background-color: blue; border-radius: 10px;")
        if self.j % 2 == 0:  # Even position
            lower_left.setStyleSheet("background-color: blue; border-radius: 10px;")
        else:  # Odd position
            lower_left.setStyleSheet("background-color: lightblue; border-radius: 10px;")

        lower_left.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Create the layout
        lower_left_layout = QVBoxLayout()

        label = QLabel(self.room_names[self.j])
        lower_left_layout.addWidget(label)
        label.setStyleSheet("color: white; font-size: 20px;")

        # Create the table and add it to the layout
        ics_file = self.paths[self.j % len(self.paths)]
        events = get_events(ics_file)  # Replace with your .ics file path
        table = self.create_table(events)

        lower_left_layout.addWidget(table)


        # Set the layout for the frame
        lower_left.setLayout(lower_left_layout)

        return lower_left

    def create_table(self, events):
        # Create the table widget
        table = QTableWidget()
        table.setStyleSheet("color: white; font-size: 18px")

# Text ins obere linke Kästchen hinzufügen



        # Define the weekdays and time slots
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        slots = [ '08-10', '10-12', '12-14', '14-16', '16-18', '18-20']

        table.setColumnCount(len(days))
        table.setRowCount(len(slots))
        table.setHorizontalHeaderLabels(days)
        table.setVerticalHeaderLabels(slots)

        # Initialize the table with empty events
        for i in range(len(slots)):
            for j in range(len(days)):
                item = QTableWidgetItem('')
                table.setItem(i, j, item)

        # Add events to the table
        for event in events:
            day_index = event['dtstart'].dt.weekday()
            start_hour = event['dtstart'].dt.hour
            end_hour = event['dtend'].dt.hour

            start_slot_index = None
            for i, slot in enumerate(slots):
                slot_start, slot_end = map(int, slot.split('-'))
                if start_hour >= slot_start and start_hour < slot_end:
                    start_slot_index = i
                    break

    # If we found the starting slot, keep adding the event to subsequent slots until the event ends
            if start_slot_index is not None:
                i = start_slot_index
                while i < len(slots) and end_hour > int(slots[i].split('-')[0]):
                    item = QTableWidgetItem(event['SUMMARY'])
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    table.setItem(i, day_index, item)
                    i += 1

        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table

    def get_current_event(self, ics_file):
        with open(ics_file, 'rb') as file:
            cal = Calendar.from_ical(file.read())

        now = datetime.now().replace(tzinfo=None)
        current_event = None
        next_event = None
        fm = timedelta(minutes=15)

        for component in cal.walk():
            if component.name == 'VEVENT':
                event_start = component.get('DTSTART').dt.replace(tzinfo=None)
                event_end = component.get('DTEND').dt.replace(tzinfo=None)

                if event_start.weekday() == now.weekday() and (event_start - fm).time()  <= now.time() <= (event_end - fm).time():
                    current_event = component
                    break

                if event_start.time() > now.time() and event_start.weekday() >= now.weekday():
                    if next_event is None:
                        next_event = component
                        #print("next event set")
        if current_event is None and next_event is None:
            for component in cal.walk():
                if component.name == 'VEVENT':
                    event_start = component.get('DTSTART').dt.replace(tzinfo=None)
                    if next_event is None:
                        next_event = component
                    break

        if current_event is None:
            current_event = next_event

        return  str(current_event.get('SUMMARY')) + "\nStart time: " + current_event.get('DTSTART').dt.strftime("%H:%M") + "; End time: " + current_event.get('DTEND').dt.strftime("%H:%M") + " " + calendar.day_name[current_event.get('DTSTART').dt.weekday()]


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
    print()
    window = BrowserWindow(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6])
    #def __init__(self, scroll_timer_pms, scroll_timer_steps, wait_after_scrolling, show_time_table, rn, ps):
    window.show()
    sys.exit(app.exec())
