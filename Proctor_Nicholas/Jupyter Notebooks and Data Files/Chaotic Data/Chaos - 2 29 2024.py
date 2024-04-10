import serial
import time
import csv
import os
import re

# Serial port settings 
SERIAL_PORT = "/dev/ttyACM0" #"COM5"  # Change this to your actual serial port 
BAUD_RATE = 115200

class SerialCommunication:
    def __init__(self, port, baud_rate):
        self.port = port 
        self.baud_rate = baud_rate 
        while True:
            try: 
                self.ser = serial.Serial(self.port, self.baud_rate, timeout=1) 
                print("Connected to", self.ser.name)
                break
            except serial.SerialException as e: 
                print("Error: Could not open serial port", e)
                time.sleep(1)
 
    def send_command(self, command): 
        self.ser.write(command.encode()) 
        if not ('?' in command):
            return "recieved"
        self.ser.timeout = .1
        response = ''
        while True:
            try: 
                response += self.ser.read(self.ser.in_waiting).decode()    
                if ('\n' in response or '\r' in response) and response != '':
                    break
            except ValueError: 
                print(f"Error: Unable to convert response to float for command {command}")
            except:
                continue
            
        pattern = re.compile(r'^\d{1,4}$')
        resp = response.replace('\r', '').strip().split('\n')
        resp_clean = [value for value in resp if pattern.match(value)]
        
        if len(resp_clean) <= 2:
            return resp_clean[0] if resp_clean else None

        resp_clean = resp_clean[1:-1]
        return max(set(resp_clean), key=resp_clean.count)
        
        """
        resp = ''
        for char in response:
            if (char == '\n' or char == '\r') and resp != '':
                break
            if char.isigit() or char == '.' or char == '-':
                resp += char
        return resp """ #''.join([char for char in response if char.isdigit() or char == '.' or char == '-'])
    def close_connection(self): 
        self.ser.close()

def main(): 
    ser_comm = SerialCommunication(SERIAL_PORT, BAUD_RATE)
    ser_comm.close_connection
    ser_comm = SerialCommunication(SERIAL_PORT, BAUD_RATE)
    
    commands = ["FREQ?", "AMPL?", "POSN?", "TIME?","FREQ .79","AMPL 216","COIL1"]  
    for command in commands: 
        response = ser_comm.send_command(command) 
        print(command, "->", response)
    
    file_name = 'data.csv'
    file_path = '/home/nprox7/Desktop/DataCollector/currTrial/' + file_name
    
    # Check if the file exists, create it if it doesn't
    if not os.path.isfile(file_path):
            file = open(file_path, 'w', newline='')
            writer = csv.writer(file)
            writer.writerow(["time(s)", "position"])
    else:
            file = open(file_path, 'a', newline='')
            writer = csv.writer(file)  # Append only data, excluding header

    bound = 0
    last_pos_data = 0
    start_time = time.time_ns()
    while True: 
        try:
            position_data_point = int(ser_comm.send_command('POSN?'))
            try:
                if abs(position_data_point + bound - last_pos_data) > 3500:
                    bound -= 4000*(position_data_point+bound-last_pos_data)/abs(position_data_point+bound-last_pos_data) 
            except: 
                bound = bound
            writer.writerow([(time.time_ns() - start_time)/10**9, position_data_point+bound])
            last_pos_data = position_data_point+bound
        except Exception as e:
            print(e)
            continue
        
    ser_comm.close_connection()
    
if __name__ == "__main__":
    main()
