import serial
from serial import Serial
import socket

TCP_ADDRESS = "0.0.0.0"
TCP_BUFFER_SIZE = 2**14
ESP_IDF_BAUD_CHANGE_PACKET_HEADER = str.encode("\x00\x0f\x08\x00\x00\x00\x00\x00")

chosen_port = input("Serial port name: ")
chosen_baudrate = int(input("Baud rate: "))

serial_port = serial.Serial()
serial_port.port = chosen_port
serial_port.baudrate = chosen_baudrate
serial_port.open()

print("Opened port.")

tcp_port = int(input("Port to listen on: "))

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind((TCP_ADDRESS, tcp_port))
tcp_socket.listen()


pending_baud_change = {
    "new": 0,
    "old": 0
}


def address_string(tuple_address):
    return tuple_address[0]+":"+str(tuple_address[1])


def check_esp_idf_baud_change(data):
    header_index = data.find(ESP_IDF_BAUD_CHANGE_PACKET_HEADER)
    if (header_index != -1):
        print("Baud change command found in message of len="+str(len(data)))
        bauds_index = header_index + len(ESP_IDF_BAUD_CHANGE_PACKET_HEADER)
        new_baud = int.from_bytes(data[bauds_index : bauds_index + 4], "little")
        old_baud = int.from_bytes(data[bauds_index + 4 : bauds_index + 8], "little")

        print("Detected esp-idf changing baud rate from "+str(old_baud)+" to "+str(new_baud)+". Waiting for response to apply...")
        pending_baud_change["old"] = old_baud
        pending_baud_change["new"] = new_baud


def check_pending_baud_change():
    global pending_baud_change
    global serial_port
    if (pending_baud_change["new"] != 0):
        print("Applying baud change from "+str(pending_baud_change["old"])+" to "+str(pending_baud_change["new"])+".")
        serial_port.baudrate = pending_baud_change["new"]
        print("Applied.")
        pending_baud_change["old"] = 0
        pending_baud_change["new"] = 0


while True:
    print("Waiting for connection...")
    connection, addr = tcp_socket.accept()
    connection.settimeout(0.0005)
    print("Connection from "+address_string(addr))
    print("Setting port baud rate to initial value. ("+str(chosen_baudrate)+")")
    serial_port.baudrate = chosen_baudrate

    while True:
        try:
            data = connection.recv(TCP_BUFFER_SIZE)
            if len(data) == 0:
                break
            
            written = serial_port.write(data)
            print(">> "+str(written)+"/"+str(len(data))+" bytes")
            check_esp_idf_baud_change(data)

        except Exception as e:
            pass

        if serial_port.in_waiting != 0:
            total = serial_port.in_waiting
            data = serial_port.read(serial_port.in_waiting)
            check_pending_baud_change()
            written = connection.send(data)
            print("<< "+str(written)+"/"+str(total)+" bytes")

    connection.close()
    print("Closed connection to "+address_string(addr))