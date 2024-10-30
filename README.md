# Python UART GPIO Control Application

This Python application provides a graphical user interface (GUI) for controlling and monitoring GPIO pins of a PIC microcontroller via UART communication. Users can send commands to read GPIO states and set the state of specific pins (high or low) easily.

## Features

- **UART Communication:** Seamless communication with a PIC microcontroller using customizable baud rates.
- **GUI Interface:** User-friendly interface built with PyQt6 for easy interaction.
- **GPIO Control:** Read and manipulate GPIO states of the PIC microcontroller (GP2 to GP5).
- **Dynamic Command Handling:** Automatically updates and processes commands based on user input.
- **Output Handling:** Displays received data and errors in a non-clickable output area, ensuring clarity.

## Requirements

- Python 3.x
- PyQt6
- pySerial

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/m3iz/uart-test-suite.git
   cd uart-test-suite
   ```

2. **Install Poetry:**
   If you haven't installed Poetry yet, you can do so by following the instructions on the [Poetry website](https://python-poetry.org/docs/#installation).

3. **Install Required Packages:**
   Once Poetry is installed, run:
   ```bash
   poetry install
   ```

4. **Connect the PIC Microcontroller:**
   - Ensure the PIC microcontroller is connected via a UART-compatible interface (like a USB-to-serial adapter).
   - Make sure the firmware is correctly uploaded to the microcontroller to handle the expected commands.

## Usage

1. **Run the Application:**
   Launch the application using:
   ```bash
   poetry run python main.py
   ```

2. **Select Serial Port:**
   Choose the appropriate serial port from the dropdown list.

3. **Set Baud Rate:**
   Select a baud rate compatible with the PIC firmware (default is 1200 bps).

4. **Open the Port:**
   Click the "Open Port" button to establish a connection with the microcontroller.

5. **Send Commands:**
   - Use the provided buttons to send commands:
     - **Read GPIO States**: Sends a command to read the current states of GPIO pins GP2 to GP5.
     - **Set GPIO Pins**: Choose the appropriate button to set the specified pin high or low.
   - The output area will display the responses from the microcontroller.

6. **Close the Port:**
   After completing your tasks, click the "Close Port" button to safely disconnect.

## Command Format

Commands sent to the microcontroller are processed as follows:

- **Read GPIO States:** 
  - Sends the command to read GPIO states, expecting a response in the format: `{1/0,1/0,0/1,1/0,1/0}`.
  
- **Set GPIO High:**
  - Sends commands like `X`, where `X` is the pin number (2-5) to set it high.
  
- **Set GPIO Low:**
  - Sends commands like `X`, where `X` is the pin number minus 4 to set it low.

## Troubleshooting

- Ensure the correct COM port and baud rate are selected.
- Check for proper wiring and connections to the microcontroller.
- Monitor the output area for any error messages regarding invalid command formats.

## Acknowledgments

- PyQt6 and pySerial for providing the necessary libraries for building the GUI and UART communication.
