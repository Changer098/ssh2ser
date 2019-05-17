import server
import traceback


def __draw_commands(pty):
    # Ctrl-X is 24
    pty.send_line(pty.button("Quit - Ctrl-X"))


def __draw_devices(pty):
    # draw header
    pty.send_line("|--------------------------------------------------")
    saved_cursor = [0, 0]
    i = 0
    for device in server.Devices:
        if i is 0:
            saved_cursor[0] = pty.cursorPositionX
            saved_cursor[1] = pty.cursorPositionY
        if device.friendly_name is not None:
            pty.send_line("| {} - {} ({})".format(i, device.friendly_name,
                                                  device.device_info.get_prod_name()))
        else:
            pty.send_line("| {} - {} ({})".format(i,
                                                  device.device_int, device.device_info.get_prod_name()))
        i += 1
    pty.send_line("|--------------------------------------------------")


def mainmenu(pty):
    pty.clear()
    pty.send_line("ssh2ser - {}".format(server.ServerInfo.name))
    __draw_commands(pty)
    __draw_devices(pty)
    pty.input("Select a device: ")
    kill = False
    while not kill:
        key = pty.read_key()
        if pty.arrow(key):
            continue
        elif pty.ctrlc(key) or pty.match(key, 24):
            kill = True
        elif pty.enter(key):
            pty.newline()
        elif pty.back(key):
            pty.backspace()
        else:
            value = pty.input_key(key, only_numbers=True)
            if value is not None:
                # check
                try:
                    devNum = int(value)
                    if devNum < 0 or devNum > len(server.Devices) - 1:
                        pty.input_fail("Device selection out of range")
                    else:
                        pty.input_success()
                        pty.send_line("Opening device {}".format(server.Devices[devNum]))
                        return queue_menu(pty, devNum)
                except Exception as e:
                    print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
                    traceback.print_exc()
                    pty.input_fail("An error occurred validating input")


def queue_menu(pty, devNum):
    pty.clear()
    pty.send_line("ssh2ser - {}".format(server.ServerInfo.name))
    __draw_commands(pty)
    return


def test_interface(channel, pty):
    pty.newline()
    pty.send_line("Echo Server")
    kill = False
    while not kill:
        rawKey, key = pty.read_key()
        if key == 3:
            kill = True
        elif key == 13:
            pty.newline()
        elif key == 127:
            pty.backspace()
        elif key == 27:
            keys = [27]
            rawKey, key = pty.read_key()
            keys.append(key)
            if key == 91:
                rawKey, key = pty.read_key()
                keys.append(key)
                if key == 65:
                    pty.up()
                elif key == 66:
                    pty.down()
                elif key == 67:
                    # print("RIGHT")
                    pty.right()
                elif key == 68:
                    # print("LEFT")
                    pty.left()
                else:
                    pty.send("".join(chr(key) for key in keys))
            else:
                pty.send("".join(chr(key) for key in keys))
        # up: [27, 91, 65], down: [27, 91. 66], left: [27, 91, 68], right: [27, 91, 67]
        else:
            pty.send(rawKey)
    pty.close()
