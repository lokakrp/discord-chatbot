import speech_recognition as sr
import pyttsx3

# initialize recognizer
r = sr.Recognizer()


def record_text():
# loop to prevent errors
    while(1):
        try:
            # use the microphone as source for input.
            with sr.Microphone() as source2:
                # prepare recognizer to receive input
                r.adjust_for_ambient_noise(source2, duration=0.2)

                # listens for the user input
                audio2 = r.listen(source2)

                # google usage to recognise audio
                mytext = r.recognise_google(audio2)

                return mytext
            
        except sr.RequestError as e:
            print("could not request results; {0}".format(e))
            
        except sr.UnknownValueError:
            print("unknown error occurred")
    return  

def output_text(text):
    f = open("output.txt", "a")
    f.write(text)
    f.write("\n")
    f.close()
    return

while(1):
    text = record_text()
    output_text(text)
    print("received text")