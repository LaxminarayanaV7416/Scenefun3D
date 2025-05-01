from gui.server import ServerGUI

def main():
    server = ServerGUI("./data", "420673", "42445198")
    server.run()

if __name__ == "__main__":
    main()