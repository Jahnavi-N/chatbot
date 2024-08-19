import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import requests
import json
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

# Load model and data
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Sam"

def respond():
    sentence = user_input.get()
    if sentence.lower() == "quit":
        root.quit()

    user_input.delete(0, tk.END)
    
    sentence = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                bot_response = random.choice(intent['responses'])
                break
    else:
        bot_response = "I do not understand..."
    
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, f"You: {sentence}\n{bot_name}: {bot_response}\n\n")
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)

    if tag == 'service_inquiry':
        handle_service_inquiry()
    elif tag == 'faq':
        handle_faq()

def handle_service_inquiry():
    service = simpledialog.askstring("Service Inquiry", "What type of service are you looking for? (e.g., landscaping, plumbing)")
    name = simpledialog.askstring("Contact Details", "Please provide your name:")
    email = simpledialog.askstring("Contact Details", "Please provide your email:")
    phone = simpledialog.askstring("Contact Details", "Please provide your phone number:")
    action = simpledialog.askstring("Action Selection", "Would you like to fill in a form, call a contractor, or set an appointment? (form/call/appointment)")

    data = {
        "name": name,
        "email": email,
        "phone": phone,
        "service": service,
        "action": action
    }

    response = requests.post('http://127.0.0.1:5000/submit', json=data)
    bot_response = response.json().get('message', "There was an issue saving your details.")
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, f"{bot_name}: {bot_response}\n\n")
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)

def handle_faq():
    question = simpledialog.askstring("FAQ", "Please enter your question:")
    response = requests.get(f'http://127.0.0.1:5000/faq', params={'question': question})
    answer = response.json().get('answer', "I couldn't find an answer to your question.")
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, f"{bot_name}: {answer}\n\n")
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)

def display_service_options():
    response = requests.get('http://127.0.0.1:5000/service-options')
    options = response.json().get('options', [])
    if options:
        message = "Available service options:\n"
        for option in options:
            message += f"Service: {option['name']}, Contact: {option['contact']}\n"
        messagebox.showinfo("Service Options", message)
    else:
        messagebox.showinfo("Service Options", "No service options available.")

def display_welcome_message():
    welcome_message = (
        "Welcome to the Home Improvement Chatbot!\n\n"
        "I'm Sam, here to assist you with connecting to top-rated contractors.\n"
        "You can inquire about services, fill out a form, call a contractor, or set an appointment.\n"
        "How can I assist you today?"
    )
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, f"{bot_name}: {welcome_message}\n\n")
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)

# Create main window
root = tk.Tk()
root.title("Chatbot")

# Create chat area
chat_area = scrolledtext.ScrolledText(root, state=tk.DISABLED, wrap=tk.WORD, height=20, width=50)
chat_area.pack(padx=10, pady=10)

# Create user input field
user_input = tk.Entry(root, width=50)
user_input.pack(padx=10, pady=5)

# Create send button
send_button = tk.Button(root, text="Send", command=respond)
send_button.pack(padx=10, pady=5)

# Create service options button
service_button = tk.Button(root, text="Show Service Options", command=display_service_options)
service_button.pack(padx=10, pady=5)

# Bind Enter key to send button
root.bind('<Return>', lambda event: respond())

# Display the welcome message when the app starts
display_welcome_message()

# Run the Tkinter event loop
root.mainloop()
