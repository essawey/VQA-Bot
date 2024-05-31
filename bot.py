# Telegram imports
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler, ApplicationBuilder
from telegram import Update, ReplyKeyboardMarkup

# Image handling imports
from io import BytesIO
import numpy as np
import cv2

# Configrations imports
from config import *


# TEST MODEL imports
import torch
from LLaVAChatBotTEST import LLaVAChatBot
from LLamaChatBotTEST import LLamaChatBot


# # REAL MODEL imports
# import torch
# from LLaVAChatBot import LLaVAChatBot
# from LLamaChatBot import LLamaChatBot

# Define the conversation states
InitialState, ImageOptionState, Question_Or_Image_First, DisplayRateState, PromptRateState, LLaVa_State, UpdatePromptState, SaveImage, LLaVAContinueChatState, LLamaContinueChatState = range(10)


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
    # Direct to the next state i.e. with out user input 
    return await DisplayRate(update, context)

# InitialState: Waits for the User to sends text and asks if they have an image
async def GetQuestion(update: Update, context: CallbackContext) -> int:
    print("START of GetQuestion")
    context.user_data['question'] = update.message.text
    reply_keyboard = [['Yes', 'No']]
    await update.message.reply_text(
        'Do you have an image to go with your question?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    print("END of GetQuestion")
    return ImageOptionState

# ImageOptionState: User indicates if they have an image or not
# Calls the LLamaChat model if the user do not have an image
async def ImageOption(update: Update, context: CallbackContext) -> int:
    print("START of ImageOption")

    if update.message.text.lower() == 'yes':
        await update.message.reply_text("Please send the image")
        print('END of ImageOption: User has an image')
        return SaveImage
    elif update.message.text.lower() == 'no':
        print('END of ImageOption: User do not have an image')
        answer = LLamaChat.start_new_chat(context.user_data['question'])
        print(f'Answer: {answer}')
        await update.message.reply_text(f'Answer: {answer}')
        return LLamaContinueChatState
    else:
        print('User input is not valid')
        await update.message.reply_text('Please choose a yes or no option')
        return await GetQuestion(update, context)


# Question_Or_Image_First: User sends image
# Check if the user has sent a question and calls the appropriate model
async def CheckQuestion(update: Update, context: CallbackContext) -> int:
    print("START of CheckQuestion")

    if 'question' in context.user_data:
        print('question found ✅')
        print(context.user_data['question'])
        answer = LLaVAChat.start_new_chat(
            prompt=context.user_data['question'],
            img_path=context.user_data['photo'],
        )

        await update.message.reply_text(f'Answer: {answer}')
        return LLaVAContinueChatState
    
    if 'question' not in context.user_data:
        print('question NOT found ❌')
        await update.message.reply_text('Got the image. Now, please ask your question:')
        return LLaVa_State

# Frist call to the L-LaVa model
async def LLaVa_Call(update: Update, context: CallbackContext) -> int:
    print("START of LLaVa_Call")
    question = update.message.text
    context.user_data['question'] = question
    answer = LLaVAChat.start_new_chat(
        prompt = context.user_data['question'],
        img_path = context.user_data['photo'],
    )
    print(f'Answer: {answer}')
    await update.message.reply_text(f'Answer: {answer}')
    print('END of LLaVa_Call')
    return LLaVAContinueChatState

# DisplayRateState: Ask the user to rate the answer
# Provide the user with the rate options
async def DisplayRate(update: Update, context: CallbackContext) -> int:
    print("START of DisplayRate")
    reply_keyboard = [['Skip'], ['1', '2', '3', '4', '5']]
    await update.message.reply_text(
        text='Do you want to rate the answer?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    print("END of DisplayRate")
    return PromptRateState

# PromptRateState: Feedback submission system
async def PromptRate(update: Update, context: CallbackContext) -> int:
    print("START of PromptRate")
    user_rating = update.message.text.lower()

    if user_rating == 'skip':
        print('User skipped the rating')
        await update.message.reply_text('Happy to help!')
        if 'photo' in context.user_data:
            return LLaVAContinueChatState
        else:
            return LLamaContinueChatState


    elif user_rating in ['1', '2', '3', '4']:
        print(f'User rated the answer as {user_rating}')
        await update.message.reply_text('Sorry the answer was not good!')
        reply_keyboard = [['Very long'], ['Very short'], ['Inaccurate'], ['Irrelevant']]
        await update.message.reply_text(
            'Why the answer was bad, give us some feedback?',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return UpdatePromptState

    elif user_rating == '5':
        print('User rated the answer as 5')
        await update.message.reply_text('Thank you for the rating!')
        if 'photo' in context.user_data:
            return LLaVAContinueChatState
        else:
            return LLamaContinueChatState

    else:
        print('User input is not valid')
        await update.message.reply_text('Please choose a rate from the given options')
        return await DisplayRate(update, context)

# Calls the model to re-generate the answer based on the user feedback
# Continues the chat with the updated answer
async def UpdatePrompt(update: Update, context: CallbackContext) -> int:
    print("START of UpdatePrompt")

    user_problem = update.message.text.lower()

    if user_problem in feedback_map.keys():
        if 'photo' in context.user_data:
            nGeneration = LLaVAChat.continue_chat(f"Please the last answer is {feedback_map[user_problem]}")
            await update.message.reply_text(nGeneration)
            print(f"END of UpdatePrompt in LLaVAContinueChatState with {user_problem} option")
            return LLaVAContinueChatState
        else:
            nGeneration = LLamaChat.continue_chat(f"Please the last answer is {feedback_map[user_problem]}")
            await update.message.reply_text(nGeneration)
            print(f"END of UpdatePrompt in LLamaContinueChatState with {user_problem} option")
            return LLamaContinueChatState
    else:
        if 'photo' in context.user_data:
            nGeneration = LLaVAChat.continue_chat(user_problem)
            await update.message.reply_text(nGeneration)
            print(f"END of UpdatePrompt in LLaVAContinueChatState with {user_problem} option")
            return LLaVAContinueChatState
        else:
            nGeneration = LLamaChat.continue_chat(user_problem)
            await update.message.reply_text(nGeneration)
            print(f"END of UpdatePrompt in LLamaContinueChatState with {user_problem} option")
            return LLamaContinueChatState


# SaveImage: Save the image sent by the user
async def SaveImage(update: Update, context: CallbackContext) -> int:
    print("START of SaveImage")
    file = await context.bot.get_file(update.message.photo[-1].file_id)
    f = BytesIO(await file.download_as_bytearray())
    file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    image_path = f"photo_{file.file_id}.jpg"
    cv2.imwrite(image_path, img)
    print(f'Image saved at {image_path}')
    context.user_data['photo'] = image_path
    print("END of SaveImage")
    # Direct to the next state i.e. with out user input 
    return await CheckQuestion(update, context)

# Continue the chat with the L-LaVa model
async def LLaVAContinueChat(update: Update, context: CallbackContext) -> int:
    print("START of LLaVAContinueChat")
    nInput = update.message.text
    nGeneration = LLaVAChat.continue_chat(nInput)
    await update.message.reply_text(nGeneration)
    print("END of LLaVAContinueChat")
    return LLaVAContinueChatState

# Continue the chat with the L-Lama model
async def LLamaContinueChat(update: Update, context: CallbackContext) -> int:
    print("START of LLamaContinueChat")
    nInput = update.message.text
    nGeneration = LLamaChat.continue_chat(nInput)
    await update.message.reply_text(nGeneration)
    print("END of LLamaContinueChat")
    return LLamaContinueChatState

########################## MAIN ##########################

# Load the L-LaVa model
LLaVAChat = LLaVAChatBot(
    load_in_8bit=True,
    bnb_8bit_compute_dtype=torch.float16,
    bnb_8bit_use_double_quant=True,
    bnb_8bit_quant_type='nf8'
)

# Load the L-Lama model
LLamaChat = LLamaChatBot()

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

# runs the MAIN_CONVERSATION conversation handler
application.add_handler(MAIN_CONVERSATION)

# Start the Bot
application.run_polling()
