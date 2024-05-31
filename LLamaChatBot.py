#FIXME: Add the L-Lama ChatBot Model

class LLamaChatBot:
    def __init__(self) -> None:

        # Here you can add initialization code if necessary
        pass

    def start_new_chat(self, question: str) -> str:
        answer = f"L-LAMA New Chat Function Call on {question}"
        print(answer)
        return answer

    def continue_chat(self, question: str) -> str:
        answer = f"L-LAMA Continue Chat Funciton call on {question}"
        print(answer)
        return answer