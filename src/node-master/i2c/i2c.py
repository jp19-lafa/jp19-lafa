import smbus
import time

bus = smbus.SMBus(1) # RPI used i2C bus 1

# This is the address we setup in the atmega Program 
address = 10

def readNumber():
    return bus.read_i2c_block_data(address, 2)

# Read a message from the atmega, this message is maximum 20 bytes long
def readMessageFromArduino():
    data = bus.read_i2c_block_data(address, 0,20)
    Message = ""
    data2 = []
    for i in range(len(data)):
        if(data[i] != 255):
            data2.append(data[i])

    for i in range(len(data2)):
        if(data2[i] != b'\xc3' or data2[i] != b'\xbf' ):
            Message += chr(data2[i])

    print(Message.encode('utf-8'))

def start(name):
    print("In I2C Thread" + name)
    while True:
        readMessageFromArduino()
        time.sleep(0.5)

# send datat to attiny (light)
# bus.write_i2c_block_data(0,ord('2'),[ord("5"),ord('5')])
if __name__ == "__main__":
    start("i2C")