class ChatBot:
    def __init__(self, name="MegaBot"):
        self.name = name
        self.memory = []

    def learn(self, input_text):
        self.memory.append(input_text)

    def respond(self, input_text):
        if input_text in self.memory:
            return f"{self.name}: Ya lo recuerdo. ¿Algo nuevo?"
        self.learn(input_text)
        return f"{self.name}: Hmm, cuéntame más..."
