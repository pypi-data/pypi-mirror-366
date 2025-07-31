import sys
import hid
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QGroupBox, QGridLayout
from PyQt6.QtCore import Qt
from qfluentwidgets import (setTheme, Theme, FluentWindow, PushButton, ComboBox, Slider, CheckBox, InfoBar, InfoBarPosition)

from src.servo import Servo, Sensitivity, LosePPMProtection

# Vendor ID and Product ID for Axon servo adapter
VENDOR_ID = 0x0471
PRODUCT_ID = 0x13aa

class ServoGUI(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Axon Servo Programmer")
        self.servo = None
        self.device = None

        # Timer for polling servo presence
        from PyQt6.QtCore import QTimer
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(400)  # ms
        self.poll_timer.timeout.connect(self.poll_servo_presence)

        # Hide the navigation panel
        self.navigationInterface.hide()

        # Create main interface
        self.main_interface = QWidget()
        self.init_ui()
        self.update_device_status()

        self.stackedWidget.addWidget(self.main_interface)

    def init_ui(self):
        main_layout = QVBoxLayout(self.main_interface)

        # Device Status
        status_layout = QHBoxLayout()
        main_layout.addLayout(status_layout)
        self.status_label = QLabel("Device Status: Disconnected")
        status_layout.addWidget(self.status_label)
        self.servo_status_label = QLabel("Servo Status: Unknown")
        status_layout.addWidget(self.servo_status_label)
        self.connect_button = PushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_device_connection)
        status_layout.addWidget(self.connect_button)

        # File Operations
        file_group = QGroupBox("File")
        file_layout = QHBoxLayout()
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        self.read_file_button = PushButton("Read from File")
        self.read_file_button.clicked.connect(self.read_from_file)
        file_layout.addWidget(self.read_file_button)

        self.save_button = PushButton("Save to File")
        self.save_button.clicked.connect(self.save_to_file)
        file_layout.addWidget(self.save_button)

        # Device Operations
        device_group = QGroupBox("Device")
        device_layout = QHBoxLayout()
        device_group.setLayout(device_layout)
        main_layout.addWidget(device_group)

        self.read_device_button = PushButton("Read from Servo")
        self.read_device_button.clicked.connect(self.read_from_device)
        device_layout.addWidget(self.read_device_button)

        self.write_to_device_button = PushButton("Write to Servo")
        self.write_to_device_button.clicked.connect(self.write_to_device)
        device_layout.addWidget(self.write_to_device_button)

        self.write_default_button = PushButton("Default")
        self.write_default_button.clicked.connect(self.write_default_settings)
        device_layout.addWidget(self.write_default_button)

        # Servo Parameters
        params_group = QGroupBox("Parameters")
        params_layout = QGridLayout()
        params_group.setLayout(params_layout)
        main_layout.addWidget(params_group)

        # Servo Angle
        params_layout.addWidget(QLabel("Servo Angle [1-255]:"), 0, 0)
        self.angle_slider = Slider(Qt.Orientation.Horizontal)
        self.angle_slider.setRange(1, 255)
        params_layout.addWidget(self.angle_slider, 0, 1)
        self.angle_label = QLabel("1")
        self.angle_slider.valueChanged.connect(lambda v: self.angle_label.setText(str(v)))
        params_layout.addWidget(self.angle_label, 0, 2)

        # Servo Neutral
        params_layout.addWidget(QLabel("Servo Neutral [-127-127]:"), 1, 0)
        self.neutral_slider = Slider(Qt.Orientation.Horizontal)
        self.neutral_slider.setRange(-127, 127)
        params_layout.addWidget(self.neutral_slider, 1, 1)
        self.neutral_label = QLabel("0")
        self.neutral_slider.valueChanged.connect(lambda v: self.neutral_label.setText(str(v)))
        params_layout.addWidget(self.neutral_label, 1, 2)

        # Damping Factor
        params_layout.addWidget(QLabel("Damping Factor [50-600]:"), 2, 0)
        self.damping_slider = Slider(Qt.Orientation.Horizontal)
        self.damping_slider.setRange(50, 600)
        params_layout.addWidget(self.damping_slider, 2, 1)
        self.damping_label = QLabel("50")
        self.damping_slider.valueChanged.connect(lambda v: self.damping_label.setText(str(v)))
        params_layout.addWidget(self.damping_label, 2, 2)

        # PWM Power
        params_layout.addWidget(QLabel("PWM Power [39.2-100]%"), 3, 0)
        self.pwm_slider = Slider(Qt.Orientation.Horizontal)
        self.pwm_slider.setRange(392, 1000)
        params_layout.addWidget(self.pwm_slider, 3, 1)
        self.pwm_label = QLabel("39.2")
        self.pwm_slider.valueChanged.connect(lambda v: self.pwm_label.setText(f"{v/10.0:.1f}"))
        params_layout.addWidget(self.pwm_label, 3, 2)

        # Sensitivity
        params_layout.addWidget(QLabel("Sensitivity:"), 4, 0)
        self.sensitivity_combo = ComboBox()
        self.sensitivity_combo.addItems([s.value for s in Sensitivity])
        params_layout.addWidget(self.sensitivity_combo, 4, 1, 1, 2)

        # Booleans
        bool_layout = QHBoxLayout()
        self.soft_start_check = CheckBox("Soft Start")
        self.inversion_check = CheckBox("Inversion")
        self.overload_protection_check = CheckBox("Overload Protection")
        bool_layout.addWidget(self.soft_start_check)
        bool_layout.addWidget(self.inversion_check)
        bool_layout.addWidget(self.overload_protection_check)
        params_layout.addLayout(bool_layout, 5, 1, 1, 2)

        # Lose PPM Protection
        params_layout.addWidget(QLabel("Lose PPM Protection:"), 6, 0)
        self.lose_ppm_combo = ComboBox()
        self.lose_ppm_combo.addItems([p.value for p in LosePPMProtection])
        params_layout.addWidget(self.lose_ppm_combo, 6, 1, 1, 2)

    def toggle_device_connection(self):
        if self.device:
            self.poll_timer.stop()
            self.device.close()
            self.device = None
            self.servo = None
        else:
            try:
                self.device = hid.device()
                self.device.open(VENDOR_ID, PRODUCT_ID)
                self.device.set_nonblocking(True)
                self.poll_timer.start()
            except (IOError, OSError) as e:
                self.device = None
                InfoBar.error(
                    title='Error',
                    content=f"Failed to connect to device: {e}",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self
                )
        self.update_device_status()
    def poll_servo_presence(self):
        if not self.device:
            self.servo_status_label.setText("Servo Status: Unknown")
            return
        try:
            poll_command = [0x04, 0x8A, 0x00, 0x00, 0x04] + [0x00] * (64 - 5)
            self.device.write(poll_command)
            import time as _time
            _time.sleep(0.05)
            report = self.device.read(64)
            if report:
                if (
                    len(report) >= 6 and
                    report[0] == 0x04 and
                    report[1] == 0x01 and
                    report[2] == 0x00 and
                    report[3] == 0x01 and
                    report[5] == 0x03
                ):
                    self.servo_status_label.setText("Servo Status: Connected")
                else:
                    self.servo_status_label.setText("Servo Status: Disconnected")
            else:
                self.servo_status_label.setText("Servo Status: Disconnected")
        except Exception:
            self.servo_status_label.setText("Servo Status: Unknown")

    def update_device_status(self):
        if self.device:
            self.status_label.setText("Device Status: Connected")
            self.connect_button.setText("Disconnect")
            self.read_device_button.setEnabled(True)
            self.write_to_device_button.setEnabled(True)
            self.write_default_button.setEnabled(True)
            # Servo status will be updated by polling
        else:
            self.status_label.setText("Device Status: Disconnected")
            self.connect_button.setText("Connect")
            self.read_device_button.setEnabled(False)
            self.write_to_device_button.setEnabled(False)
            self.write_default_button.setEnabled(False)
            self.servo_status_label.setText("Servo Status: Unknown")


    def write_default_settings(self):
        if not self.servo:
            self.servo = Servo()
        # Write default settings to the servo
        try:
            #self.servo.write_to_HID()
            pass
        except Exception as e:
            InfoBar.error(
                title='Error',
                content=f"Failed to write default settings: {e}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
            return
        self.update_gui_from_servo()
        
        InfoBar.success(
            title='Success',
            content="Default settings written to servo.",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )

    def read_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Servo Config", "", "Servo Files (*.svo)")
        if file_path:
            try:
                self.servo = Servo(file_path=file_path)
                self.update_gui_from_servo()
                InfoBar.success(
                    title='Success',
                    content=f"Successfully loaded {file_path}",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
            except Exception as e:
                InfoBar.error(
                    title='Error',
                    content=f"Error reading file: {e}",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self
                )

    def save_to_file(self):
        if not self.servo:
            self.servo = Servo()
        self.update_servo_from_gui()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Servo Config", "", "Servo Files (*.svo)")
        if file_path:
            try:
                self.servo.save_to_file(file_path)
                InfoBar.success(
                    title='Success',
                    content=f"Successfully saved to {file_path}",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
            except Exception as e:
                InfoBar.error(
                    title='Error',
                    content=f"Error saving file: {e}",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self
                )

    def read_from_device(self):
        if not self.device:
            InfoBar.warning(
                title='Warning',
                content="Device not connected.",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        try:
            self.servo = Servo(device=self.device)
            self.update_gui_from_servo()
            self.update_device_status()
            InfoBar.success(
                title='Success',
                content="Successfully read from servo.",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
        except Exception as e:
            InfoBar.error(
                title='Error',
                content=f"Failed to read from servo: {e}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )

    def write_to_device(self):
        if not self.device:
            InfoBar.warning(
                title='Warning',
                content="Device not connected.",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        if not self.servo:
            self.servo = Servo()
        self.update_servo_from_gui()
        try:
            self.servo.write_to_HID()
            InfoBar.success(
                title='Success',
                content="Successfully wrote to servo.",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
        except Exception as e:
            InfoBar.error(
                title='Error',
                content=f"Failed to write to servo: {e}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )

    def update_gui_from_servo(self):
        if not self.servo:
            return
        self.angle_slider.setValue(self.servo.angle)
        self.neutral_slider.setValue(self.servo.neutral)
        self.damping_slider.setValue(self.servo.damping_factor)
        self.pwm_slider.setValue(int(self.servo.pwm_power * 10))
        self.sensitivity_combo.setCurrentText(self.servo.sensitivity.value)
        self.soft_start_check.setChecked(self.servo.soft_start)
        self.inversion_check.setChecked(self.servo.inversion)
        self.overload_protection_check.setChecked(self.servo.overload_protection)
        self.lose_ppm_combo.setCurrentText(self.servo.lose_ppm_protection.value)

    def update_servo_from_gui(self):
        if not self.servo:
            self.servo = Servo()
        self.servo.angle = self.angle_slider.value()
        self.servo.neutral = self.neutral_slider.value()
        self.servo.damping_factor = self.damping_slider.value()
        self.servo.pwm_power = self.pwm_slider.value() / 10.0
        self.servo.sensitivity = Sensitivity(self.sensitivity_combo.currentText())
        self.servo.soft_start = self.soft_start_check.isChecked()
        self.servo.inversion = self.inversion_check.isChecked()
        self.servo.overload_protection = self.overload_protection_check.isChecked()
        self.servo.lose_ppm_protection = LosePPMProtection(self.lose_ppm_combo.currentText())

def main():
    # Enable high DPI scaling if available
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    if hasattr(Qt.HighDpiScaleFactorRoundingPolicy, 'PassThrough'):
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    setTheme(Theme.DARK)

    app = QApplication(sys.argv)
    gui = ServoGUI()
    gui.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()