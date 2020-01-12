import serial
import socket

TCP_ADDRESS = "0.0.0.0"
TCP_BUFFER_SIZE = 2**14


serial_port = serial.Serial()

serial_port.port = input("Serial port name: ")
serial_port.baudrate = int(input("Baud rate: "))
serial_port.open()

print("Opened port.")
tcp_port = int(input("Port to listen on: "))

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind((TCP_ADDRESS, tcp_port))
tcp_socket.listen()


def address_string(tuple_address):
    return tuple_address[0]+":"+str(tuple_address[1])

while True:
    print("Waiting for connection...")
    connection, addr = tcp_socket.accept()
    connection.settimeout(0.001)
    print("Connection from "+address_string(addr))

    while True:
        try:
            data = connection.recv(TCP_BUFFER_SIZE)
            if len(data) == 0:
                break
            written = serial_port.write(data)
            print(">> "+str(written)+"/"+str(len(data))+" bytes")
        except:
            pass

        if serial_port.in_waiting != 0:
            total = serial_port.in_waiting
            data = serial_port.read(serial_port.in_waiting)
            written = connection.send(data)
            print("<< "+str(written)+"/"+str(total)+" bytes")

    connection.close()
    print("Closed connection to "+address_string(addr))