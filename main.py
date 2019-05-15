import server

if __name__ == "__main__":
    server = server.Server(2200, "test2", "test2")
    server.run()
