import time
import serial
import serial.tools.list_ports
import os
import threading
import queue


ser = None
serial_lock = threading.Lock()
serial_command_queue = queue.Queue()
serial_worker_running = False
status_thread = None
status_thread_running = False

CMD_REPLY_MAP = {
    0x10: 0x80,  # MOVE_REQ         -> MOVE_REP
    0x11: 0x81,  # LIGHT_REQ        -> LIGHT_REP
    0x12: 0x82,  # PLAY_SOUND_REQ   -> PLAY_SOUND_REP
    0x13: 0x83,  # MOVE_STOP_REQ    -> MOVE_STOP_REP
    0x14: 0x84,  # LIGHT_STOP_REQ   -> LIGHT_STOP_REP
    0x15: 0x85,  # SOUND_STOP_REQ   -> SOUND_STOP_REP 
    0x16: 0x86,  # LIGHT12_REQ      -> LIGHT12_REP (not implemented yet)
    0x17: 0x87,  # WAIT_SENSOR_REQ  -> WAIT_SENSOR_REP
    0x18: 0x88,  # GET_SENSOR_REQ   -> GET_SENSOR_REP
    0x19: 0x89,  # GET_STATUS_REQ   -> GET_STATUS_REP
}

class SerialCommand:
    def __init__(self, cmd, payload, expect_reply=True):
        self.cmd = cmd
        self.payload = payload
        self.expect_reply = expect_reply
        self.response = None
        self.done = threading.Event()

def start_serial_worker():
    global serial_worker_running
    if not serial_worker_running:
        serial_worker_running = True
        threading.Thread(target=serial_worker_loop, daemon=True).start()

def serial_worker_loop():
    global ser
    while serial_worker_running:
        try:
            command = serial_command_queue.get(timeout=0.1)
        except queue.Empty:
            continue
        with serial_lock:
            result = send_packet(
                command.cmd,
                command.payload,
                wait_done=True,
                verbose=True
            )
            command.response = result
            command.done.set()

def stop_status_monitor():
    global status_thread_running
    status_thread_running = False
    print("Status monitor stopped.")

class DeviceStatus:
    def __init__(self):
        # Motors
        self.motor1 = False 
        self.motor2 = False 
        self.motor3 = False 

        # LEDs
        self.led1 = False
        self.led2 = False

        # Sound
        self.sound = False

        # Sensors (state and values)
        self.sensor1 = False
        self.sensor2 = False
        self.sensor1_value = 0.0
        self.sensor2_value = 0.0


g_algopython_system_status = DeviceStatus()

def serial_thread_task():
    last_status_time = time.time()
    while True:
        # Check if it's time to fetch the brain status (every 10ms)
        now = time.time()

        # if (now - last_status_time) >= 1:  # 10ms = 0.01 seconds
        if (now - last_status_time) >= 0.05:  # 10ms = 0.01 seconds
            serial_get_brain_status()
            last_status_time = now

        # Process queued commands (non-blocking)
        try:
            command = serial_command_queue.get_nowait()
            serial_send_next_command(command)
        except queue.Empty:
            pass

        # Short sleep to avoid busy-loop hogging CPU
        time.sleep(0.001)  # 1ms pause


def serial_thread_start():
    threading.Thread(target=serial_thread_task, daemon=True).start()

def serial_send_next_command(command):
    result = send_packet(
            command.cmd,
            command.payload,
            wait_done=command.expect_reply,
            verbose=True
            )
    command.response = result
    command.done.set()

def serial_get_brain_status():
    global g_algopython_system_status
    response = serial_send_command(0x19, b"", expect_reply=True)

    if not response or len(response) < 10:
        return "?, ?, ?, ?, ?, ?, ?, ?, ?, ?"

    g_algopython_system_status.motor1 = response[0]
    g_algopython_system_status.motor2 = response[1]
    g_algopython_system_status.motor3 = response[2]
    g_algopython_system_status.led1 = bool(response[3])
    g_algopython_system_status.led2 = bool(response[4])
    g_algopython_system_status.sound = bool(response[5])
    g_algopython_system_status.sensor1 = bool(response[6])
    g_algopython_system_status.sensor2 = bool(response[7])
    g_algopython_system_status.sensor1_value = response[8]
    g_algopython_system_status.sensor2_value = response[9]

    s = g_algopython_system_status
    print(
        f"Motors: {s.motor1}, {s.motor2}, {s.motor3} | "
        f"LEDs: {int(s.led1)}, {int(s.led2)} | "
        f"Sound: {int(s.sound)} | "
        f"Sensors: Trig1={int(s.sensor1)}, Trig2={int(s.sensor2)}, "
        f"Value1={s.sensor1_value}, Value2={s.sensor2_value}"
    )
def serial_queue_command(cmd, payload, expect_reply=True):
    command = SerialCommand(cmd, payload, expect_reply)
    serial_command_queue.put(command)
    command.done.wait()
    return command.response

def serial_send_command(cmd, payload, expect_reply=True):
    command = SerialCommand(cmd, payload, expect_reply)
    serial_tx_command(command)
    command.done.wait()
    return command.response

def serial_tx_command(command):
    result = send_packet(
            command.cmd,
            command.payload,
            wait_done=command.expect_reply,
            verbose=True
            )
    command.response = result
    command.done.set()

def serial_send_next_command(command):
    result = send_packet(
            command.cmd,
            command.payload,
            wait_done=command.expect_reply,
            verbose=True
            )
    command.response = result
    command.done.set()


def algopython_init(port: str = None):
    time.sleep(2) # Allow time for the system to start up and establish the serial connection
    os.system('cls' if os.name == 'nt' else 'clear')
    global ser
    if not port:
        port = find_usb_serial_port()
        if not port:
            print("USB port not found. Please connect the device and try again.")
            return False
    try:
        ser = serial.Serial(
            port=port,
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.5
        )
        print(f"Serial port: {port}")
        serial_thread_start();
        time.sleep(2)
        return True
    except serial.SerialException as e:
        print(f"\nError when opening port: {port}: {e}\n")
        return False

def find_usb_serial_port():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if "USB" in p.description or "CP210" in p.description or "ttyUSB" in p.device:
            return p.device
    return None

def build_packet(cmd: int, payload: bytes) -> bytes:
    if not isinstance(payload, (bytes, bytearray)):
        payload = bytes(payload)
    header = bytes([0xA5, cmd, len(payload)])
    crc = sum(header) % 256
    return header + payload + bytes([crc])

def send_packet(cmd, payload, wait_done=True, delay_after=0.01, retries=2, verbose=True):
    global ser
    if ser is None:
        print("[Error] Serial port is not initialized.")
        return None

    packet = build_packet(cmd, payload)
    expected_reply_cmd = CMD_REPLY_MAP.get(cmd)
    # print(f"Sending packet: {packet.hex()} (CMD: 0x{cmd:02X}, Expected Reply: 0x{expected_reply_cmd:02X})")
    for attempt in range(retries + 1):
        with serial_lock:
            ser.reset_input_buffer()
            # if verbose:
            #     print(f"\n[Try {attempt + 1}] Sending packet: " + ' '.join(f'{b:02X}' for b in packet))
            ser.write(packet)
            time.sleep(delay_after)
            # if wait_done:
            if True:
                reply = wait_for_reply(expected_reply_cmd)
                if reply is not None:
                    return reply
            else:
                return True
    if verbose:
        print(f"[Fail] No reply for CMD 0x{cmd:02X} after {retries + 1} tries.")
    return None

def wait_for_reply(expected_cmd, timeout=1):
    global ser
    start = time.time()
    buffer = bytearray()
    #print(f"Waiting for reply for CMD 0x{expected_cmd:02X}...")
    while time.time() - start < timeout:
        if ser.in_waiting:
            # print("Serianl in waiting: ", ser.in_waiting);
            buffer.extend(ser.read(ser.in_waiting))
        while len(buffer) >= 4:
            # print("Buffer length: ", len(buffer))
            # print("Buffer content: ", buffer.hex())
            if buffer[0] == 0xA5:
                cmd, size = buffer[1], buffer[2]
                total_length = 3 + size + 1
                if len(buffer) >= total_length:
                    crc = buffer[3 + size]
                    #print("CRC: ", crc, "Expected: ", (sum(buffer[:total_length - 1])&0xff) )
                    if cmd == expected_cmd and crc == sum(buffer[:total_length - 1])&0xff:
                        return buffer[3:3+size]
                    buffer = buffer[1:]
                else:
                    break
            else:
                buffer = buffer[1:]
        time.sleep(0.005)
    return None

# You can import send_command from this file into algopython_cmd.py and replace all uses of send_packet.
