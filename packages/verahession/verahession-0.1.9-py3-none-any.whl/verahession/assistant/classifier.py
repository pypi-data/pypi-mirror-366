import torch
from .model import NeuralNet
from .utils import tokenize, stem, bag_of_words

class Classifier:
    def __init__(self, model_path):
        data = torch.load(model_path)

        self.all_words = data["all_words"]
        self.tags = data["tags"]
        input_size = data["input_size"]
        hidden_size = data["hidden_size"]
        output_size = data["output_size"]

        self.model = NeuralNet(input_size, hidden_size, output_size)
        self.model.load_state_dict(data["model_state"])
        self.model.eval()

    def classify(self, sentence):
        tokens = tokenize(sentence)
        bag = bag_of_words(tokens, self.all_words)
        bag = torch.from_numpy(bag).float().unsqueeze(0)  # Shape: (1, input_size)

        with torch.no_grad():
            output = self.model(bag)
            probs = torch.softmax(output, dim=1)
            confidence, pred_idx = torch.max(probs, dim=1)
            intent_tag = self.tags[pred_idx.item()]
            return intent_tag, confidence.item()
