**Computer Laboratory Temperature Control System**
A professional GUI-based monitoring and control application developed as a final year project for Adamawa State University (ADSU), Mubi. This system provides a comprehensive interface for managing environmental conditions in a computer laboratory setting, ensuring equipment longevity and optimal performance.

**Key Features**
_Real-Time Data Monitoring_: Visualizes temperature and humidity trends using PyQtGraph with dynamic updates every 2 seconds.

_Automated Control Logic_: Intelligent automation mode that simulates cooling/heating adjustments based on user-defined setpoints and thresholds.

_Interactive Dashboard_: * Dynamic "Error" calculation (Difference between setpoint and actual temp).

Manual overrides for Fans, Cooling, and Heating systems.

Adjustable target parameters via intuitive sliders.

_Comprehensive Logging & Exporting_: * Tracks all system events and environmental fluctuations.

_Multi-Format Export_: Save system logs as PDF, Microsoft Word (.docx), CSV, or Text files for administrative reporting.

University-Branded UI: Professional interface styled with the 'Fusion' theme, featuring ADSU Mubi institutional branding.

**Technologies Used**
Python 3.x

PyQt5: For the core Graphical User Interface (GUI).

PyQtGraph: For high-performance, real-time data plotting.

Python-Docx: For generating Microsoft Word reports.

PyQt PrintSupport: For PDF generation.

**Installation & Setup**

_Clone the Repository_:
git clone https://github.com/eshek2020/temperature-control-system.git
cd temperature-control-system

_Install Dependencies_: Make sure you have pip installed, then run:
pip install PyQt5 pyqtgraph python-docx

_Run the Application_:
python main.py

**Usage Guide**
_Start System_: Click the "Start System" button to begin real-time data simulation.

_Adjust Setpoints_: Use the Settings tab to change the "Target Temperature" and "Threshold."

_Monitor Trends_: Watch the Dashboard to see the red (Temp) and blue (Humidity) lines update in real-time.

_Export Data_: Navigate to the System Log tab to view historical events and click "Export Log" to save your report in your preferred format.

🏫 Institutional Credit
This project was developed by me at the Department of Computer Science, Adamawa State University, Mubi. It serves as a proof-of-concept for localized climate control automation in high-density computing environments.
