from .nohe import Operations

class ClientPacket:
    maxSize = 1 + 4*2 + 1024*2
    def __init__(self, operation=None, X=None, Y=None):
        self.op = Operations[operation].value if operation else None
        self.X = X
        self.Y = Y

    def to_bytes(self):
        op = self.op.to_bytes(1, byteorder='big')
        X = bytes(self.X)
        Y = bytes(self.Y)
        sizeX = len(self.X).to_bytes(4, byteorder='big')
        sizeY = len(self.X).to_bytes(4, byteorder='big')
        return op + sizeX + sizeY + X + Y

    def from_bytes(self, data):
        cnt = 0
        op = int.from_bytes(data[cnt:cnt+1], byteorder='big'); cnt += 1
        operation = Operations(op).name

        sizeX = int.from_bytes(data[cnt:cnt+4], byteorder='big'); cnt += 4
        sizeY = int.from_bytes(data[cnt:cnt+4], byteorder='big'); cnt += 4

        X = data[cnt:cnt+sizeX]; cnt += sizeX
        Y = data[cnt:cnt+sizeY]; cnt += sizeY
        return operation, X, Y

class ServerPacket:
    maxSize = 4*2 + 1024*2
    def __init__(self, X=None, Y=None):
        self.X = X
        self.Y = Y

    def to_bytes(self):
        X = bytes(self.X)
        Y = bytes(self.Y)
        sizeX = len(self.X).to_bytes(4, byteorder='big')
        sizeY = len(self.X).to_bytes(4, byteorder='big')
        return sizeX + sizeY + X + Y

    def from_bytes(self, data):
        cnt = 0
        sizeX = int.from_bytes(data[cnt:cnt+4], byteorder='big'); cnt += 4
        sizeY = int.from_bytes(data[cnt:cnt+4], byteorder='big'); cnt += 4

        X = data[cnt:cnt+sizeX]; cnt += sizeX
        Y = data[cnt:cnt+sizeY]; cnt += sizeY
        return X, Y