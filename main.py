import sys
import serial
import serial.tools.list_ports
from PyQt6 import QtWidgets, QtCore

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
        self.baudrate_combobox.addItems(["9600", "38400", "57600", "115200"])  # Предустановленные значения
        layout.addWidget(self.baudrate_combobox)

        # Open/Close button
        self.open_button = QtWidgets.QPushButton('Open Port')
        self.open_button.clicked.connect(self.toggle_port)
        layout.addWidget(self.open_button)

        # Input text field
        self.input_field = QtWidgets.QLineEdit()
        layout.addWidget(self.input_field)

        # Send button
        self.send_button = QtWidgets.QPushButton('Send')
        self.send_button.clicked.connect(self.send_data)
        layout.addWidget(self.send_button)

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
        else:
            selected_port = self.port_combobox.currentText()
            selected_baudrate = int(self.baudrate_combobox.currentText())  # Получаем выбранный baudrate
            self.serial_port = serial.Serial(selected_port, baudrate=selected_baudrate, timeout=1)
            self.open_button.setText('Close Port')

    def send_data(self):
        if self.serial_port and self.serial_port.is_open:
            data = self.input_field.text()
            self.serial_port.write(data.encode())
            self.output_area.append(f'Sent: {data}')
            self.input_field.clear()

    def read_data(self):
        if self.serial_port and self.serial_port.is_open:
            if self.serial_port.in_waiting > 0:
                data = self.serial_port.read(self.serial_port.in_waiting).decode()
                self.output_area.append(f'Received: {data}')

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
