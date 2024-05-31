class LLaVAChatBot:

    def __init__(self,
                 model_path: str = 'liuhaotian/llava-v1.5-7b',  # Path to the model
                 device_map: str = 'auto',  # Device mapping for model loading
                 load_in_8_bit: bool = True,  # Flag to load model in 8-bit precision
                 **quant_kwargs) -> None:  # Additional keyword arguments for quantization
        pass

    def start_new_chat(self, prompt: str ,img_path: str) -> str:
        answer = f"L-LAVA New Chat Function Call on {prompt} and {img_path}"
        print(answer)
        return answer

    def continue_chat(self, prompt: str) -> str:
        answer = f"L-LAVA Continue Chat Funciton call on {prompt}"
        print(answer)
        return answer