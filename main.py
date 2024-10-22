import sys
import serial
import serial.tools.list_ports
from PyQt6 import QtWidgets, QtCore, QtGui


class SerialApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.serial_port = None
        self.append_newline = False  # Flag to track newline character

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

        # Checkbox for newline option (\r\n)
        self.newline_checkbox = QtWidgets.QCheckBox('Send with \\r\\n (carriage return + newline)')
        self.newline_checkbox.stateChanged.connect(self.toggle_newline)
        layout.addWidget(self.newline_checkbox)

        # Command list for GPIO control
        self.command_list = QtWidgets.QListWidget()
        self.command_list.setVisible(False)  # Hidden initially, becomes visible on successful port open
        layout.addWidget(self.command_list)

        # Input text field for additional commands
        self.input_field = QtWidgets.QLineEdit()
        layout.addWidget(self.input_field)

        # Send button
        self.send_button = QtWidgets.QPushButton('Send')
        self.send_button.clicked.connect(self.send_data)
        layout.addWidget(self.send_button)

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
            self.command_list.setVisible(False)
        else:
            selected_port = self.port_combobox.currentText()
            selected_baudrate = int(self.baudrate_combobox.currentText())  # Получаем выбранный baudrate

            try:
                self.serial_port = serial.Serial(selected_port, baudrate=selected_baudrate, timeout=1)
                if self.serial_port.is_open:
                    self.output_message("Port opened successfully!", QtGui.QColor('green'))
                    self.open_button.setText('Close Port')
                    self.populate_gpio_commands()
            except serial.SerialException as e:
                self.output_message(f"Error: {str(e)}", QtGui.QColor('red'))

    def populate_gpio_commands(self):
        """Populate the list with GPIO control commands."""
        self.command_list.clear()  # Clear previous commands if any
        self.command_list.setVisible(True)

        # Adding headers for information (non-clickable items)
        self.add_non_clickable_item("-- Read GPIO States --")
        for i in range(1, 7):
            self.command_list.addItem(f'Read GPIO {i}')

        self.add_non_clickable_item("-- Set GPIO States --")
        for i in range(1, 7):
            self.command_list.addItem(f'Set GPIO {i} Up')
            self.command_list.addItem(f'Set GPIO {i} Down')

        self.command_list.itemClicked.connect(self.handle_command_click)

    def add_non_clickable_item(self, text):
        """Add a non-clickable item to the command list."""
        item = QtWidgets.QListWidgetItem(text)
        item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsSelectable)  # Remove selection capability
        item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEnabled)  # Remove clickability
        self.command_list.addItem(item)

    def handle_command_click(self, item):
        """Handle the click event when a command is selected."""
        command = item.text()
        if 'Read' in command:
            gpio_num = command.split(' ')[2]
            command_to_send = f'READ_GPIO_{gpio_num}'
        elif 'Set' in command:
            gpio_num, state = command.split(' ')[2], command.split(' ')[3]
            command_to_send = f'SET_GPIO_{gpio_num}_{state.upper()}'

        # Insert the command into the input field for user to send later
        self.input_field.setText(command_to_send)

    def toggle_newline(self, state):
        """Toggle whether to send commands with \r\n."""
        self.append_newline = (state == QtCore.Qt.CheckState.Checked)

    def clear_output(self):
        """Clear the output area."""
        self.output_area.clear()

    def output_message(self, message, color):
        self.output_area.setTextColor(color)
        self.output_area.append(message)
        self.output_area.setTextColor(QtGui.QColor('black'))  # Reset to default color

    def send_data(self):
        if self.serial_port and self.serial_port.is_open:
            data = self.input_field.text()
            if self.append_newline:
                data += '\r\n'
            self.serial_port.write(data.encode())
            self.output_area.append(f'Sent: {data.strip()}')
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
