# Telegram imports
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler, ApplicationBuilder

# Bot Command Hander imports
from CommandHandler import start, newchat, rate

# Bot State Hander imports
from StateHandler import GetQuestion, ImageOption, CheckQuestion, LLaVa_Call, DisplayRateState, PromptRate, UpdatePrompt, SaveImage, LLaVAContinueChat, LLamaContinueChat

# Configrations imports
from config import BOT_TOKEN

# Define the conversation states
InitialState, ImageOptionState, Question_Or_Image_First, DisplayRateState, PromptRateState, LLaVa_State, UpdatePromptState, _, LLaVAContinueChatState, LLamaContinueChatState = range(10)

# Create the Application
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Conversation Handler
MAIN_CONVERSATION = ConversationHandler(
    name="MAIN_CONVERSATION",
    entry_points=[CommandHandler('start', start)],

    states={
        # Fire the GetQuestion function or the SaveImage function
        InitialState: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, GetQuestion),
            MessageHandler(filters.PHOTO, SaveImage),
            CommandHandler("newchat", newchat),
        ],

        # ImageOptionState: Check if user has an image or not
        ImageOptionState: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ImageOption),
            MessageHandler(filters.PHOTO, SaveImage),
            CommandHandler("newchat", newchat),
        ],

        # Check if user has a sent the Image frist or the Question
        Question_Or_Image_First: [
            MessageHandler(filters.ALL, CheckQuestion),
            MessageHandler(filters.ALL, SaveImage),
            CommandHandler("newchat", newchat),
        ],

        DisplayRateState: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, DisplayRateState),
        ],

        # Asks the user to rate the answer
        PromptRateState: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, PromptRate),
            CommandHandler("newchat", newchat),
        ],

        # Calls the L-LaVa model
        LLaVa_State: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, LLaVa_Call),
            CommandHandler("newchat", newchat),
        ],

        # Re-generate the answer based on the user feedback
        UpdatePromptState: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, UpdatePrompt),
            CommandHandler("newchat", newchat),
        ],

        # Save the image whenever the user sends a photo
        SaveImage: [
            MessageHandler(filters.PHOTO, SaveImage),
            CommandHandler("newchat", newchat),
        ],

        LLaVAContinueChatState: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, LLaVAContinueChat),
            CommandHandler("newchat", newchat),
            CommandHandler("rate", rate),
        ],

        LLamaContinueChatState: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, LLamaContinueChat),
            CommandHandler("newchat", newchat),
            CommandHandler("rate", rate),
        ],
    },

    fallbacks=[

    ],
)

# Runs the MAIN_CONVERSATION conversation handler
application.add_handler(MAIN_CONVERSATION)

# Start the Bot
application.run_polling()
