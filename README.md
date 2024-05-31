# Ocean: Multi-Modal Question & Answer Bot

## Description

Ocean is a Multi-Modal Question & Answer Bot designed to interact with users through the Telegram messaging platform. It provides answers to text-based questions and questions accompanied by images, utilizing advanced AI models to generate responses. Ocean is a versatile tool for a variety of user queries.

## Key Features

### Text-based Question Answering

- Users can ask any question by sending a text message to the bot.
- The bot processes the question using the LLamaChatBot model and provides a text response.

### Image-based Question Answering

- Users can send an image with their question, and the bot uses the LLaVAChatBot model to analyze both the image and the text prompt.
- The bot saves the image, processes it, and generates an appropriate response considering both inputs.

### Feedback System

- After receiving an answer, users are prompted to rate the response on a scale from 1 to 5.
- Users can provide specific feedback if the response is not satisfactory (e.g., too long, too short, inaccurate, or irrelevant).
- The bot uses this feedback to improve subsequent answers.

### Chat Management

- Users can clear the chat history and start a new conversation using the `/newchat` command.
- The bot maintains the context of the conversation, allowing for a continuous and coherent dialogue.

## Workflow

### 1. Starting the Bot

- Users initiate interaction with the bot using the `/start` command.
- The bot welcomes the user and prompts them to ask a question or send an image.

### 2. Handling User Inputs

#### Initial Input

- If the user sends a text message, the bot asks if they have an image to accompany the question.
- If the user sends an image, the bot saves the image and asks for the associated question.

#### Image Option

- If the user confirms they have an image, they are prompted to send it.
- If not, the bot processes the text question using the LLamaChatBot model and responds accordingly.

### 3. Processing Inputs

#### Text-Only

- The bot uses the LLamaChatBot model to generate a response based on the user's question.

#### Text and Image

- The bot saves the image and uses the LLaVAChatBot model to process both the image and the text prompt to generate a comprehensive response.

### 4. Providing Feedback

- After receiving a response, users can rate the answer.
- Based on the rating and feedback, the bot can re-generate the answer to better meet the user's expectations.

## Technical Details

- **Libraries and Frameworks**: The bot is built using the `python-telegram-bot` library for interaction with the Telegram API, `torch` for model inference, `numpy` and `opencv` for image processing.
- **AI Models**:
  - **LLaVAChatBot**: Used for handling questions that come with images.
  - **LLamaChatBot**: Used for handling text-only questions.
- **States and Handlers**: The bot uses a conversation handler to manage different states of the interaction, ensuring a smooth flow from one step to the next.

## Commands

- `/start` - Initiate the bot and start a new conversation.
- `/newchat` - Clear the current chat and start a new one.
- `/rate` - Invoke the rating system to provide feedback on the bot's responses.

## Usage Example

1. **User**: `/start`
2. **Bot**: "Welcome! Ask any Question or Send any Image ✨"
3. **User**: "What is the capital of France?"
4. **Bot**: "Do you have an image to go with your question? (Yes/No)"
5. **User**: "No"
6. **Bot**: (Processes the question using LLamaChatBot) "The capital of France is Paris."
7. **Bot**: "Do you want to rate the answer? (Skip/1/2/3/4/5)"
8. **User**: "5"
9. **Bot**: "Thank you for the rating!"

This bot provides an interactive and dynamic way for users to get answers to their questions, leveraging both text and image inputs to enhance the quality and relevance of the responses.

---

**Note**: Please ensure you have the necessary dependencies installed and correctly configured before running the bot.
