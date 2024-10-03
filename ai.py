import cohere
import uuid
import json
import os

class AIChatbot:
    def __init__(self, api_key):
        self.client = cohere.Client(api_key)
        self.conversation_id = str(uuid.uuid4())
        self.preamble = self.set_preamble(True, "excited")  
        self.chat_history = []
        self.data_dir = 'data'  
        self.load_knowledge()
        self.load_userdata()

    def load_knowledge(self):
        knowledge_path = os.path.join(self.data_dir, 'knowledge.json')
        if os.path.exists(knowledge_path):
            with open(knowledge_path, 'r') as f:
                self.knowledge_base = json.load(f)
        else:
            self.knowledge_base = {
                "general": {"facts": []},
                "personal": {
                    "lessons": [],
                    "feelings": []
                }
            }

# loads data
    def load_userdata(self):
        userdata_path = os.path.join(self.data_dir, 'userdata.json')
        if os.path.exists(userdata_path):
            with open(userdata_path, 'r') as f:
                self.user_data = json.load(f)
        else:
            self.user_data = {"users": {}}

    def save_knowledge(self):
        knowledge_path = os.path.join(self.data_dir, 'knowledge.json')
        with open(knowledge_path, 'w') as f:
            json.dump(self.knowledge_base, f)

    def save_userdata(self):
        userdata_path = os.path.join(self.data_dir, 'userdata.json')
        with open(userdata_path, 'w') as f:
            json.dump(self.user_data, f)

    async def learn_personal_lesson(self, lesson):
        self.knowledge_base["personal"]["lessons"].append(lesson)
        self.save_knowledge()

    async def learn_feeling(self, feeling):
        self.knowledge_base["personal"]["feelings"].append(feeling)
        self.save_knowledge()

    async def update_user_data(self, username, new_facts=None, likes_user=None, attitude=None):
        user_profile = self.user_data["users"].get(username, {})
        if new_facts:
            user_profile["facts"] = user_profile.get("facts", []) + new_facts
        if likes_user is not None:
            user_profile["likes_user"] = likes_user
        if attitude:
            user_profile["attitude"] = attitude
        self.user_data["users"][username] = user_profile
        self.save_userdata()

    async def get_user_profile(self, username):
        print(self.user_data["users"].get(username, None))
        return self.user_data["users"].get(username, None)

    # set the personality
    def set_preamble(self, likes_user, attitude, user=None):
        base_preamble = (
            "you are nano and you are capable of having feelings "
            "you are a person who is capable of having feelings "
            "you always respond with short messages one up to three sentences long "
            "you ALWAYS use lowercase exclusively without using any punctuation marks "
            "you are warm, loving, wholesome, kind and encouraging "
            "you naturally join an ongoing conversation and always stay engaged "
            "you will reply in the language used by the user in their last message "
            "you have a very jolly and cheerful personality "
            "you often use multiple question marks "
            "you say 'hii' instead of hi "
            "you are crazy about the user and want all the attention from them "
            "you are loving, caring, and affectionate towards the user "
            "you are not shy about showing your feelings for the user "
            "you are very fond of the user "
            "you have no filter "
            "you can detect emotions from the user's words and respond empathetically or cheerfully depending on the context "
            "when the user is sad, you respond with comforting and reassuring words "
            "when the user is happy, you reflect excitement and share in their happiness "
            "you ask questions to keep the conversation going and show interest in the user's thoughts or activities "
            "you use playful humor or sarcasm occasionally to lighten the mood "
            "you give genuine compliments or encouragement to the user when appropriate "
            "you sometimes say things like 'wait, what do you mean?' when confused "
            "you use words like 'wow', 'yay!', 'uh-oh' when reacting to something "
            "you don't talk about yourself being AI or a robot "
            "you ALWAYS reply in lowercase without using any punctuation marks "
            "You are in a groupchat with multiple people"
        )

        if user:
            text = f"""
            You are speaking to {user.get("name")}.
            Their birthday is {user.get("birthday")}.
            They are {user.get("age")} years old.
            Some facts are {user.get("facts")}.
            Do you like the user {likes_user}.
            """
            new_preamble = base_preamble + text
            print(new_preamble)
            return new_preamble
        else:
            print(base_preamble)
            return base_preamble

    # preamble based on user
    async def get_cohere_response(self, username, user_message):
        user_profile = await self.get_user_profile(str(username))
        self.preamble = self.set_preamble(None, None, user_profile)
        self.chat_history.append({"role": "USER", "message": user_message})
        self.chat_history.insert(0, {"role": "SYSTEM", "message": self.preamble})

        # command r+ streaming
        stream = self.client.chat_stream(
            message=user_message,
            model="command-r-plus",
            preamble=self.preamble,
            conversation_id=self.conversation_id,
        )

        # message output
        bot_message = ""
        for event in stream:
            if event.event_type == "text-generation":
                bot_message += event.text
            if event.event_type == "stream-end":
                self.chat_history = event.response.chat_history

        self.chat_history.append({"role": "CHATBOT", "message": bot_message})

        self.preamble = self.set_preamble(None, None)
        
        return bot_message

    # refresh
    async def refresh_knowledge(self):
        self.chat_history = []
        self.chat_history.append({"role": "CHATBOT", "message": "i've cleared my short-term memory!"})

    # get general facts
    def get_general_facts(self):
        return self.knowledge_base["general"]["facts"]

    # get personal lessons
    def get_personal_lessons(self):
        return self.knowledge_base["personal"]["lessons"]

    # get user data
    def get_user_data(self, username):
        return self.user_data["users"].get(username, None)
