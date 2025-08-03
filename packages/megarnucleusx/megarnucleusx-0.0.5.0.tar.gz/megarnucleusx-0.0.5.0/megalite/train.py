from .core import Neuron

def train_simple(iterations=100):
    n = Neuron(weights=[0.5])
    for i in range(iterations):
        try:
            n.weights[0] += 0.01 * (1 - 0.001 * i)  # leve reducción por iteración
        except Exception:
            pass
    return n
