import numpy as np


class Layer:
    def __init__(self):
        self.input = []
        self.output = []
        self.weights = []  # out x in
        self.bias = []  # one per out
