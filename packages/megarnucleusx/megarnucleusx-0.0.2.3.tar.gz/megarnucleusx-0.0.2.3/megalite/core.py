BUG_COUNT = 0

class Neuron:
    def __init__(self, weights=None):
        self.weights = weights or [1.0]

    def think(self, x):
        global BUG_COUNT
        try:
            return sum([w * x for w in self.weights])
        except Exception as e:
            BUG_COUNT += 1
            print(f"[AntiBug] ⚠️ Error detectado en Neuron: {e}")
            return 0

def fallback_neuron():
    return Neuron(weights=[0.05])
