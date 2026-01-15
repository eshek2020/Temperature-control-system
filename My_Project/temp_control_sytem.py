import sys
import random
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QSlider, QFrame,
                             QGridLayout, QGroupBox, QTabWidget, QStatusBar, QFileDialog)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QPixmap, QTextDocument, QTextCursor, QTextTableFormat, QTextCharFormat, QFont, QTextLength
from PyQt5.QtPrintSupport import QPrinter
import pyqtgraph as pg
from collections import deque
from docx import Document
from docx.shared import Inches

class TemperatureControlSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Temperature Control System - Adamawa State University Mubi")
        self.setGeometry(100, 100, 1000, 700)
        
        # System state
        self.system_running = False
        
        # Data for plotting - initialize FIRST
        self.temp_data = deque([20.0] * 50, maxlen=50)
        self.humidity_data = deque([45.0] * 50, maxlen=50)
        self.time_data = deque([i for i in range(50)], maxlen=50)
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create header with logo
        self.create_header()
        
        # Create tabs
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Create dashboard tab
        self.dashboard_tab = QWidget()
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        
        # Create settings tab
        self.settings_tab = QWidget()
        self.tabs.addTab(self.settings_tab, "Settings")
        
        # Create logs tab
        self.logs_tab = QWidget()
        self.tabs.addTab(self.logs_tab, "System Log")
        
        # Initialize tabs
        self.init_dashboard()
        self.init_settings()
        self.init_logs()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("System Ready")
        
        # Timer for updating data
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(2000)  # Update every 2 seconds
        
    def create_header(self):
        # Header widget
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #2c3e50; border-radius: 5px; padding: 10px;")
        header_layout = QHBoxLayout(header_widget)
        
        # University name and title - LEFT side
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        uni_name = QLabel("Adamawa State University, Mubi")
        uni_name.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        uni_name.setAlignment(Qt.AlignLeft)
        
        system_name = QLabel("Computer Laboratory Temperature Control System")
        system_name.setStyleSheet("font-size: 14px; color: #ecf0f1;")
        system_name.setAlignment(Qt.AlignLeft)
        
        title_layout.addWidget(uni_name)
        title_layout.addWidget(system_name)
        
        header_layout.addWidget(title_widget)
        header_layout.addStretch()  # Push title to the left
        
        # Load and display logo - RIGHT side
        try:
            logo_label = QLabel()
            # Replace "logo.png" with your actual logo file path
            # Try different common image formats
            logo_paths = ["logo.png", "logo.jpg", "logo.jpeg", "logo.bmp", "adamawa_university_logo.jpeg"]
            pixmap = None
            
            for path in logo_paths:
                if os.path.exists(path):
                    pixmap = QPixmap(path)
                    break
            
            if pixmap is None:
                # Create a fallback logo with text
                raise Exception("Logo file not found")
                
            # Scale the logo if needed
            pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setStyleSheet("padding: 5px; background-color: white; border-radius: 5px;")
            header_layout.addWidget(logo_label)
        except:
            # Fallback if logo can't be loaded - create a text-based logo
            logo_fallback = QLabel("ASU\nMubi")
            logo_fallback.setStyleSheet("font-size: 16px; font-weight: bold; color: white; padding: 10px; background-color: #3498db; border-radius: 5px;")
            logo_fallback.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(logo_fallback)
        
        self.main_layout.addWidget(header_widget)
        
    def init_dashboard(self):
        layout = QVBoxLayout(self.dashboard_tab)
        
        # System control frame
        system_control_frame = QFrame()
        system_control_frame.setStyleSheet("QFrame { background-color: #f8f9fa; border-radius: 5px; padding: 10px; }")
        system_control_layout = QHBoxLayout(system_control_frame)
        
        self.system_button = QPushButton("Start System")
        self.system_button.setStyleSheet("QPushButton { background-color: #2ecc71; color: white; padding: 10px; border-radius: 5px; font-weight: bold; }"
                                       "QPushButton:hover { background-color: #27ae60; }")
        self.system_button.clicked.connect(self.toggle_system)
        system_control_layout.addWidget(self.system_button)
        
        system_status = QLabel("System Status: OFF")
        system_status.setStyleSheet("font-weight: bold; color: #e74c3c;")
        system_control_layout.addWidget(system_status)
        self.system_status_label = system_status
        
        system_control_layout.addStretch()
        
        layout.addWidget(system_control_frame)
        
        # Current readings frame
        readings_frame = QFrame()
        readings_frame.setFrameStyle(QFrame.StyledPanel)
        readings_frame.setStyleSheet("QFrame { background-color: #f8f9fa; border-radius: 5px; }")
        readings_layout = QHBoxLayout(readings_frame)
        
        # Temperature reading
        temp_widget = QWidget()
        temp_layout = QVBoxLayout(temp_widget)
        temp_title = QLabel("Current Temperature")
        temp_title.setAlignment(Qt.AlignCenter)
        self.temp_label = QLabel("24.5°C")
        self.temp_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #e74c3c; padding: 10px;")
        self.temp_label.setAlignment(Qt.AlignCenter)
        temp_layout.addWidget(temp_title)
        temp_layout.addWidget(self.temp_label)
        
        # Error display (difference between setpoint and current temp)
        error_widget = QWidget()
        error_layout = QVBoxLayout(error_widget)
        error_title = QLabel("Temperature Error")
        error_title.setAlignment(Qt.AlignCenter)
        self.error_label = QLabel("+1.5°C")
        self.error_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #e67e22; padding: 10px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        error_layout.addWidget(error_title)
        error_layout.addWidget(self.error_label)
        
        # Target temperature
        target_widget = QWidget()
        target_layout = QVBoxLayout(target_widget)
        target_title = QLabel("Target Temperature")
        target_title.setAlignment(Qt.AlignCenter)
        self.target_label = QLabel("23.0°C")
        self.target_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #2ecc71; padding: 10px;")
        self.target_label.setAlignment(Qt.AlignCenter)
        target_layout.addWidget(target_title)
        target_layout.addWidget(self.target_label)
        
        # Humidity reading
        humidity_widget = QWidget()
        humidity_layout = QVBoxLayout(humidity_widget)
        humidity_title = QLabel("Humidity Level")
        humidity_title.setAlignment(Qt.AlignCenter)
        self.humidity_label = QLabel("45%")
        self.humidity_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #3498db; padding: 10px;")
        self.humidity_label.setAlignment(Qt.AlignCenter)
        humidity_layout.addWidget(humidity_title)
        humidity_layout.addWidget(self.humidity_label)
        
        # Add to readings layout
        readings_layout.addWidget(temp_widget)
        readings_layout.addWidget(error_widget)
        readings_layout.addWidget(target_widget)
        readings_layout.addWidget(humidity_widget)
        
        layout.addWidget(readings_frame)
        
        # Graph frame
        graph_frame = QFrame()
        graph_frame.setFrameStyle(QFrame.StyledPanel)
        graph_frame.setStyleSheet("QFrame { background-color: white; border-radius: 5px; }")
        graph_layout = QVBoxLayout(graph_frame)
        
        # Create plot widget with adjusted width
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setTitle("Temperature and Humidity Trends", color='#333', size='14pt')
        self.plot_widget.setLabel('left', 'Value')
        self.plot_widget.setLabel('bottom', 'Time')
        self.plot_widget.addLegend()
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setFixedHeight(250)  # Fixed height as requested
        
        # Initialize plots with our data
        self.temp_plot = self.plot_widget.plot(list(self.time_data), list(self.temp_data), 
                                              pen=pg.mkPen(color='#e74c3c', width=2), 
                                              name="Temperature (°C)")
        self.humidity_plot = self.plot_widget.plot(list(self.time_data), list(self.humidity_data), 
                                                  pen=pg.mkPen(color='#3498db', width=2), 
                                                  name="Humidity (%)")
        
        graph_layout.addWidget(self.plot_widget)
        layout.addWidget(graph_frame)
        
        # Control buttons frame
        control_frame = QFrame()
        control_frame.setStyleSheet("QFrame { background-color: #f8f9fa; border-radius: 5px; }")
        control_layout = QHBoxLayout(control_frame)
        
        self.cool_button = QPushButton("Start Cooling")
        self.cool_button.setStyleSheet("QPushButton { background-color: #3498db; color: white; padding: 10px; border-radius: 5px; }"
                                      "QPushButton:hover { background-color: #2980b9; }")
        self.cool_button.clicked.connect(self.toggle_cooling)
        self.cool_button.setEnabled(False)  # Disabled until system is started
        
        self.heat_button = QPushButton("Start Heating")
        self.heat_button.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; padding: 10px; border-radius: 5px; }"
                                      "QPushButton:hover { background-color: #c0392b; }")
        self.heat_button.clicked.connect(self.toggle_heating)
        self.heat_button.setEnabled(False)  # Disabled until system is started
        
        self.fan_button = QPushButton("Toggle Fans")
        self.fan_button.setStyleSheet("QPushButton { background-color: #2ecc71; color: white; padding: 10px; border-radius: 5px; }"
                                      "QPushButton:hover { background-color: #27ae60; }")
        self.fan_button.clicked.connect(self.toggle_fans)
        self.fan_button.setEnabled(False)  # Disabled until system is started
        
        control_layout.addWidget(self.cool_button)
        control_layout.addWidget(self.heat_button)
        control_layout.addWidget(self.fan_button)
        
        layout.addWidget(control_frame)
        
    def init_settings(self):
        layout = QVBoxLayout(self.settings_tab)
        layout.setSpacing(20)
        
        # Temperature settings
        temp_group = QGroupBox("Temperature Settings")
        temp_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        temp_layout = QVBoxLayout(temp_group)
        
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target Temperature:"))
        self.target_slider = QSlider(Qt.Horizontal)
        self.target_slider.setRange(18, 30)
        self.target_slider.setValue(23)
        self.target_slider.valueChanged.connect(self.update_target_temp)
        target_layout.addWidget(self.target_slider)
        self.target_display = QLabel("23°C")
        self.target_display.setStyleSheet("min-width: 40px;")
        target_layout.addWidget(self.target_display)
        temp_layout.addLayout(target_layout)
        
        # Threshold settings
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Temperature Threshold:"))
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(1, 5)
        self.threshold_slider.setValue(2)
        self.threshold_slider.valueChanged.connect(self.update_threshold)
        threshold_layout.addWidget(self.threshold_slider)
        self.threshold_display = QLabel("±2°C")
        self.threshold_display.setStyleSheet("min-width: 40px;")
        threshold_layout.addWidget(self.threshold_display)
        temp_layout.addLayout(threshold_layout)
        
        layout.addWidget(temp_group)
        
        # System settings
        system_group = QGroupBox("System Settings")
        system_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        system_layout = QVBoxLayout(system_group)
        
        # Automation settings
        auto_layout = QHBoxLayout()
        auto_layout.addWidget(QLabel("Automation Mode:"))
        self.auto_button = QPushButton("Enabled")
        self.auto_button.setCheckable(True)
        self.auto_button.setChecked(True)
        self.auto_button.clicked.connect(self.toggle_automation)
        self.auto_button.setStyleSheet("QPushButton:checked { background-color: #2ecc71; color: white; border-radius: 5px; }"
                                      "QPushButton:unchecked { background-color: #e74c3c; color: white; border-radius: 5px; }")
        auto_layout.addWidget(self.auto_button)
        system_layout.addLayout(auto_layout)
        
        # Notification settings
        notif_layout = QHBoxLayout()
        notif_layout.addWidget(QLabel("Notifications:"))
        self.notif_button = QPushButton("Enabled")
        self.notif_button.setCheckable(True)
        self.notif_button.setChecked(True)
        self.notif_button.clicked.connect(self.toggle_notifications)
        self.notif_button.setStyleSheet("QPushButton:checked { background-color: #2ecc71; color: white; border-radius: 5px; }"
                                      "QPushButton:unchecked { background-color: #e74c3c; color: white; border-radius: 5px; }")
        notif_layout.addWidget(self.notif_button)
        system_layout.addLayout(notif_layout)
        
        layout.addWidget(system_group)
        layout.addStretch()
        
    def init_logs(self):
        layout = QVBoxLayout(self.logs_tab)
        
        # Log display
        log_title = QLabel("System Log")
        log_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(log_title)
        
        self.log_display = QLabel()
        self.log_display.setWordWrap(True)
        self.log_display.setStyleSheet("background-color: #f5f5f5; padding: 10px; border: 1px solid #ddd; border-radius: 5px; min-height: 300px;")
        self.log_display.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # Initial log content
        self.log_entries = [
            "System started at " + QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss"),
            "Temperature sensors initialized",
            "HVAC system connected",
            "Target temperature set to 23°C",
            "System running in automatic mode"
        ]
        self.update_log_display()
        
        layout.addWidget(self.log_display)
        
        # Log controls
        control_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear Log")
        clear_btn.setStyleSheet("QPushButton { padding: 8px; border-radius: 5px; background-color: #e74c3c; color: white; }")
        clear_btn.clicked.connect(self.clear_log)
        export_btn = QPushButton("Export Log")
        export_btn.setStyleSheet("QPushButton { padding: 8px; border-radius: 5px; background-color: #3498db; color: white; }")
        export_btn.clicked.connect(self.export_log)
        control_layout.addWidget(clear_btn)
        control_layout.addWidget(export_btn)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
    def update_data(self):
        # Only update if system is running
        if not self.system_running:
            return
            
        # Simulate temperature and humidity changes
        current_temp = float(self.temp_label.text().replace('°C', ''))
        target_temp = float(self.target_label.text().replace('°C', ''))
        
        # Calculate and display error
        error = current_temp - target_temp
        error_color = "#e67e22"  # Default orange
        if error > 2:
            error_color = "#e74c3c"  # Red for large positive error
        elif error < -2:
            error_color = "#3498db"  # Blue for large negative error
        elif abs(error) < 0.5:
            error_color = "#2ecc71"  # Green for small error
            
        self.error_label.setText(f"{error:+.1f}°C")
        self.error_label.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {error_color}; padding: 10px;")
        
        # Simulate some random variation
        variation = random.uniform(-0.5, 0.5)
        new_temp = current_temp + variation
        
        # If automation is enabled, move toward target temperature
        if self.auto_button.isChecked():
            if new_temp > target_temp + 0.2:
                new_temp -= 0.1  # Simulate cooling
            elif new_temp < target_temp - 0.2:
                new_temp += 0.1  # Simulate heating
        
        # Update temperature display
        self.temp_label.setText(f"{new_temp:.1f}°C")
        
        # Update humidity (simulate small changes)
        current_humidity = float(self.humidity_label.text().replace('%', ''))
        new_humidity = current_humidity + random.uniform(-1, 1)
        new_humidity = max(30, min(70, new_humidity))  # Keep within reasonable bounds
        self.humidity_label.setText(f"{new_humidity:.0f}%")
        
        # Update graphs
        self.temp_data.append(new_temp)
        self.humidity_data.append(new_humidity)
        self.time_data.append(self.time_data[-1] + 1 if self.time_data else 0)
        
        self.temp_plot.setData(list(self.time_data), list(self.temp_data))
        self.humidity_plot.setData(list(self.time_data), list(self.humidity_data))
        
        # Add log entry occasionally
        if random.random() < 0.2:  # 20% chance each update
            log_msg = f"Temperature: {new_temp:.1f}°C, Humidity: {new_humidity:.0f}%"
            self.log_entries.append(QDateTime.currentDateTime().toString("hh:mm:ss") + " - " + log_msg)
            if len(self.log_entries) > 50:
                self.log_entries.pop(0)
            self.update_log_display()
            
        # Update status bar
        self.status_bar.showMessage(f"Current: {new_temp:.1f}°C, Target: {target_temp}°C, Humidity: {new_humidity:.0f}%")
        
    def toggle_system(self):
        if not self.system_running:
            # Start the system
            self.system_running = True
            self.system_button.setText("Stop System")
            self.system_button.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; padding: 10px; border-radius: 5px; font-weight: bold; }"
                                           "QPushButton:hover { background-color: #c0392b; }")
            self.system_status_label.setText("System Status: ON")
            self.system_status_label.setStyleSheet("font-weight: bold; color: #2ecc71;")
            
            # Enable control buttons
            self.cool_button.setEnabled(True)
            self.heat_button.setEnabled(True)
            self.fan_button.setEnabled(True)
            
            self.log_entries.append(QDateTime.currentDateTime().toString("hh:mm:ss") + " - System started")
        else:
            # Stop the system
            self.system_running = False
            self.system_button.setText("Start System")
            self.system_button.setStyleSheet("QPushButton { background-color: #2ecc71; color: white; padding: 10px; border-radius: 5px; font-weight: bold; }"
                                           "QPushButton:hover { background-color: #27ae60; }")
            self.system_status_label.setText("System Status: OFF")
            self.system_status_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
            
            # Disable control buttons
            self.cool_button.setEnabled(False)
            self.heat_button.setEnabled(False)
            self.fan_button.setEnabled(False)
            
            self.log_entries.append(QDateTime.currentDateTime().toString("hh:mm:ss") + " - System stopped")
            
        self.update_log_display()
        
    def update_target_temp(self):
        target_temp = self.target_slider.value()
        self.target_label.setText(f"{target_temp}°C")
        self.target_display.setText(f"{target_temp}°C")
        
        # Add to log
        self.log_entries.append(QDateTime.currentDateTime().toString("hh:mm:ss") + 
                               f" - Target temperature changed to {target_temp}°C")
        self.update_log_display()
        
    def update_threshold(self):
        threshold = self.threshold_slider.value()
        self.threshold_display.setText(f"±{threshold}°C")
        
    def toggle_cooling(self):
        if self.cool_button.text() == "Start Cooling":
            self.cool_button.setText("Stop Cooling")
            self.cool_button.setStyleSheet("QPushButton { background-color: #2980b9; color: white; padding: 10px; border-radius: 5px; }")
            self.log_entries.append(QDateTime.currentDateTime().toString("hh:mm:ss") + " - Cooling started")
        else:
            self.cool_button.setText("Start Cooling")
            self.cool_button.setStyleSheet("QPushButton { background-color: #3498db; color: white; padding: 10px; border-radius: 5px; }")
            self.log_entries.append(QDateTime.currentDateTime().toString("hh:mm:ss") + " - Cooling stopped")
        self.update_log_display()
        
    def toggle_heating(self):
        if self.heat_button.text() == "Start Heating":
            self.heat_button.setText("Stop Heating")
            self.heat_button.setStyleSheet("QPushButton { background-color: #c0392b; color: white; padding: 10px; border-radius: 5px; }")
            self.log_entries.append(QDateTime.currentDateTime().toString("hh:mm:ss") + " - Heating started")
        else:
            self.heat_button.setText("Start Heating")
            self.heat_button.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; padding: 10px; border-radius: 5px; }")
            self.log_entries.append(QDateTime.currentDateTime().toString("hh:mm:ss") + " - Heating stopped")
        self.update_log_display()
        
    def toggle_fans(self):
        self.log_entries.append(QDateTime.currentDateTime().toString("hh:mm:ss") + " - Fans toggled")
        self.update_log_display()
        
    def toggle_automation(self):
        if self.auto_button.isChecked():
            self.auto_button.setText("Enabled")
            self.log_entries.append(QDateTime.currentDateTime().toString("hh:mm:ss") + " - Automation enabled")
        else:
            self.auto_button.setText("Disabled")
            self.log_entries.append(QDateTime.currentDateTime().toString("hh:mm:ss") + " - Automation disabled")
        self.update_log_display()
        
    def toggle_notifications(self):
        if self.notif_button.isChecked():
            self.notif_button.setText("Enabled")
            self.log_entries.append(QDateTime.currentDateTime().toString("hh:mm:ss") + " - Notifications enabled")
        else:
            self.notif_button.setText("Disabled")
            self.log_entries.append(QDateTime.currentDateTime().toString("hh:mm:ss") + " - Notifications disabled")
        self.update_log_display()
        
    def update_log_display(self):
        self.log_display.setText("\n".join(self.log_entries))
        
    def clear_log(self):
        self.log_entries = ["Log cleared at " + QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")]
        self.update_log_display()
        
    def export_log(self):
        # Get file path to save with multiple format options
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, 
            "Export Log", 
            f"temperature_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}", 
            "PDF Files (*.pdf);;Word Documents (*.docx);;Text Files (*.txt);;CSV Files (*.csv)"
        )
        
        if not file_path:
            return  # User cancelled the dialog
            
        try:
            # Determine the format based on the selected filter
            if selected_filter == "PDF Files (*.pdf)":
                if not file_path.endswith('.pdf'):
                    file_path += '.pdf'
                self.export_to_pdf(file_path)
            elif selected_filter == "Word Documents (*.docx)":
                if not file_path.endswith('.docx'):
                    file_path += '.docx'
                self.export_to_word(file_path)
            elif selected_filter == "CSV Files (*.csv)":
                if not file_path.endswith('.csv'):
                    file_path += '.csv'
                self.export_to_csv(file_path)
            else:  # Text file
                if not file_path.endswith('.txt'):
                    file_path += '.txt'
                self.export_to_text(file_path)
                
            self.log_entries.append(QDateTime.currentDateTime().toString("hh:mm:ss") + f" - Log exported to {os.path.basename(file_path)}")
            self.update_log_display()
            self.status_bar.showMessage(f"Log successfully exported to {file_path}")
            
        except Exception as e:
            self.log_entries.append(QDateTime.currentDateTime().toString("hh:mm:ss") + f" - Error exporting log: {str(e)}")
            self.update_log_display()
            self.status_bar.showMessage(f"Error exporting log: {str(e)}")
    
    def export_to_pdf(self, file_path):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_path)
        printer.setPageSize(QPrinter.A4)
        
        document = QTextDocument()
        cursor = QTextCursor(document)
        
        # Add title
        title_format = QTextCharFormat()
        title_format.setFont(QFont("Arial", 16, QFont.Bold))
        cursor.insertText("Temperature Control System Log\n", title_format)
        
        # Add timestamp
        timestamp_format = QTextCharFormat()
        timestamp_format.setFont(QFont("Arial", 10))
        cursor.insertText(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n", timestamp_format)
        
        # Add log entries
        for entry in self.log_entries:
            cursor.insertText(entry + "\n")
        
        document.print_(printer)
    
    def export_to_word(self, file_path):
        # For Word documents, we'll create a simple text-based document
        # In a real application, you might use python-docx for more advanced formatting
        with open(file_path, 'w') as f:
            f.write("Temperature Control System Log\n")
            f.write(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for entry in self.log_entries:
                f.write(entry + "\n")
    
    def export_to_csv(self, file_path):
        with open(file_path, 'w', newline='') as file:
            file.write("Timestamp,Message\n")
            for entry in self.log_entries:
                if " - " in entry:
                    timestamp, message = entry.split(" - ", 1)
                    file.write(f'"{timestamp}","{message}"\n')
                else:
                    file.write(f'"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}","{entry}"\n')
    
    def export_to_text(self, file_path):
        with open(file_path, 'w') as file:
            file.write("Temperature Control System Log\n")
            file.write(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for entry in self.log_entries:
                file.write(entry + "\n")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = TemperatureControlSystem()
    window.show()
    
    sys.exit(app.exec_())