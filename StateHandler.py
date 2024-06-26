# Telegram Imports
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from config import feedback_map, print_ar

# Text to Speech imports
from Text2Speech import text2Speech

# Image handling imports
from io import BytesIO
import numpy as np
import cv2


import logging

# Translation Layer imports
from TranslationLayer import ToEN, fromEN, UserLanguage

# # TEST MODEL imports
# import torch
# from LLaVAChatBotTEST import LLaVAChatBot
# from LLamaChatBotTEST import LLamaChatBot


# REAL MODEL imports
import torch
from LLaVAChatBot import LLaVAChatBot
from LLamaChatBot import LLamaChatBot


InitialState, ImageOptionState, Question_Or_Image_First, DisplayRateState, PromptRateState, LLaVa_State, UpdatePromptState, SaveImage, LLaVAContinueChatState, LLamaContinueChatState = range(10)

# Load the L-LaVa model
LLaVAChat = LLaVAChatBot(
    load_in_8bit=True,
    bnb_8bit_compute_dtype=torch.float16,
    bnb_8bit_use_double_quant=True,
    bnb_8bit_quant_type='nf8'
)

# Load the L-Lama model
LLamaChat = LLamaChatBot()


# InitialState: Waits for the User to sends text and asks if they have an image
async def GetQuestion(update: Update, context: CallbackContext) -> int:
    print("START of GetQuestion")
    context.user_data['question'] = update.message.text
    
    # Get the User's language

    user_language = UserLanguage(context.user_data['question'])
    context.user_data['UserLanguage'] = user_language
    print(f'User language: {user_language}')



    reply_keyboard = [[
        fromEN(
            UserLanguage=context.user_data['UserLanguage'],
            text = 'Yes'),
        fromEN(
            UserLanguage=context.user_data['UserLanguage'],
            text = 'No'),
        ]]
    await update.message.reply_text(
        fromEN(
            UserLanguage=context.user_data['UserLanguage'],
            text='Do you have an image to go with your question?'
        ),
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    print("END of GetQuestion")
    return ImageOptionState

# ImageOptionState: User indicates if they have an image or not
# Calls the LLamaChat model if the user do not have an image
async def ImageOption(update: Update, context: CallbackContext) -> int:
    print("START of ImageOption")

    if update.message.text.lower() == fromEN(
            UserLanguage=context.user_data['UserLanguage'],
            text = 'Yes').lower():
        
        GetImageReply = fromEN(
            UserLanguage = context.user_data['UserLanguage'],
            text = "Please send the image"
        )

        await update.message.reply_text(GetImageReply)
        print('END of ImageOption: User has an image')
        return SaveImage
    
    elif update.message.text.lower() == fromEN(
            UserLanguage=context.user_data['UserLanguage'],
            text = 'No').lower():
        
        print('END of ImageOption: User do not have an image')
        UserLanguagePrompt = context.user_data['question']

        EnglishPrompt = ToEN(
            UserLanguage = context.user_data['UserLanguage'],
            text = UserLanguagePrompt
        )

        # EnglishAnswer = LLamaChat.start_new_chat(EnglishPrompt)

        #FIXME
        EnglishAnswer = LLaVAChat.start_new_chat(
            prompt = EnglishPrompt,
            img_path = "one-black.jpg",
        )        
        print(f'{EnglishAnswer = }')

        UserLanguageAnswer = fromEN(
            UserLanguage = context.user_data['UserLanguage'],
            text = EnglishAnswer
        )
        print(f'{UserLanguageAnswer = }')
        await update.message.reply_text(UserLanguageAnswer)
        text2Speech(text = UserLanguageAnswer)
        audio_file_path = 'audio_file.mp3'
        with open(audio_file_path, 'rb') as audio_file:
            await update.message.reply_voice(voice = audio_file)

        return LLamaContinueChatState
    else:
        print('User input is not valid')
        await update.message.reply_text(fromEN(
            UserLanguage=context.user_data['UserLanguage'],
            text = 'Please choose Yes or No'))
        return await GetQuestion(update, context)


# Question_Or_Image_First: User sends image
# Check if the user has sent a question and calls the appropriate model
async def CheckQuestion(update: Update, context: CallbackContext) -> int:
    print("START of CheckQuestion")


    if 'question' in context.user_data:
        print('question found ✅')

        EnglishPrompt = ToEN(
            UserLanguage = context.user_data['UserLanguage'],
            text = context.user_data['question']
        )

        print(context.user_data['question'])
        print(EnglishPrompt)

        print("MODEL RUN")
        EnglishAnswer = LLaVAChat.start_new_chat(
            prompt = EnglishPrompt,
            img_path = context.user_data['photo'],
        )

        UserLanguageAnswer = fromEN(
            UserLanguage=context.user_data['UserLanguage'],
            text = EnglishAnswer
        )
        print(f'{EnglishAnswer = }')
        print(f'{UserLanguageAnswer = }')

        await update.message.reply_text(UserLanguageAnswer)
        audio_file_path = 'audio_file.mp3'
        with open(audio_file_path, 'rb') as audio_file:
            await update.message.reply_voice(voice = audio_file)

        return LLaVAContinueChatState
    
    if 'question' not in context.user_data:
        print('question NOT found ❌')
        GotImage = "Got the image ✅."
        AskQuestion = "Now, Please ask your question:"
    

        await update.message.reply_text(GotImage)
        await update.message.reply_text(AskQuestion)
        return LLaVa_State

# Frist call to the L-LaVa model
async def LLaVa_Call(update: Update, context: CallbackContext) -> int:
    print("START of LLaVa_Call")
    question = update.message.text

    context.user_data['question'] = question
    context.user_data['UserLanguage'] = UserLanguage(context.user_data['question'])

    EnglishPrompt = ToEN(
        UserLanguage = context.user_data['UserLanguage'],
        text = context.user_data['question']
    )

    print("MODEL RUN")
    print(context.user_data['question'])
    print(EnglishPrompt)

    EnglishAnswer = LLaVAChat.start_new_chat(
        prompt = EnglishPrompt,
        img_path = context.user_data['photo'],
    )

    UserLanguageAnswer = fromEN(
        UserLanguage=context.user_data['UserLanguage'],
        text = EnglishAnswer
    )

    UserLanguageAnswer = str(UserLanguageAnswer)
    print(f'{EnglishAnswer = }')
    print()
    print_ar(f'{UserLanguageAnswer = }')
    await update.message.reply_text(UserLanguageAnswer)
    text2Speech(text = UserLanguageAnswer)
    audio_file_path = 'audio_file.mp3'
    with open(audio_file_path, 'rb') as audio_file:
        await update.message.reply_voice(voice = audio_file)

    print('END of LLaVa_Call')
    return LLaVAContinueChatState

# DisplayRateState: Ask the user to rate the answer
# Provide the user with the rate options
async def DisplayRate(update: Update, context: CallbackContext) -> int:
    print("START of DisplayRate")

    RateQuestion = fromEN(
        UserLanguage=context.user_data['UserLanguage'],
        text="How do you want to rate the answer?"
    )

    RateAnswer_skip = fromEN(
        UserLanguage=context.user_data['UserLanguage'],
        text="Skip"
    )
    reply_keyboard = [[RateAnswer_skip], ['1', '2', '3', '4', '5']]

    await update.message.reply_text(
        text=RateQuestion,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    print("END of DisplayRate")
    return PromptRateState

# PromptRateState: Feedback submission system
async def PromptRate(update: Update, context: CallbackContext) -> int:
    print("START of PromptRate")
    user_rating = update.message.text.lower()

    if user_rating == fromEN(
        UserLanguage=context.user_data['UserLanguage'],
        text="Skip"
    ):
        print('User skipped the rating')
        await update.message.reply_text('Happy to help!')
        if 'photo' in context.user_data:
            return LLaVAContinueChatState
        else:
            return LLamaContinueChatState


    elif user_rating in ['1', '2', '3', '4']:
        print(f'User rated the answer as {user_rating}')

        SorryReply = fromEN(
            UserLanguage=context.user_data['UserLanguage'],
            text='Sorry the answer was not good!'
        )
        feedbackQuestion = fromEN(
            UserLanguage=context.user_data['UserLanguage'],
            text='Why the answer was bad, give us some feedback?'
        )
        feedbackAnswer1 = fromEN(
            UserLanguage=context.user_data['UserLanguage'],
            text="Very long"
        )
        feedbackAnswer2 = fromEN(
            UserLanguage=context.user_data['UserLanguage'],
            text="Very short"
        )
        feedbackAnswer3 = fromEN(
            UserLanguage=context.user_data['UserLanguage'],
            text="Inaccurate"
        )
        feedbackAnswer4 = fromEN(
            UserLanguage=context.user_data['UserLanguage'],
            text="Irrelevant"
        )
        ThankyouReply = fromEN(
            UserLanguage=context.user_data['UserLanguage'],
            text="Thank you for the rating ❤️!"
        )

        await update.message.reply_text(SorryReply)

        reply_keyboard = [[feedbackAnswer1], [feedbackAnswer2], [feedbackAnswer3], [feedbackAnswer4]]
        await update.message.reply_text(
            feedbackQuestion,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )

        return UpdatePromptState

    elif user_rating == '5':
        print('User rated the answer as 5')
        await update.message.reply_text(ThankyouReply)
        if 'photo' in context.user_data:
            return LLaVAContinueChatState
        else:
            return LLamaContinueChatState

    else:
        BadReply = fromEN(
            UserLanguage=context.user_data['UserLanguage'],
            text="Please choose a answer from the given options"
        )

        print('User input is not valid')
        await update.message.reply_text(BadReply)
        return await DisplayRate(update, context)

# Calls the model to re-generate the answer based on the user feedback
# Continues the chat with the updated answer
async def UpdatePrompt(update: Update, context: CallbackContext) -> int:
    print("START of UpdatePrompt")
    
    user_problem = update.message.text.lower()
    user_language = context.user_data['UserLanguage']
    user_problem_en = ToEN(UserLanguage=user_language, text=user_problem)

    is_photo = 'photo' in context.user_data
    chat_instance = LLaVAChat if is_photo else LLamaChat

    if user_problem in feedback_map:
        message = f"Please the last answer is \"{feedback_map[user_problem]}\""
    else:
        message = user_problem_en

    n_generation = chat_instance.continue_chat(message)

    n_generation = fromEN(
        UserLanguage = context.user_data['UserLanguage'],
        text = n_generation
    )

    await update.message.reply_text(n_generation)
    text2Speech(text = UserLanguageAnswer)

    audio_file_path = 'audio_file.mp3'
    with open(audio_file_path, 'rb') as audio_file:
        await update.message.reply_voice(voice = audio_file)


    chat_state = LLaVAContinueChatState if is_photo else LLamaContinueChatState
    print(f"END of UpdatePrompt with {user_problem} option")
    return chat_state

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
    UserLanguageQuestion = update.message.text
    print(f"{UserLanguageQuestion = }")

    # User Language to Englsih
    EnglishQuestion = ToEN(
        UserLanguage=context.user_data['UserLanguage'],
        text=UserLanguageQuestion
    )
    print(f"{EnglishQuestion = }")

    # Model call on english text
    EnglishAnswer = LLaVAChat.continue_chat(EnglishQuestion)

    # Englsih Answer to User Language
    UserLanguageAnswer = fromEN(
        UserLanguage=context.user_data['UserLanguage'],
        text=EnglishAnswer
    )
    await update.message.reply_text(UserLanguageAnswer)
    text2Speech(text = UserLanguageAnswer)

    audio_file_path = 'audio_file.mp3'
    with open(audio_file_path, 'rb') as audio_file:
        await update.message.reply_voice(voice = audio_file)

    print("END of LLaVAContinueChat")
    return LLaVAContinueChatState


# Continue the chat with the L-Lama model
async def LLamaContinueChat(update: Update, context: CallbackContext) -> int:
    print("START of LLamaContinueChat")

    UserLanguageQuestion = update.message.text
    print(f"{UserLanguageQuestion = }")

    # User Language to Englsih
    EnglishQuestion = ToEN(
        UserLanguage=context.user_data['UserLanguage'],
        text=UserLanguageQuestion
    )
    print(f"{EnglishQuestion = }")

    # Model call on english text
    EnglishAnswer = LLaVAChat.continue_chat(EnglishQuestion)

    # Englsih Answer to User Language
    UserLanguageAnswer = fromEN(
        UserLanguage=context.user_data['UserLanguage'],
        text=EnglishAnswer
    )
    await update.message.reply_text(UserLanguageAnswer)

    print("END of LLamaContinueChat")
    return LLamaContinueChatState
