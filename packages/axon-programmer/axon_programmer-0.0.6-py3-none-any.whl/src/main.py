import hid
import time

from src.gui import main as gui_main

# Vendor ID and Product ID for Axon servo adapter
VENDOR_ID = 0x0471
PRODUCT_ID = 0x13aa

# Command to poll the servo adapter
poll_command = [0x04, 0x8A, 0x00, 0x00, 0x04] + [0x00] * (64 - 5)

def parse_servo_report(data):
    """
    Parse the 64-byte HID report from the servo adapter into meaningful parameters.
    Assumes `data` is a list or bytes of length 64.
    """
    #TODO: Write reading from device to get servo data
    raise NotImplementedError("Parse function not implemented yet.")

def is_servo_present(report):
    """
    Determine if the servo is plugged in based on parsed data.
    For example, check if servo angle and PWM power are in valid ranges.
    """
    return (
        len(report) >= 6 and
        report[0] == 0x04 and
        report[1] == 0x01 and
        report[2] == 0x00 and
        report[3] == 0x01 and
        report[5] == 0x03
    )

def main():
    gui_main()
    # device = None
    # adapter_connected = False
    # last_servo_status = None
    # last_parsed = None  # Track last parsed message

    # print("Starting servo adapter monitoring... (Press Ctrl+C to stop)")

    # while True:
    #     if not adapter_connected:
    #         print("Searching for servo adapter...")
    #         while not adapter_connected:
    #             try:
    #                 device = hid.device()
    #                 device.open(VENDOR_ID, PRODUCT_ID)
    #                 device.set_nonblocking(True)
    #                 adapter_connected = True
    #                 print("✅ Adapter connected.")
    #                 last_servo_status = None
    #                 last_parsed = None
    #             except (IOError, OSError) as e:
    #                 print(f"Adapter not found or accessible: {e}. Retrying in 2 seconds...")
    #                 time.sleep(2)
    #             except Exception as e:
    #                 print(f"Unexpected error opening device: {e}. Retrying in 2 seconds...")
    #                 time.sleep(2)

    #     if adapter_connected:
    #         try:
    #             device.write(poll_command)
    #             time.sleep(0.05)

    #             report = device.read(64)

    #             if report:

    #                 if is_servo_present(report):
    #                     if last_servo_status != "plugged":
    #                         print("✅ Servo is PLUGGED in")
    #                         last_servo_status = "plugged"
    #                 else:
    #                     if last_servo_status != "not_plugged":
    #                         print("❌ Servo is NOT plugged in")
    #                         last_servo_status = "not_plugged"

    #                 # if parsed and parsed != last_parsed:
    #                 #     print("--- Servo Status ---")
    #                 #     last_parsed = parsed

    #             time.sleep(0.4)

    #         except (IOError, OSError) as e:
    #             print(f"❌ Adapter disconnected: {e}")
    #             if device:
    #                 device.close()
    #             adapter_connected = False
    #             device = None
    #             last_servo_status = None
    #             last_parsed = None
    #             time.sleep(1)
    #         except Exception as e:
    #             print(f"Unexpected error during polling: {e}")
    #             if device:
    #                 device.close()
    #             adapter_connected = False
    #             device = None
    #             last_servo_status = None
    #             last_parsed = None
    #             time.sleep(1)

if __name__ == "__main__":
    import sys
    if '--gui' in sys.argv:
        from gui import main as gui_main
        gui_main()
    else:
        main()
