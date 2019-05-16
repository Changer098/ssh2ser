import server
import serial

if __name__ == "__main__":
    server.Devices = serial.find_devices()
    server.ServerInfo = server.Info("Test Server", banner="Bannery banner")
    server = server.Server(2200, "test2", "test2")
    server.run()
