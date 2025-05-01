from gui.server import ServerGUI

def main():
    server = ServerGUI("./data")
    server.run()

if __name__ == "__main__":
    main()