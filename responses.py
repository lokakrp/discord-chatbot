import random

def get_responses(message:str ) -> str:        #
    p_message = message.lower()                # processed message is lowercase

    if p_message == "hello":
        return "hii"
    
    if message == "roll":
        return str(random.randint(1, 6))
    
    if p_message == "!help":
        return "`Commands list:`"
    
    return 'I don\'t understand you sorry. Please try "!help"'