from .core import Neuron, fallback_neuron
from .train import train_simple
from .bot import ChatBot
from .utils import simple_mean, tokenize

__version__ = "0.0.2.1"

def get_bug_count():
    from .core import BUG_COUNT
    return BUG_COUNT
