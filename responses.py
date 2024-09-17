import random

def get_response(message: str) -> str:
    p_message = message.lower().strip()  # Strip unnecessary whitespace and lowercase

    # Greeting
    if p_message in ["hello", "hi", "hey"]:
        return random.choice(["hiii!", "hello!!", "heyy!!!", "hi!"])

    # Help command
    if p_message in ["!help", "help", "?"]:
        return (
            "`Commands list:`\n"
            "[chatbot]\n"
            "`hello`: Greet the bot\n"
            "`flip`: Flip a coin\n"
            "`rps`: Play Rock-Paper-Scissors\n"
            "`8ball`: Ask the Magic 8 Ball a question\n"
            "`quote`: Get an inspirational quote\n"
            "\n"
            "[DJ]\n"
            "`play [url]`: Play music from a URL (YouTube, SoundCloud, etc.)\n"
            "`pause`: Pause the current playback\n"
            "`resume`: Resume the paused playback\n"
            "`stop`: Stop the current playback\n"
            "`volume [0-100]`: Set the volume of the playback (0-100)\n"
            "`leave`: Disconnect from the voice channel\n"
        )

    # Coin flip
    if p_message == "flip":
        return f"🪙 You got {random.choice(['heads', 'tails'])}!"

    # Rock Paper Scissors (RPS)
    if p_message.startswith("rps"):
        user_choice = p_message.split()[1] if len(p_message.split()) > 1 else ""
        rps_choices = ["rock", "paper", "scissors"]
        
        if user_choice in rps_choices:
            bot_choice = random.choice(rps_choices)
            result = check_rps_result(user_choice, bot_choice)
            return f"🎮 You chose {user_choice}, I chose {bot_choice}. {result}"
        else:
            return "Please choose `rock`, `paper`, or `scissors` by typing `rps <choice>`."

    # Magic 8 Ball
    if p_message == "8ball":
        responses = [
            "It is certain.", "Without a doubt.", "You may rely on it.",
            "Yes, definitely.", "As I see it, yes.", "Most likely.", 
            "Outlook good.", "Yes.", "No.", "Don't count on it.", 
            "My sources say no.", "Very doubtful.", "Cannot predict now."
        ]
        return f"🎱 {random.choice(responses)}"

    # Inspirational quote
    if p_message == "quote":
        quotes = [
            "Believe in yourself and all that you are.",
            "Act as if what you do makes a difference. It does.",
            "Success is not final, failure is not fatal: It is the courage to continue that counts.",
            "What lies behind us and what lies before us are tiny matters compared to what lies within us."
        ]
        return random.choice(quotes)

    # Unknown command
    return 'I don\'t understand that. Try "!help" for a list of commands.'

# Helper function to determine Rock Paper Scissors result
def check_rps_result(user_choice: str, bot_choice: str) -> str:
    if user_choice == bot_choice:
        return "It's a tie!"
    elif (user_choice == "rock" and bot_choice == "scissors") or \
         (user_choice == "scissors" and bot_choice == "paper") or \
         (user_choice == "paper" and bot_choice == "rock"):
        return "You win!"
    else:
        return "I win!"

# Example test cases
if __name__ == "__main__":
    print(get_response("hello"))          # Random greeting
    print(get_response("flip"))           # Flip a coin
    print(get_response("rps rock"))       # Play rock-paper-scissors
    print(get_response("8ball"))          # Magic 8 ball response
    print(get_response("quote"))          # Inspirational quote
    print(get_response("!help"))          # List of commands
    print(get_response("unknown"))        # Unknown command
