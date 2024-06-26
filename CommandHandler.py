from telegram import Update
from telegram.ext import CallbackContext

InitialState, ImageOptionState, Question_Or_Image_First, DisplayRateState, PromptRateState, LLaVa_State, UpdatePromptState, SaveImage, LLaVAContinueChatState, LLamaContinueChatState = range(10)
from StateHandler import DisplayRate

# Start function
async def start(update: Update, context: CallbackContext) -> int:
    context.user_data.clear()
    await update.message.reply_text('Welcome!, Ask any Question or Send any Image ✨')
    print("BOT: Welcome!, Ask any Question or Send any Image ✨")
    return InitialState

# Clear the chat and initialize a new one
async def newchat(update: Update, context: CallbackContext) -> int:
    context.user_data.clear()
    await update.message.reply_text('Cleared Chat 🧹')
    print("BOT: Cleared Chat 🧹")
    return InitialState

# Initialize the rate system
async def rate(update: Update, context: CallbackContext) -> int:
    print("User requested to rate the answer")
    # Direct call to the next state i.e. without user input 
    return await DisplayRate(update, context)