import cohere
import uuid
import json
import os

class AIChatbot:
    def __init__(self, api_key):
        self.client = cohere.Client(api_key)
        self.conversation_id = str(uuid.uuid4())
        self.personality = "i type in lowercase letters, i am a friendly robot who speaks in a schizophrenic way and is very crazy and silly."
        self.chat_history = []
        self.load_knowledge()

    def load_knowledge(self):
        if os.path.exists('knowledge.json'):
            with open('knowledge.json', 'r') as f:
                self.knowledge_base = json.load(f)
        else:
            self.knowledge_base = {}

    def save_knowledge(self):
        with open('knowledge.json', 'w') as f:
            json.dump(self.knowledge_base, f)

    async def get_cohere_response(self, user_message):
        self.chat_history.append({"role": "USER", "message": user_message})
        self.chat_history.insert(0, {"role": "SYSTEM", "message": self.personality})

        stream = self.client.chat_stream(
            message=user_message,
            model="command-r-plus",
            preamble=self.personality,
            conversation_id=self.conversation_id,
        )

        bot_message = ""
        for event in stream:
            if event.event_type == "text-generation":
                bot_message += event.text
            if event.event_type == "stream-end":
                self.chat_history = event.response.chat_history

        self.chat_history.append({"role": "CHATBOT", "message": bot_message})
        return bot_message

    async def learn(self, new_info):
        self.knowledge_base[new_info] = new_info
        self.save_knowledge()
        self.chat_history.append({"role": "CHATBOT", "message": f"Learned: {new_info}"})

    async def refresh_knowledge(self):
        self.chat_history = []
        self.chat_history.append({"role": "CHATBOT", "message": "i've cleared my short term memory!"})
