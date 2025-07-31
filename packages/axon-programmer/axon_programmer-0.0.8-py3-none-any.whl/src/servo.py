from enum import Enum
from typing import Tuple
import os
import hid

class Sensitivity(Enum):
    ULTRA_HIGH = "Ultra High"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class LosePPMProtection(Enum):
    RELEASE = "Release"
    KEEP_POSITION = "Keep Position"
    GO_NEUTRAL_POSITION = "Go Neutral Position"

# The Level class remains, but its usage will be commented out in Servo
class Level:
    def __init__(self, seconds: float, percentage: float):
        self.seconds = max(0.0, min(10.5, seconds))
        self.percentage = max(29.0, min(100.0, percentage))

    def __repr__(self):
        return f"Level(seconds={self.seconds}, percentage={self.percentage})"

class Servo:
    SVO_FILE_LENGTH = 95
    DEFAULT_HEX_STRING = """
        3B D0 0B F6 82 82 80 03 00 3C 00 55 10 00 00 D2 
        0A E6 E6 E6 24 1C 18 14 19 00 3C 00 3C 00 3C 00 
        00 00 00 00 01 E1 C0 00 55 00 55 00 55 00 00 00 
        0F 0A 16 00 00 C0 50 78 50 50 64 23 E3 00 00 00 
        53 41 38 31 42 48 4D 57 00 00 00 00 00 00 00 00 
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 01
    """

    def __init__(
        self,
        file_path: str = None,
        device: 'hid.device' = None,
        # level1: Level = Level(0.0, 100.0), # Commented out for now
        # level2: Level = Level(0.0, 100.0), # Commented out for now
        # level3: Level = Level(0.0, 100.0), # Commented out for now
    ):
        if file_path:
            self._parse_from_file(file_path)
        elif device:
            self.device = device
            self.servo_connected = False
            self._from_HID()
            # self.level1 = self._validate_level(level1) # Commented out for now
            # self.level2 = self._validate_level(level2) # Commented out for now
            # self.level3 = self._validate_level(level3) # Commented out for now
        else:
            # Initialize with default values if no file or device is provided
            self._load_from_hex_string(self.DEFAULT_HEX_STRING)
        

    @staticmethod
    def _clamp(value, min_value, max_value):
        return max(min_value, min(max_value, value))

    # @staticmethod
    # def _validate_level(level: Level) -> Level: # Commented out for now
    #     if not isinstance(level, Level):
    #         raise ValueError("Level must be an instance of Level class")
    #     return level

    def _load_from_hex_string(self, hex_string: str):
        """
        Load servo configuration from a hex string.
        """
        file_data = bytearray(bytes.fromhex(hex_string.replace(" ", "")))
        if len(file_data) != self.SVO_FILE_LENGTH:
            raise ValueError(f"SVO file must be exactly {self.SVO_FILE_LENGTH} bytes long, but got {len(file_data)} bytes.")
        
        self._parse_from_file(file_data)
        self.device = None

    def _from_HID(self):
        #TODO: Correct this Poll command based on actual servo protocol
        poll_command = [0x04, 0x8A, 0x00, 0x00, 0x04] + [0x00] * (64 - 5)
        self.device.write(poll_command)
        # Now, read the response
        report = self.device.read(64)
        print(f"Raw HID report: {report.hex(' ')}")
        if report:
            self._parse_from_data(report)

    def write_to_HID(self):
        """
        Placeholder method to write Servo data back to a HID device.
        This is a placeholder for future implementation.
        """
        #TODO: Implement a write function to write servo data back to the device
        raise NotImplementedError("HID write support is not yet implemented. Use file-based saving for now.")


    def to_bytes(self):
        # Convert the servo's configuration into a byte array for writing
        file_data = bytearray(bytes.fromhex(self.DEFAULT_HEX_STRING.replace(" ", "")))

        # Overlay the dynamic servo data onto this base
        file_data[0x04] = self._clamp(self.angle, 1, 255)
        file_data[0x05] = self._clamp(self.angle, 1, 255) # Mirror angle

        file_data[0x06] = self._clamp(self.neutral + 128, 0, 255) # Encode neutral back to 0-255

        file_data[0x0B] = self._clamp(self.damping_factor, 50, 600)

        pwm_raw_val = int((self.pwm_power / 100.0) * 0xFFFFFF)
        pwm_raw_val = self._clamp(pwm_raw_val, 0, 0xFFFFFF)
        file_data[0x10:0x13] = pwm_raw_val.to_bytes(3, 'little')

        file_data[0x0C] = self._encode_sensitivity()

        encoded_byte_25 = self._encode_lose_ppm_protection()
        encoded_byte_25 = self._set_bit(encoded_byte_25, 1, self.inversion)
        encoded_byte_25 = self._set_bit(encoded_byte_25, 4, self.soft_start)
        encoded_byte_25 = self._set_bit(encoded_byte_25, 7, self.overload_protection)
        file_data[0x25] = encoded_byte_25
        return file_data

    def _parse_from_data(self, data: bytes):
        if len(data) < self.SVO_FILE_LENGTH:
            raise ValueError(f"Data must be at least {self.SVO_FILE_LENGTH} bytes long, but got {len(data)} bytes.")

        angle1 = data[0x04]
        angle2 = data[0x05]
        if angle1 != angle2:
            print(f"Warning: Servo angle bytes differ: 0x04={angle1}, 0x05={angle2}. Using angle from 0x04.")
        self.angle = self._clamp(angle1, 1, 255)

        raw_neutral = data[0x06]
        self.neutral = self._clamp(raw_neutral - 128, -127, 127)

        self.damping_factor = self._clamp(data[0x0B], 50, 600)

        pwm_power_bytes = data[0x10:0x13]
        pwm_raw = int.from_bytes(pwm_power_bytes, 'little')
        pwm_percent = (pwm_raw / 0xFFFFFF) * 100
        self.pwm_power = self._clamp(pwm_percent, 39.2, 100.0)

        sensitivity_byte = data[0x0C]
        self.sensitivity = self._decode_sensitivity(sensitivity_byte)

        byte_25 = data[0x25]
        self.inversion = self._get_bit(byte_25, 1)
        self.soft_start = self._get_bit(byte_25, 4)
        self.overload_protection = self._get_bit(byte_25, 7)

        lose_ppm_byte = data[0x25]
        self.lose_ppm_protection = self._decode_lose_ppm_protection(lose_ppm_byte)

    def _parse_from_file(self, file_path: str):
        try:
            with open(file_path, 'rb') as f:
                data = f.read()

            if len(data) != self.SVO_FILE_LENGTH:
                raise ValueError(f"SVO file must be exactly {self.SVO_FILE_LENGTH} bytes long, but got {len(data)} bytes.")

            angle1 = data[0x04]
            angle2 = data[0x05]
            if angle1 != angle2:
                print(f"Warning: Servo angle bytes differ: 0x04={angle1}, 0x05={angle2}. Using angle from 0x04.")
            self.angle = self._clamp(angle1, 1, 255)

            raw_neutral = data[0x06]
            self.neutral = self._clamp(raw_neutral - 128, -127, 127)

            self.damping_factor = self._clamp(data[0x0B], 50, 600)

            pwm_power_bytes = data[0x10:0x13]
            pwm_raw = int.from_bytes(pwm_power_bytes, 'little')
            pwm_percent = (pwm_raw / 0xFFFFFF) * 100
            self.pwm_power = self._clamp(pwm_percent, 39.2, 100.0)

            sensitivity_byte = data[0x0C]
            self.sensitivity = self._decode_sensitivity(sensitivity_byte)

            byte_25 = data[0x25]
            self.inversion = self._get_bit(byte_25, 1)
            self.soft_start = self._get_bit(byte_25, 4)
            self.overload_protection = self._get_bit(byte_25, 7)

            lose_ppm_byte = data[0x25]
            self.lose_ppm_protection = self._decode_lose_ppm_protection(lose_ppm_byte)

            # Levels are not parsed from file for now
            # self.level1 = self._decode_level_block(data, 0x38)
            # self.level2 = self._decode_level_block(data, 0x3C)
            # self.level3 = self._decode_level_block(data, 0x40)

        except Exception as e:
            raise IOError(f"Error parsing SVO file '{file_path}': {e}")

    def _decode_sensitivity(self, byte_value: int) -> Sensitivity:
        if byte_value == 0x10:
            return Sensitivity.ULTRA_HIGH
        elif byte_value == 0x20:
            return Sensitivity.HIGH
        elif byte_value == 0x30:
            return Sensitivity.MEDIUM
        elif byte_value == 0x40:
            return Sensitivity.LOW
        else:
            print(f"Warning: Unknown sensitivity byte value 0x{byte_value:02X}. Defaulting to MEDIUM.")
            return Sensitivity.MEDIUM
    
    def _encode_sensitivity(self) -> int:
        if self.sensitivity == Sensitivity.ULTRA_HIGH:
            return 0x10
        elif self.sensitivity == Sensitivity.HIGH:
            return 0x20
        elif self.sensitivity == Sensitivity.MEDIUM:
            return 0x30
        elif self.sensitivity == Sensitivity.LOW:
            return 0x40
        return 0x30 # Default to Medium if somehow not matched

    def _decode_lose_ppm_protection(self, byte_value: int) -> LosePPMProtection:
        if byte_value == 0x73 or byte_value == 0xE1:
            return LosePPMProtection.GO_NEUTRAL_POSITION
        elif byte_value == 0x53 or byte_value == 0xC1:
            return LosePPMProtection.KEEP_POSITION
        elif byte_value == 0x13 or byte_value == 0x81:
            return LosePPMProtection.RELEASE
        else:
            print(f"Warning: Unknown Lose PPM Protection byte value 0x{byte_value:02X}. Defaulting to RELEASE.")
            return LosePPMProtection.RELEASE

    def _encode_lose_ppm_protection(self) -> int:
        if self.lose_ppm_protection == LosePPMProtection.GO_NEUTRAL_POSITION:
            return 0xE1
        elif self.lose_ppm_protection == LosePPMProtection.KEEP_POSITION:
            return 0xC1
        elif self.lose_ppm_protection == LosePPMProtection.RELEASE:
            return 0x81
        return 0x81 # Default to Release

    @staticmethod
    def _get_bit(byte: int, bit_pos: int) -> bool:
        return (byte >> bit_pos) & 1 == 1

    @staticmethod
    def _set_bit(byte: int, bit_pos: int, value: bool) -> int:
        if value:
            return byte | (1 << bit_pos)
        else:
            return byte & ~(1 << bit_pos)

    # _decode_level_block and _encode_level_block are commented out as per request
    # def _decode_level_block(self, data: bytes, offset: int) -> Level:
    #     if len(data) < offset + 4:
    #         raise ValueError(f"File too short to read level block at offset 0x{offset:X}.")
        
    #     level_block = data[offset : offset + 4]
    #     raw_time = level_block[0] + (level_block[1] << 8)
    #     seconds = round(raw_time * 0.02, 1)
        
    #     percent_raw = level_block[2]
    #     percent = round((percent_raw / 255) * 100, 1)
        
    #     return Level(seconds, percent)
    
    # def _encode_level_block(self, level: Level) -> bytes:
    #     raw_time = int(level.seconds / 0.02)
    #     percent_raw = int((level.percentage / 100.0) * 255)
    #     raw_time = self._clamp(raw_time, 0, 0xFFFF)
    #     percent_raw = self._clamp(percent_raw, 0, 0xFF)

    #     return bytes([
    #         raw_time & 0xFF,
    #         (raw_time >> 8) & 0xFF,
    #         percent_raw,
    #         0x00 # 4th byte is usually padding or unused for levels
    #     ])

    def save_to_file(self, file_path: str):
        # Initialize the bytearray with the fixed SVO_FILE_LENGTH
        # and populate it with the default hex string content
        initial_file_data_bytes = bytes.fromhex(self.DEFAULT_HEX_STRING.replace(" ", ""))
        file_data = bytearray(initial_file_data_bytes)

        # Overlay the dynamic servo data onto this base
        file_data[0x04] = self._clamp(self.angle, 1, 255)
        file_data[0x05] = self._clamp(self.angle, 1, 255) # Mirror angle

        file_data[0x06] = self._clamp(self.neutral + 128, 0, 255) # Encode neutral back to 0-255

        file_data[0x0B] = self._clamp(self.damping_factor, 50, 600)

        pwm_raw_val = int((self.pwm_power / 100.0) * 0xFFFFFF)
        pwm_raw_val = self._clamp(pwm_raw_val, 0, 0xFFFFFF)
        file_data[0x10:0x13] = pwm_raw_val.to_bytes(3, 'little')

        file_data[0x0C] = self._encode_sensitivity()

        encoded_byte_25 = self._encode_lose_ppm_protection()
        encoded_byte_25 = self._set_bit(encoded_byte_25, 1, self.inversion)
        encoded_byte_25 = self._set_bit(encoded_byte_25, 4, self.soft_start)
        encoded_byte_25 = self._set_bit(encoded_byte_25, 7, self.overload_protection)
        file_data[0x25] = encoded_byte_25

        # Levels are not written to file for now
        # file_data[0x38:0x3C] = self._encode_level_block(self.level1)
        # file_data[0x3C:0x40] = self._encode_level_block(self.level2)
        # file_data[0x40:0x44] = self._encode_level_block(self.level3)

        try:
            output_dir = os.path.dirname(file_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            with open(file_path, 'wb') as f:
                f.write(file_data)
            print(f"Servo configuration saved to '{file_path}' successfully.")
        except Exception as e:
            raise IOError(f"Error saving SVO file to '{file_path}': {e}")

    def flash_firmware(self, firmware_path: str):
        """
        Placeholder method to flash firmware to the servo.
        This is a placeholder for future implementation.
        """
        raise NotImplementedError("Firmware flashing support is not yet implemented. Use file-based saving for now.")
    

    def __repr__(self):
        # Removed level1, level2, level3 from __repr__
        return (
            f"Servo(angle={self.angle}, neutral={self.neutral}, damping_factor={self.damping_factor}, "
            f"pwm_power={self.pwm_power:.1f}, sensitivity={self.sensitivity.value}, soft_start={self.soft_start}, "
            f"inversion={self.inversion}, lose_ppm_protection={self.lose_ppm_protection.value}, "
            f"overload_protection={self.overload_protection})"
        )
    

    
if __name__ == "__main__":
    import sys

    dummy_file_path = "servo.svo"

    print(f"Created a dummy .svo file: {dummy_file_path}")

    # Test instantiation with file
    try:
        my_servo_from_file = Servo(file_path=dummy_file_path)
        print("\nServo object instantiated from file:")
        print(my_servo_from_file)

        # You can now access its attributes
        print(f"\nIndividual attributes from file parsing:")
        print(f"Angle: {my_servo_from_file.angle}")
        print(f"Neutral: {my_servo_from_file.neutral}")
        print(f"Damping Factor: {my_servo_from_file.damping_factor}")
        print(f"PWM Power: {my_servo_from_file.pwm_power:.1f}%")
        print(f"Sensitivity: {my_servo_from_file.sensitivity.value}")
        print(f"Soft Start: {my_servo_from_file.soft_start}")
        print(f"Inversion: {my_servo_from_file.inversion}")
        print(f"Lose PPM Protection: {my_servo_from_file.lose_ppm_protection.value}")
        print(f"Overload Protection: {my_servo_from_file.overload_protection}")
        # print(f"Level 1: {my_servo_from_file.level1}")
        # print(f"Level 2: {my_servo_from_file.level2}")
        # print(f"Level 3: {my_servo_from_file.level3}")

        my_servo_from_file.angle = 150
        my_servo_from_file.neutral = 10
        my_servo_from_file.damping_factor = 200
        my_servo_from_file.save_to_file("updated_servo.svo")

    except Exception as e:
        print(f"An error occurred: {e}")
    sys.exit(0)
