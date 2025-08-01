import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from .utils import tokenize, stem, bag_of_words
from .model import NeuralNet

class ChatDataset(Dataset):
    def __init__(self, X_data, y_data):
        self.n_samples = len(X_data)
        self.x_data = X_data
        self.y_data = y_data

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    def __len__(self):
        return self.n_samples

class trainer:
    def __init__(self, INTENTS_PATH, MODEL_SAVE):
        self.INTENTS_PATH = INTENTS_PATH
        self.MODEL_FILE = MODEL_SAVE

    def train(self):
        with open(self.INTENTS_PATH, 'r') as f:
            intents = json.load(f)

        all_words = []
        tags = []
        xy = []

        for intent in intents['intents']:
            tag = intent['tag']
            tags.append(tag)
            for pattern in intent['patterns']:
                w = tokenize(pattern)
                all_words.extend(w)
                xy.append((w, tag))

        ignore_words = ['?', '.', '!', ',']
        all_words = [stem(w) for w in all_words if w not in ignore_words]
        all_words = sorted(set(all_words))
        tags = sorted(set(tags))

        X_train = []
        y_train = []

        for (pattern_sentence, tag) in xy:
            bag = bag_of_words(pattern_sentence, all_words)
            X_train.append(bag)
            y_train.append(tags.index(tag))

        X_train = np.array(X_train)
        y_train = np.array(y_train)

        batch_size = 8
        hidden_size = 8
        output_size = len(tags)
        input_size = len(all_words)
        learning_rate = 0.001

        num_patterns = sum(len(intent['patterns']) for intent in intents['intents'])
        complexity_factor = len(tags) * len(all_words)
        num_epochs = min(1500, max(300, int((num_patterns * 10) + (complexity_factor / 3))))

        dataset = ChatDataset(X_train, y_train)
        train_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True)

        model = NeuralNet(input_size, hidden_size, output_size)

        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

        for epoch in range(num_epochs):
            for (words, labels) in train_loader:
                words = words.float()
                labels = labels.long()

                outputs = model(words)
                loss = criterion(outputs, labels)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            if (epoch+1) % 100 == 0 or epoch == num_epochs - 1:
                print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

        data = {
            "model_state": model.state_dict(),
            "input_size": input_size,
            "hidden_size": hidden_size,
            "output_size": output_size,
            "all_words": all_words,
            "tags": tags,
            "responses": {intent['tag']: intent.get('responses', []) for intent in intents['intents']},
            "commands": {intent['tag']: intent.get('command', None) for intent in intents['intents']},
        }
        torch.save(data, self.MODEL_FILE)
        
        print(f"Model trained and saved to {self.MODEL_FILE}")
