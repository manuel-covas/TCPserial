import serial
import socket

TCP_ADDRESS = "0.0.0.0"
TCP_BUFFER_SIZE = 2**6


serial_port = serial.Serial()

serial_port.port = input("Serial port name: ")
serial_port.baudrate = int(input("Baud rate: "))
serial_port.open()

print("Opened port.")
tcp_port = int(input("Port to listen on: "))

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind((TCP_ADDRESS, tcp_port))
tcp_socket.listen()


while True:
    print("Waiting for connection...")
    connection, addr = tcp_socket.accept()
    connection.settimeout(0.010)
    print("Connection from "+"".join(tuple(map(str, addr))))

    while True:
        try:
            data = connection.recv(TCP_BUFFER_SIZE)
            written = serial_port.write(data)
            print(">> "+str(written)+" bytes")
        except:
            pass

        if serial_port.in_waiting != 0:
            data = serial_port.read(serial_port.in_waiting)
            written = connection.send(data)
            print("<< "+str(written)+" bytes")

    connection.close()
    print("Closed connection to "+"".join(tuple(map(str, addr))))