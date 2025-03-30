import time
import logging
from flask import Flask, render_template, request, jsonify
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference import ChatCompletionsClient  # Ensure your SDK version supports this

# Configuration for DeepSeek‑R1 using Azure AI Inference SDK
endpoint = "https://ai-chaouachimohamedali7466ai872562483805.services.ai.azure.com/models"
model_name = "DeepSeek-R1"

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential("EW6ViVluOrgcYdzmV2hfq3qY2tGO1QScxK27Jiqyi9czHGX597SaJQQJ99BCACfhMk5XJ3w3AAAAACOGAdDH"),
)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def get_response(prompt):
    """Sends the prompt to DeepSeek‑R1 and returns the chatbot response."""
    max_retries = 5
    delay = 2  # initial delay in seconds
    for attempt in range(max_retries):
        try:
            response = client.complete(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2048,
                temperature=1.0,
                top_p=1.0,
            )
            logging.info("Full response: %s", response)
            choice = response.choices[0]
            if hasattr(choice, 'message') and choice.message is not None and hasattr(choice.message, 'content'):
                return choice.message.content
            elif hasattr(choice, 'text'):
                return choice.text
            else:
                logging.error("Unexpected response structure: %s", choice)
                return "Sorry, I couldn't understand the response from the model."
        except Exception as e:
            logging.error("Attempt %d failed with error: %s", attempt + 1, e)
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                return "Sorry, I encountered an error while processing your request."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Invalid request"}), 400
    user_message = data["message"]
    logging.info("User message: %s", user_message)
    bot_reply = get_response(user_message)
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    # For local testing
    app.run(debug=True, host="0.0.0.0")

import os
from flask import request, jsonify
from azure.storage.blob import BlobServiceClient
from datetime import datetime

# Get the connection string from environment variable
AZURE_STORAGE_CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "chat-history"  # Ensure this container exists in your storage account
BLOB_NAME = "chat_history.txt"

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

def ensure_append_blob_exists():
    """Check if the append blob exists, and create it if not."""
    blob_client = container_client.get_blob_client(BLOB_NAME)
    try:
        blob_client.get_blob_properties()
    except Exception:
        # Create an append blob if it does not exist
        blob_client.create_append_blob()
    return blob_client

@app.route("/save_chat", methods=["POST"])
def save_chat():
    data = request.get_json()
    chat_history = data.get("chat_history", "")
    if not chat_history:
        return jsonify({"error": "No chat history provided"}), 400

    blob_client = ensure_append_blob_exists()
    # Prepare content to append with a timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    content = f"--- Chat saved at {timestamp} UTC ---\n{chat_history}\n"
    try:
        blob_client.append_block(content)
        return jsonify({"message": "Chat history saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to save chat history: {str(e)}"}), 500
