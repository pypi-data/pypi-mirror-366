# Verahession

**Verahession** is an intelligent conversational interface built for AI agents, supporting message sending, rewriting, and local intent classification.

---

## 🔧 Features

- 🧠 Send and receive messages using an API-based LLM
- ✍️ Rewrite user input intelligently
- 🏋️‍♂️ Train a local intent classification model
- 🔍 Detect user intent with confidence scoring

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/verahession.git
cd verahession
pip install -r requirements.txt
```

---

## 🔑 API Key

To use the Vera API (LLM), you need an API key.  
Visit [hessiondynamics.com](https://hessiondynamics.com) to request your key.

---

## 🚀 Example Usage

```python
from verahession.api import vera_interface
from verahession.assistant import *

# Initialize Vera interface
vera = vera_interface(API_KEY="your_api_key_here", AGENT_NAME="Brian", USER_NAME="Jack")

# Send a message
message = input("You: ")
result = vera.send(message)
print("Vera says:", result.get("response", result))

# Rewrite a message
message = input("Text: ")
result = vera.rewrite(message)
print("Vera rewrites:", result.get("response", result))

# Train the intent classifier
bot_trainer = trainer("./intents.json", "./model.pth")
bot_trainer.train()

# Classify a new input
classifier = Classifier("./model.pth")
message = input("You: ")
intent, confidence = classifier.classify(message)
print(intent)
print(confidence)
```

---

## 📁 File Structure

- `verahession/api.py` – Vera API interface (LLM)
- `verahession/assistant.py` – Local trainer & classifier tools
- `intents.json` – Training data for intent classification
- `model.pth` – Output model file after training

---

## 📄 License

MIT License

---
