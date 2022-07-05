import Constants as Const
import Network as Net


class BoundBox:
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.n = min(y0, y1)
        self.s = max(y0, y1)
        self.e = max(x0, x1)
        self.w = min(x0, x1)


class Node:
    def __init__(self, parent, index):
        self.parent = parent
        self.index = index
        self.pushConnections = []
        #  self.neuron = Net.Neuron()

    @property
    def x(self):
        return self.parent.x

    @property
    def y(self):
        return self.parent.bound.n + self.index * 2 * self.parent.spacing + self.parent.spacing


class Placeable:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.name = 'Empty'
        self.color = str
        self.drawing = None  # maybe instead i say starting layer and how many layers to reduce memory usage


class Solo(Placeable):  # DEPRECIATED
    index = 0

    def __init__(self, x, y, r):
        super().__init__(x, y)
        self.name = f'Solo({Solo.index})'
        self.color = 'green'
        self.tabcolor = Const.COL_B
        self.tabOutlineCol = 'white'
        self.radius = r
        Solo.index += 1

    @property
    def bound(self):
        return BoundBox(self.x + self.radius * 1.4, self.y + self.radius * 1.4, self.x - self.radius * 1.4,
                        self.y - self.radius * 1.4)  # 1.4 accounts for grab tab


class LayerBlock(Placeable):
    index = 0

    def __init__(self, x, y, size):
        super().__init__(x, y)
        self.name = f'LayerBlock({LayerBlock.index})'
        self.pushesTo = None
        self.pullsFrom = None
        self.color = Const.COL_B
        self.outlineCol = 'white'
        self.ncolor = 'yellow'
        self.spacing = Const.NODE_RADIUS * 1.5
        self.nodes = list(Node(self, i) for i in range(size))
        LayerBlock.index += 1

    @property
    def bound(self):
        return BoundBox(self.x + self.spacing, self.y + self.spacing * self.size, self.x - self.spacing,
                        self.y - self.spacing * self.size)

    @property
    def size(self):
        return len(self.nodes)

    @size.setter
    def size(self, value):
        self.nodes = list(Node(self, i) for i in range(value))
