import torch
import requests
from PIL import Image
from io import BytesIO
from llava.utils import disable_torch_init
from llava.model import LlavaLlamaForCausalLM
from transformers import AutoTokenizer, BitsAndBytesConfig
from llava.conversation import conv_templates, SeparatorStyle
from llava.mm_utils import tokenizer_image_token, KeywordsStoppingCriteria
from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN, DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN


class LLaVAChatBot:
    def __init__(self,
                 model_path: str = 'liuhaotian/llava-v1.5-7b',  # Path to the model
                 device_map: str = 'auto',  # Device mapping for model loading
                 load_in_8_bit: bool = True,  # Flag to load model in 8-bit precision
                 **quant_kwargs) -> None:  # Additional keyword arguments for quantization
        self.model = None  # Placeholder for the model
        self.tokenizer = None  # Placeholder for the tokenizer
        self.image_processor = None  # Placeholder for the image processor
        self.conv = None  # Placeholder for conversation state
        self.conv_img = None  # Placeholder for image conversation state
        self.img_tensor = None  # Placeholder for image tensor
        self.roles = None  # Placeholder for roles in conversation
        self.stop_key = None  # Placeholder for stop key in conversation
        self.load_models(model_path,  # Load the models with specified parameters
                         device_map=device_map,  # Device mapping for loading
                         load_in_8_bit=load_in_8_bit,  # 8-bit precision loading flag
                         **quant_kwargs)  # Additional quantization arguments

    def load_models(self, model_path: str,
                    device_map: str,
                    load_in_8_bit: bool,
                    **quant_kwargs) -> None:
        """Load the model, processor and tokenizer."""
        quant_cfg = BitsAndBytesConfig(**quant_kwargs)  # Create quantization configuration
        self.model = LlavaLlamaForCausalLM.from_pretrained(model_path,  # Load the model from the specified path
                                                           low_cpu_mem_usage=True,  # Use low CPU memory
                                                           device_map=device_map,  # Device mapping for loading
                                                           load_in_8bit=load_in_8_bit,  # Load model in 8-bit precision
                                                           quantization_config=quant_cfg)  # Apply quantization config
        self.tokenizer = AutoTokenizer.from_pretrained(model_path,  # Load the tokenizer from the specified path
                                                       use_fast=False)  # Use the slow version of the tokenizer
        vision_tower = self.model.get_vision_tower()  # Get the vision tower component of the model
        vision_tower.load_model()  # Load the vision tower model
        vision_tower.to(device='cuda')  # Move the vision tower model to the CUDA device
        self.image_processor = vision_tower.image_processor  # Set the image processor from the vision tower
        disable_torch_init()  # Disable PyTorch's default initialization to save memory

    def setup_image(self, img_path: str) -> None:
        """Load and process the image."""
        if img_path.startswith('http') or img_path.startswith('https'):  # Check if the image path is a URL
            response = requests.get(img_path)  # Fetch the image from the URL
            self.conv_img = Image.open(BytesIO(response.content)).convert('RGB')  # Open the image and convert to RGB
        else:  # If the image path is a local path
            self.conv_img = Image.open(img_path).convert('RGB')  # Open the image and convert to RGB
        self.img_tensor = self.image_processor.preprocess(self.conv_img,  # Preprocess the image
                                                          return_tensors='pt'  # Return as PyTorch tensors
                                                          )['pixel_values'].half().cuda()  # Convert to half precision and move to CUDA

    def generate_answer(self, **kwargs) -> str:
        """Generate an answer from the current conversation."""
        raw_prompt = self.conv.get_prompt()  # Get the current conversation prompt
        input_ids = tokenizer_image_token(raw_prompt,  # Tokenize the prompt with image token support
                                          self.tokenizer,  # Use the chatbot's tokenizer
                                          IMAGE_TOKEN_INDEX,  # Index for the image token
                                          return_tensors='pt').unsqueeze(0).cuda()  # Return as PyTorch tensors, add batch dim, move to CUDA
        stopping = KeywordsStoppingCriteria([self.stop_key],  # Define stopping criteria for generation
                                            self.tokenizer,  # Use the tokenizer for stopping criteria
                                            input_ids)  # Input IDs for stopping criteria context
        with torch.inference_mode():  # Disable gradient computation for inference
            output_ids = self.model.generate(input_ids,  # Generate output IDs from the model
                                             images=self.img_tensor,  # Provide the preprocessed image tensor
                                             stopping_criteria=[stopping],  # Apply stopping criteria
                                             **kwargs)  # Additional generation parameters
        outputs = self.tokenizer.decode(  # Decode the output IDs to text
            output_ids[0, input_ids.shape[1]:]  # Exclude the input prompt from the output
        ).strip()  # Remove leading/trailing whitespace
        self.conv.messages[-1][-1] = outputs  # Update the last message in the conversation with the output

        return outputs.rsplit('</s>', 1)[0]  # Return the output text, remove the trailing stop token

    def get_conv_text(self) -> str:
        """Return full conversation text."""
        return self.conv.get_prompt()  # Get the full conversation text from the conversation object

    def start_new_chat(self,
                       img_path: str,  # Path to the image for the new chat
                       prompt: str,  # Initial text prompt for the new chat
                       do_sample=True,  # Flag to enable sampling during generation
                       temperature=0.2,  # Sampling temperature for generation
                       max_new_tokens=1024,  # Maximum number of new tokens to generate
                       use_cache=True,  # Flag to enable caching during generation
                       **kwargs) -> str:  # Additional keyword arguments for generation
        """Start a new chat with a new image."""
        conv_mode = "v1"  # Set the conversation mode
        self.setup_image(img_path)  # Load and process the image
        self.conv = conv_templates[conv_mode].copy()  # Create a new conversation from the template
        self.roles = self.conv.roles  # Set the roles for the conversation
        first_input = (DEFAULT_IM_START_TOKEN + DEFAULT_IMAGE_TOKEN +  # Construct the first input message with image tokens
                       DEFAULT_IM_END_TOKEN + '\n' + prompt)  # Append the initial text prompt
        self.conv.append_message(self.roles[0], first_input)  # Add the first input message to the conversation
        self.conv.append_message(self.roles[1], None)  # Add a placeholder for the response
        if self.conv.sep_style == SeparatorStyle.TWO:  # Check the separator style for the conversation
            self.stop_key = self.conv.sep2  # Use the second separator if applicable
        else:
            self.stop_key = self.conv.sep  # Use the default separator
        answer = self.generate_answer(do_sample=do_sample,  # Generate the answer using the specified parameters
                                      temperature=temperature,  # Set the sampling temperature
                                      max_new_tokens=max_new_tokens,  # Set the maximum number of new tokens
                                      use_cache=use_cache,  # Enable or disable caching
                                      **kwargs)  # Additional arguments for generation
        return answer  # Return the generated answer

    def continue_chat(self,
                      prompt: str,  # Text prompt to continue the chat
                      do_sample=True,  # Flag to enable sampling during generation
                      temperature=0.2,  # Sampling temperature for generation
                      max_new_tokens=1024,  # Maximum number of new tokens to generate
                      use_cache=True,  # Flag to enable caching during generation
                      **kwargs) -> str:  # Additional keyword arguments for generation
        """Continue the existing chat."""
        if self.conv is None:  # Check if there's an existing conversation
            raise RuntimeError("No existing conversation found. Start a new"
                               "conversation using the `start_new_chat` method.")  # Raise error if no conversation exists
        self.conv.append_message(self.roles[0], prompt)  # Add the new prompt as a message from the user
        self.conv.append_message(self.roles[1], None)  # Add a placeholder for the response
        answer = self.generate_answer(do_sample=do_sample,  # Generate the answer using the specified parameters
                                      temperature=temperature,  # Set the sampling temperature
                                      max_new_tokens=max_new_tokens,  # Set the maximum number of new tokens
                                      use_cache=use_cache,  # Enable or disable caching
                                      **kwargs)  # Additional arguments for generation
        return answer  # Return the generated answer