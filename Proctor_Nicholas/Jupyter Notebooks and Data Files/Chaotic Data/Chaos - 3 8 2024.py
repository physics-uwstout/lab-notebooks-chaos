from tabnanny import filename_only
import serial.tools.list_ports
from collections import Counter
import serial
import time
import csv
import os
import re

dev_vid = '16c0'
dev_pid = '0483'

SERIAL_PORT = find_port()

# Serial port settings 
#SERIAL_PORT = "/dev/ttyACM1" #"/dev/ttyACM0" #"COM5"  # Change this to your actual serial port 
#BAUD_RATE = 115200

class CleanResponseError(Exception):
    def __init__(self, message="Failed to generate clean response"):
        self.message = message
        super().__init__(self.message)

def find_port(self):
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if port.vid == int(dev_vid, 16) and port.pid == int(dev_pid, 16):
            print(f"Device found at {port.device}")
            return port.device
    return ''

class SerialCommunication:
    def __init__(self, port, baud_rate = 115200):
        self.port = port 
        self.baud_rate = baud_rate 
        while True:
            try: 
                self.ser = serial.Serial(self.port, self.baud_rate, timeout=1) 
                print("Connected to", self.ser.name)
                break
            except serial.SerialException as e: 
                try:
                    self.ser = serial.Serial(find_port(), self.baud_rate, timeout=1)
                    break
                except:
                    print("Error: Could not open serial port", e)
                    time.sleep(1)
                                    
    def send_command(self, command): 
        self.ser.write(command.encode())
        if not ('?' in command):
            return "received"
        
        self.ser.timeout = .15
        pattern = re.compile(r'^\d{1,4}$')
        runtime = time.time_ns()
        counter = Counter()
        
        response = ''
        while time.time_ns() - runtime < 1e9:
            try: 
                response += self.ser.read(self.ser.in_waiting).decode()    
                temp = response.replace('\r', '').split('\n')
                for value in temp:
                    if pattern.match(value):
                        counter[value] += 1
                if counter:
                    return counter.most_common(1)[0][0]
                response = temp[-1]
            except:
                continue
        raise CleanResponseError
    
        """    
        resp = response.replace('\r', '').strip().split('\n')
        resp_clean = [value for value in resp if pattern.match(value)]
        
        if len(resp_clean) <= 2:
            return resp_clean[0] if resp_clean else None

        resp_clean = resp_clean[1:-1]
        return max(set(resp_clean), key=resp_clean.count)
        
        resp = ''
        for char in response:
            if (char == '\n' or char == '\r') and resp != '':
                break
            if char.isigit() or char == '.' or char == '-':
                resp += char
        return resp """ #''.join([char for char in response if char.isdigit() or char == '.' or char == '-'])
        
    def receive_comm(self, timeout = .05):
        pattern = re.compile(r'^(\d{1,4}\s){1,2}(nan|\d{1,6}(\.\d+))$')
        runtime = time.time_ns()
        counter = Counter()        

        response = ''
        while time.time_ns() - runtime < timeout * 1e9:
            response += self.ser.read(self.ser.in_waiting).decode()   

            temp = response.replace('\r', '').split('\n')
            for value in temp:
                if pattern.match(value):
                    counter[value.split(' ')[1]] += 1
            if counter:
                return counter.most_common(1)[0][0]
            response = temp[-1]
        raise CleanResponseError
            
        """
        temp = ''
            for char in response:
                if char == '\r':
                    continue
                if char != '\n':
                    temp += char
                    continue
                if pattern.match(temp):
                    counter[temp.split(' ')[1]] += 1
                temp = ''
            
            if counter:
                return counter.most_common(1)[0][0]
            
            response = temp
            
        resp_clean = [value for value in temp if pattern.match(value)]
        if (len(resp_clean) > 0):
            for r in resp_clean:
                counter[r.split(' ')[1]] += 1 # resp_vals = [r.split(' ')[1] for r in resp_clean]
            return counter.most_common(1)[0][0] # max(set(resp_vals), key=resp_vals.count)
        if not temp:
            continue
        response = temp[-1]"""
    
    def close_connection(self): 
        self.ser.close()

def insureStop(self, ser_comm):
    last_pos = int(ser_comm.receive_comm())
    while last_pos - int(ser_comm.receive_comm()) < 10:
        last_pos = int(ser_comm.receive_comm())

def main(): 
    ser_comm = SerialCommunication(SERIAL_PORT)
    ser_comm.send_command("REPT0")
    ser_comm.close_connection
    
    ser_comm = SerialCommunication(SERIAL_PORT)
    
    commands = ["FREQ?", "AMPL?", "POSN?", "TIME?","COIL1", "REPT1"]  
    for command in commands: 
        response = ser_comm.send_command(command) 
        print(command, "->", response)
        
    FREQ_INC, AMPL_INC = 1, 50
    FREQ_BASE, AMPL_BASE = 5, 100
    FREQ_TH, AMPL_TH = 150, 1000
    
    FREQ, AMPL = FREQ_BASE, AMPL_BASE
    file_path = '/home/nprox7/Desktop/DataCollector/currTrial/'
    while True:
        ser_comm.send_command("FREQ 0")
        ser_comm.send_command("AMPL "+AMPL)
        insureStop(ser_comm)
        ser_comm.send_command("FREQ "+FREQ/100)

        file_name = time.strftime("%m-%d-%Y %H:%M", time.localtime())
        file_name += ' AMPL' + AMPL
        file_name += ' 100FREQ' + FREQ
        file_name += '.csv'
        
        with open(file_path+file_name, 'a', newline='') as file:
            writer = csv.writer(file)
            if os.path.getsize(file_path) == 0:
                writer.writerow(["time(s)", "position"])
            
            DELTA = 4096
            bound = 0
            trial_time_hr = 1
            last_pos_data = 0
            start_time = time.time_ns()
            while time.time_ns() - start_time <= trial_time_hr * 3.6e12: 
                try:
                    position_data_point = int(ser_comm.receive_comm()) #int(ser_comm.send_command('POSN?'))
                    try:
                        if abs(position_data_point + DELTA*bound - last_pos_data) > 3500:
                            bound -= (position_data_point+DELTA*bound-last_pos_data)/abs(position_data_point+DELTA*bound-last_pos_data) 
                    except: 
                        bound = bound
                    writer.writerow([(time.time_ns() - start_time)/10**9, position_data_point+DELTA*bound])
                    last_pos_data = position_data_point+DELTA*bound
                except Exception as e:
                    print(e)
                    continue
        FREQ += FREQ_INC
        if FREQ > FREQ_TH:
            FREQ = FREQ_BASE
            AMPL += AMPL_INC
        if AMPL > AMPL_TH:
            AMPL = AMPL_BASE                
    ser_comm.close_connection()
    
if __name__ == "__main__":
    main()
