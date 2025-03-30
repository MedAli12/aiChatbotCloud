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
