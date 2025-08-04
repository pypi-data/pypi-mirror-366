import serial
import serial.tools.list_ports
import time

class ElectroBlocks:

    last_sense_data = ""

    def __init__(self, baudrate=115200, timeout=2):
        self.ser = self._auto_connect(baudrate, timeout)
        self._wait_for_ready()
    
    def _auto_connect(self, baudrate, timeout):
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if (p.vid == 9025 and p.pid in (67, 16)) or (p.vid == 6790): # Arduino Uno or Mega and Indian Arduino UNO
                try:
                    ser = serial.Serial(p.device, baudrate, timeout=timeout)
                    time.sleep(2)  # Give Arduino time to reset
                    return ser
                except serial.SerialException as e:
                    print(f"Failed to connect to {e}. Trying next port...")
                    continue
        raise Exception("No Arduino Uno or Mega found.")

    def _wait_for_message(self, message):
        while True:
            if self.ser.in_waiting:
                line = self.ser.readline().decode("utf-8", errors="ignore").strip()
                if message in line:
                    return line

    def _get_sensor_str(self):
        self._send("sense")
        message = self._wait_for_message("SENSE_COMPLETE")
        message = message.replace("SENSE_COMPLETE", "")
        sensorsStr = message.split(";")
        return sensorsStr
    
    # return the result of pin read that is being sensed
    def _find_sensor_str(self, sensorPin, sensorType):
        sensorsStr = self._get_sensor_str()
        for sensor in sensorsStr:
            if len(sensor) == 0:
                continue
            [type, pin, result] = sensor.split(":")
            if (type == sensorType and pin == str(sensorPin)):
                return result

        return ""

    def _wait_for_ready(self):
        self.ser.write(b"IAM_READY|")
        self._wait_for_message("System:READY")

    def _send(self, cmd):
        self.ser.write((cmd + "|\n").encode())
        self._wait_for_message("DONE_NEXT_COMMAND")

    # Digital Write Method
    def config_digital_read(self, pin):
        self._send(f"config:b={pin}")

    def digital_read(self, pin):
        return self._find_sensor_str(pin, "dr") == "1"

    # Button Methods
    def config_button(self, pin):
        self._send(f"config:b={pin}")

    def is_button_pressed(self, pin):
        return self._find_sensor_str(pin, "b") == "0"

    # Servo Methods
    def config_servo(self, pin):
        self._send(f"config:servo={pin}")

    def move_servo(self, pin, angle):
        self._send(f"s:{pin}:{angle}")

    # RGB Methods
    def config_rgb(self, r_pin, g_pin, b_pin):
        self._send(f"config:rgb={r_pin},{g_pin},{b_pin}")

    def set_rgb(self, r, g, b):
        self._send(f"rgb:{r},{g},{b}")

    # LCD Methods
    def config_lcd(self, rows=2, cols=16):
        self._send(f"config:lcd={rows},{cols}")

    def lcd_print(self, row, col, message):
        self._send(f"l:{row}:{col}:{message}")

    def lcd_clear(self):
        self._send("l:clear")

    def lcd_toggle_backlight(self, on):
        if on:
            self._send("l:backlighton")
        else:
            self._send("l:backlightoff")

    def lcd_blink_curor(self, row, col, on):
        if on == True:
            self._send(f"l:cursor_on:{row}:{col}")
        else:
            self._send(f"l:cursor_off:{row}:{col}")

    def lcd_scrollright(self):
        self._send("l:scroll_right")

    def lcd_scrollleft(self):
        self._send("l:scroll_left")

    # LED Methods
    def digital_write(self, pin, value):
        self._send(f"dw:{pin}:{value}")

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()