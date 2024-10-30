import sys
import serial
import serial.tools.list_ports
from PyQt6 import QtWidgets, QtCore, QtGui


class SerialApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.serial_port = None

    def initUI(self):
        self.setWindowTitle('UART Serial Communication')

        # Layout
        layout = QtWidgets.QVBoxLayout()

        # ComboBox for ports
        self.port_combobox = QtWidgets.QComboBox()
        self.refresh_ports()
        layout.addWidget(self.port_combobox)

        # ComboBox for baud rates
        self.baudrate_combobox = QtWidgets.QComboBox()
        self.baudrate_combobox.addItems(["1170", "1200", "57600", "115200"])  # Предустановленные значения
        layout.addWidget(self.baudrate_combobox)

        # Open/Close button
        self.open_button = QtWidgets.QPushButton('Open Port')
        self.open_button.clicked.connect(self.toggle_port)
        layout.addWidget(self.open_button)

        # Command buttons for GPIO control
        self.command_buttons_layout = QtWidgets.QVBoxLayout()

        # Button for reading GPIO
        self.read_gpio_button = QtWidgets.QPushButton('Read GPIO')
        self.read_gpio_button.clicked.connect(self.send_read_gpio)
        self.command_buttons_layout.addWidget(self.read_gpio_button)

        # Buttons for setting GPIO states
        for i in range(2, 6):  # GP2 to GP5
            set_high_button = QtWidgets.QPushButton(f'Set GP{i} High')
            set_high_button.clicked.connect(lambda _, num=i: self.send_set_gpio_high(num))
            self.command_buttons_layout.addWidget(set_high_button)

            set_low_button = QtWidgets.QPushButton(f'Set GP{i} Low')
            set_low_button.clicked.connect(lambda _, num=i: self.send_set_gpio_low(num))
            self.command_buttons_layout.addWidget(set_low_button)

        # Initially hide the command buttons
        for i in range(self.command_buttons_layout.count()):
            button = self.command_buttons_layout.itemAt(i).widget()
            if button:
                button.setVisible(False)

        layout.addLayout(self.command_buttons_layout)

        # Button to clear the output area
        self.clear_button = QtWidgets.QPushButton('Clear Output')
        self.clear_button.clicked.connect(self.clear_output)
        layout.addWidget(self.clear_button)

        # Output text area
        self.output_area = QtWidgets.QTextEdit()
        layout.addWidget(self.output_area)

        self.setLayout(layout)
        self.show()

    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_combobox.clear()
        for port in ports:
            self.port_combobox.addItem(port.device)

    def toggle_port(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.open_button.setText('Open Port')
            # Hide command buttons
            for i in range(self.command_buttons_layout.count()):
                button = self.command_buttons_layout.itemAt(i).widget()
                if button:
                    button.setVisible(False)
        else:
            selected_port = self.port_combobox.currentText()
            selected_baudrate = int(self.baudrate_combobox.currentText())  # Получаем выбранный baudrate

            try:
                self.serial_port = serial.Serial(selected_port, baudrate=selected_baudrate, timeout=1)
                if self.serial_port.is_open:
                    self.output_message("Port opened successfully!", QtGui.QColor('green'))
                    self.open_button.setText('Close Port')
                    # Show command buttons
                    for i in range(self.command_buttons_layout.count()):
                        button = self.command_buttons_layout.itemAt(i).widget()
                        if button:
                            button.setVisible(True)
            except serial.SerialException as e:
                self.output_message(f"Error: {str(e)}", QtGui.QColor('red'))

    def send_read_gpio(self):
        self.send_data('0')  # Send command '0' to read GPIO

    def send_set_gpio_high(self, gpio_num):
        self.send_data(str(gpio_num))  # Send GPIO number as string for High

    def send_set_gpio_low(self, gpio_num):
        low_command = str(gpio_num + 4)  # Send GPIO number + 4 for Low (GP2=6, GP3=7, GP4=8, GP5=9)
        self.send_data(low_command)

    def clear_output(self):
        """Clear the output area."""
        self.output_area.clear()

    def output_message(self, message, color):
        self.output_area.setTextColor(color)
        self.output_area.append(message)
        self.output_area.setTextColor(QtGui.QColor('black'))  # Reset to default color

    def send_data(self, data):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(data.encode())
            self.output_area.append(f'Sent: {data.strip()}')

    def read_data(self):
        if self.serial_port and self.serial_port.is_open:
            if self.serial_port.in_waiting > 0:
                data = self.serial_port.read(self.serial_port.in_waiting).decode()
                self.process_received_data(data)

    def process_received_data(self, data):
        """Process the received GPIO states and format them for display."""
        # Check if the data length is correct for GP2 to GP5 (4 states)
        if len(data) == 4 and all(c in '01' for c in data):
            formatted_states = []

            # Map the states to GPIO pins (GP2 to GP5)
            for i in range(len(data)):
                pin_value = "High" if data[i] == '1' else "Low"
                formatted_states.append(f'GP{i + 2}: {pin_value}')

            # Join formatted states into a single string
            output_string = ', '.join(formatted_states)
            self.output_area.append(f'Received GPIO States: {output_string}')
        else:
            self.output_area.append(f'Invalid data format: {data}')

    def closeEvent(self, event):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    serial_app = SerialApp()

    # Timer to read data periodically
    timer = QtCore.QTimer()
    timer.timeout.connect(serial_app.read_data)
    timer.start(100)

    sys.exit(app.exec())
