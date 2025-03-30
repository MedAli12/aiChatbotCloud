import time
import logging
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference import ChatCompletionsClient  # Ensure your SDK version supports this
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Configuration for DeepSeek‑R1 using Azure AI Inference SDK
endpoint = "https://ai-chaouachimohamedali7466ai872562483805.services.ai.azure.com/models"
model_name = "DeepSeek-R1"

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential("EW6ViVluOrgcYdzmV2hfq3qY2tGO1QScxK27Jiqyi9czHGX597SaJQQJ99BCACfhMk5XJ3w3AAAAACOGAdDH"),
)

# Telegram Bot Token (replace with your actual token)
TELEGRAM_BOT_TOKEN = "7774343356:AAHQTammQXsAsJz40qhSpRHfF_gORZTv2ec"

# Telegram's maximum allowed message length (in characters)
MAX_TELEGRAM_MSG_LENGTH = 4096

def get_response(prompt):
    """Sends the prompt to DeepSeek‑R1 using the Azure AI Inference SDK and returns the chatbot response."""
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
            # Try to extract the answer from the expected fields.
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
                delay *= 2  # Exponential backoff
            else:
                return "Sorry, I encountered an error while processing your request."

async def start(update, context):
    """Handles the /start command."""
    try:
        await update.message.reply_text("Hello! I'm your DeepSeek‑R1 powered assistant. How can I help you today?")
    except Exception as e:
        logging.error("Error in start command: %s", e)

async def handle_message(update, context):
    """Processes incoming messages from users."""
    user_text = update.message.text
    logging.info("Received message: %s", user_text)
    reply = get_response(user_text)  # This call is synchronous; consider offloading to an executor if needed.
    # Validate and truncate the reply if it's too long
    if not isinstance(reply, str) or not reply.strip():
        reply = "I'm sorry, I didn't get a valid response from the model."
    else:
        reply = reply.strip()
    if len(reply) > MAX_TELEGRAM_MSG_LENGTH:
        reply = reply[:MAX_TELEGRAM_MSG_LENGTH - 3] + "..."
    try:
        await update.message.reply_text(reply)
    except Exception as e:
        logging.error("Error sending reply: %s", e)

def main():
    # Set up logging for debugging purposes
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    # Create the Application using the ApplicationBuilder
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    # Set up command handler for /start and a message handler for text messages.
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # Start the Bot with polling
    logging.info("Bot started. Listening for messages...")
    application.run_polling()

if __name__ == "__main__":
    main()
