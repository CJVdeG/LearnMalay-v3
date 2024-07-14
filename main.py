# ---------------------------- IMPORTS ------------------------------- #
from gtts import gTTS
import pygame
import os

from tkinter import ttk
from tkinter import *
import random
import pandas as pd

from threading import Thread

# ---------------------------- VARIABLE DECLARATION ------------------------------- #
BACKGROUND_COLOR = "B1DDC6"
to_learn = {}
current_card = {}
current_direction = "malay_to_english"  # Default direction

# Create a variable to track the "Auto-pronounce" feature state
auto_pronounce = False

# Add variable for storing after IDs
pending_pronunciation = None

# Keep track of difficult words
difficult_words = []

# ---------------------- FRONT FLASH CARD FUNCTIONALITY ----------------------- #
# Creating a list of dictionaries from the CSV file using a dataframe

try:
    dataframe = pd.read_csv("data/words_to_learn.csv")

except FileNotFoundError:
    dataframe = pd.read_csv("data/1-GettingStarted.csv")
    to_learn = dataframe.to_dict(orient="records")

else:
    to_learn = dataframe.to_dict(orient="records")


# ---------------------------- INITIALIZE FLASHCARDS ------------------------------- #
# Define a function to initialize the flashcards (used for program restart)
def initialize_flashcards(file_path):
    global to_learn
    try:
        # Check if the file exists and if it is empty
        if os.path.exists(file_path) and os.path.getsize(file_path) == 0:
            # If the file is empty, remove it
            os.remove(file_path)
            raise FileNotFoundError  # Raise FileNotFoundError to load the preconfigured list

        df = pd.read_csv(file_path)
        if df.empty:
            # Handle empty DataFrame
            raise ValueError("The file is empty")

    except (FileNotFoundError, ValueError) as e:
        # If the file doesn't exist or was empty, load the preconfigured list
        print(e)
        df = pd.read_csv("data/1-GettingStarted.csv")

    to_learn = df.to_dict(orient="records")

    if not to_learn:
        # If there are no words to learn, create a new DataFrame from the default file
        df = pd.read_csv("data/1-GettingStarted.csv")
        to_learn = df.to_dict(orient="records")


# ---------------------------- LOAD SELECTED FILE CARD ------------------------------- #
# Define a function to load the selected file from the dropdown list
def load_selected_file():
    selected_file = selected_file_var.get()
    initialize_flashcards(f"data/{selected_file}")

    # Enable the "Wrong" and "Right" buttons
    button_wrong.config(state=NORMAL)
    button_right.config(state=NORMAL)

    next_card()


# ---------------------------- MARK WORD AS DIFFICULT ------------------------------- #
def mark_difficult_word():
    global current_card

    difficult_word = {
        "Malay": current_card["Malay"],
        "English": current_card["English"]
    }

    # Check if the '1-DifficultWords.csv' file exists
    if os.path.exists("data/1-DifficultWords.csv"):
        # Read existing difficult words from the file
        existing_data = pd.read_csv("data/1-DifficultWords.csv")
        # Create a DataFrame for the new difficult word
        new_data = pd.DataFrame([difficult_word])
        # Concatenate the existing data with the new difficult word
        updated_data = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        # If the file does not exist, create a new DataFrame with the new difficult word
        updated_data = pd.DataFrame([difficult_word])

    # Save the updated list of difficult words to the CSV file
    updated_data.to_csv("data/1-DifficultWords.csv", index=False)

    # Remove the word from the to_learn list
    to_learn.remove(current_card)
    data = pd.DataFrame(to_learn)
    data.to_csv("data/words_to_learn.csv", index=False)

    next_card()
    word_count_label.config(text=f"Words to Learn: {get_remaining_words_count()}")
    difficult_word_count_label.config(text=f"Difficult words: {get_difficult_words_count()}")


# ---------------------------- CLEAR DIFFICULT WORDS ------------------------------- #
def clear_difficult_words():
    try:
        os.remove("data/1-DifficultWords.csv")
    except FileNotFoundError:
        pass

    next_card()  # Load the next card after clearing difficult words

    # Update the difficult word count label
    difficult_word_count_label.config(text=f"Difficult words: {get_difficult_words_count()}")


# ---------------------------- GOOGLE TEXT TO SPEECH ------------------------------- #
# Initialize pygame mixer
pygame.mixer.init()


# Updated text_to_speech function to use pygame
def text_to_speech(text, manual=False):
    def play_sound():
        tts = gTTS(text, lang='ms')
        temp_file_path = "temp_audio.mp3"
        tts.save(temp_file_path)

        # Debugging
        # print("Saved audio to:", temp_file_path)
        #
        # if os.path.exists(temp_file_path):
        #     print("Audio file exists")
        # else:
        #     print("Audio file does not exist")
        #     return

        # Load and play sound using pygame
        pygame.mixer.music.load(temp_file_path)
        pygame.mixer.music.play()

        # Wait until the sound is finished playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        os.remove(temp_file_path)  # Remove the temporary file after playing

    # Run the sound playing function in a separate thread
    thread = Thread(target=play_sound)
    thread.start()


# ---------------------------- SHOW REMAINING WORDS ------------------------------- #
# Function to show the number of remaining words
def get_difficult_words_count():
    try:
        df = pd.read_csv("data/1-DifficultWords.csv")
        return len(df)
    except FileNotFoundError:
        return 0


# ---------------------------- SHOW REMAINING WORDS ------------------------------- #
# Function to show the number of remaining words
def get_remaining_words_count():
    try:
        df = pd.read_csv("data/words_to_learn.csv")
        return len(df)
    except FileNotFoundError:
        return 0


# ---------------------------- AUTO PRONOUNCE ------------------------------- #
# Function to toggle the "Auto-pronounce" feature
def toggle_auto_pronounce():
    global auto_pronounce
    auto_pronounce = auto_pronounce_var.get()


# ---------------------------- WORD IS KNOWN  ------------------------------- #
def is_known():
    global current_card
    if current_card in to_learn:
        to_learn.remove(current_card)
        data = pd.DataFrame(to_learn)
        data.to_csv("data/words_to_learn.csv", index=False)
        next_card()
        word_count_label.config(text=f"Words to Learn: {get_remaining_words_count()}")
        difficult_word_count_label.config(text=f"Difficult words: {get_difficult_words_count()}")
    else:
        # Handle the case when there are no more words to learn
        canvas.itemconfig(card_title, text="Done. Load new file or clear words to learn.")
        canvas.itemconfig(card_word, text="")
        button_right.config(state=DISABLED)  # Disable the "Right" button

        # Optionally, you can also disable the "Wrong" button in this case
        button_wrong.config(state=DISABLED)


# ---------------------------- TOGGLE DIRECTION ------------------------------- #
# In the "toggle_direction" function, update the "Auto-pronounce" state
def toggle_direction():
    global current_direction
    global auto_pronounce
    if current_direction == "malay_to_english":
        current_direction = "english_to_malay"
        button_direction.config(text="Switch to Malay to English")
        # Disable "Auto-pronounce" when the direction changes
        auto_pronounce = False
    else:
        current_direction = "malay_to_english"
        button_direction.config(text="Switch to English to Malay")


# ---------------------------- TOGGLE TRANSLATION  ------------------------------- #
def toggle_translation():
    if current_direction == "malay_to_english":
        if canvas.itemcget(card_title, "text") == "Malay":
            canvas.itemconfig(card_title, text="English")
            canvas.itemconfig(card_word, text=current_card["English"])
        else:
            canvas.itemconfig(card_title, text="Malay")
            canvas.itemconfig(card_word, text=current_card["Malay"])
    else:
        if canvas.itemcget(card_title, "text") == "English":
            canvas.itemconfig(card_title, text="Malay")
            canvas.itemconfig(card_word, text=current_card["Malay"])
        else:
            canvas.itemconfig(card_title, text="English")
            canvas.itemconfig(card_word, text=current_card["English"])


# ---------------------------- RESTART PROGRAM ------------------------------- #
def restart_program():
    try:
        os.remove("data/words_to_learn.csv")
    except FileNotFoundError:
        pass
    to_learn.clear()  # Clear the 'to_learn' dictionary
    initialize_flashcards(f"data/{selected_file_var.get()}")  # Load the selected file

    # Enable the "Wrong" and "Right" buttons
    button_wrong.config(state=NORMAL)
    button_right.config(state=NORMAL)

    next_card()  # Load the next card after restarting

    # Update the word count label
    word_count_label.config(text=f"Words to Learn: {get_remaining_words_count()}")

    # Update the difficult word count label
    difficult_word_count_label.config(text=f"Difficult words: {get_difficult_words_count()}")


# ---------------------------- FLIP CARD ------------------------------- #
# In the "flip_card" function, call the text_to_speech function for the Malay word only if "Auto Pronounce" is enabled
def flip_card():
    if current_direction == "malay_to_english":
        canvas.itemconfig(card_title, text="English", fill="white")
        canvas.itemconfig(card_word, text=current_card["English"], fill="white")

    else:
        canvas.itemconfig(card_title, text="Malay", fill="white")
        canvas.itemconfig(card_word, text=current_card["Malay"], fill="white")

    canvas.itemconfig(card_background, image=card_back_img)


# ---------------------------- NEXT CARD ------------------------------- #
# In the "next_card" function, call the text_to_speech function for the first card
def next_card():
    global current_card, flip_timer, pending_pronunciation
    root.after_cancel(flip_timer)

    if pending_pronunciation is not None:
        root.after_cancel(pending_pronunciation)

    text_to_speech.pronounced = False

    if to_learn:
        current_card = random.choice(to_learn)
        if current_direction == "malay_to_english":
            canvas.itemconfig(card_word, text=current_card["Malay"], fill="black")
            canvas.itemconfig(card_title, text="Malay", fill="black")
        else:
            canvas.itemconfig(card_word, text=current_card["English"], fill="black")
            canvas.itemconfig(card_title, text="English", fill="black")
        canvas.itemconfig(card_background, image=card_front_img)

        # Use the user-selected flip timer value
        flip_timer = root.after(int(flip_timer_scale.get()), func=flip_card)

        # Auto pronounce the Malay word if auto pronounce is enabled
        if auto_pronounce and current_direction == "malay_to_english":
            pending_pronunciation = root.after(100, lambda: text_to_speech(current_card["Malay"]))

    else:
        canvas.itemconfig(card_title, text="Done. Load new file or clear words to learn")
        canvas.itemconfig(card_word, text="")
        button_right.config(state=DISABLED)
        button_wrong.config(state=DISABLED)
        initialize_flashcards(f"data/{selected_file_var.get()}")


# ---------------------------- UI SETUP ------------------------------- #
root = Tk()
root.title("Flashcards: Learn Malay")
root.config(pady=20, bg="#B1DDC6", width=1300, height=600)

# Card FRONT
canvas = Canvas(width=900, height=600, bg="#B1DDC6")
card_front_img = PhotoImage(file="images/card_front.gif", width=800, height=526)
card_back_img = PhotoImage(file="images/card_back.gif", width=800, height=526)
card_background = canvas.create_image(450, 280, image=card_front_img)
card_title = canvas.create_text(450, 100, text="Title", font=("Arial", 25, "italic"))
card_word = canvas.create_text(450, 200, text="Word", font=("Arial", 30, "bold"), width=700)
canvas.config(bg="#B1DDC6", highlightthickness=0)
canvas.place(x=10, y=20)

# ---------------------------- BUTTONS FOR RIGHT AND WRONG AND DIFFICULT ------------------------------- #
# Button wrong
img_wrong = PhotoImage(file="images/wrong.gif")
button_wrong = Button(image=img_wrong, width=100, height=100, command=next_card)
button_wrong.place(x=320, y=360)

# Button right
img_right = PhotoImage(file="images/right.gif")
button_right = Button(image=img_right, width=100, height=100, command=is_known)
button_right.place(x=470, y=360)

# Button to mark the current word as difficult
button_difficult = Button(root, text="Mark as Difficult", font=("Arial", 13, "normal"), width=18,
                          command=mark_difficult_word)
button_difficult.place(x=340, y=480)

# ---------------------------- TOGGLE DIRECTION ------------------------------- #

# Button to toggle direction
button_direction = Button(root, text="Switch to English to Malay", font=("Arial", 15, "bold"), width=25,
                          command=toggle_direction)
button_direction.place(x=900, y=50)

# ---------------------------- TOGGLE TRANSLATION ------------------------------- #

# Button to toggle translation
button_toggle = Button(root, text="Toggle Translation", font=("Arial", 15, "bold"), width=25,
                       command=toggle_translation)
button_toggle.place(x=900, y=100)

# ---------------------------- GOOGLE TEXT TO SPEECH / PRONOUNCE ------------------------------- #

# Button for Google text to speech
pronounce_button = Button(root, text="Pronounce", font=("Arial", 14, "bold"), width=25,
                          command=lambda: text_to_speech(current_card["Malay"], manual=True))
pronounce_button.place(x=900, y=150)

# ---------------------------- FILE SELECTION DROPDOWN AND LOADING ------------------------------- #

# Add a dropdown list to select the file
available_files = os.listdir("data")
available_files.sort()  # Sort the list alphabetically
selected_file_var = StringVar(root)
selected_file_var.set("1-GettingStarted.csv")  # Default selection
file_dropdown = OptionMenu(root, selected_file_var, *available_files)
file_dropdown.configure(font=("Arial", 14, "normal"), width=25)  # Apply font and width styling
file_dropdown.place(x=900, y=220)

# Button to load the selected file
load_file_button = Button(root, text="Load selected File", font=("Arial", 14, "normal"), width=25,
                          command=load_selected_file)
load_file_button.place(x=900, y=265)

# ---------------------------- SET THE FLIP CARD TIMER ------------------------------- #

# Create a Scale widget to allow the user to set the flip_card timer.
flip_timer_scale = Scale(root, from_=3000, to=10000, orient=HORIZONTAL, length=200, resolution=100)
flip_timer_scale.set(3000)  # Set the default value
flip_timer_scale.place(x=900, y=320)  # Adjust the placement according to your UI

# Update the flip_timer initialization to use the scale value
flip_timer = root.after(int(flip_timer_scale.get()), func=flip_card)

# ---------------------------- SEE HOW MANY DIFFICULT WORDS REMAINING ------------------------------- #

# Show how many words remain in words to learn list
difficult_word_count_label = Label(root, text=f"Difficult words: {get_difficult_words_count()}", font=("Arial", 14))
difficult_word_count_label.place(x=900, y=395)

# ---------------------------- SEE HOW MANY WORDS REMAINING ------------------------------- #

# Show how many words remain in words to learn list
word_count_label = Label(root, text=f"Words to Learn: {get_remaining_words_count()}", font=("Arial", 14))
word_count_label.place(x=900, y=420)

# ---------------------------- BUTTON TO CLEAR DIFFICULT WORDS LIST ------------------------------- #

# Button to restart the program
button_clear_difficult_words = Button(root, text="Clear difficult words", font=("Arial", 15, "normal"), width=25,
                                      command=clear_difficult_words)
button_clear_difficult_words.place(x=900, y=490)

# ---------------------------- RESTART PROGRAM / CLEAR WORDS TO LEARN ------------------------------- #

# Button to restart the program
button_restart = Button(root, text="Clear words to learn", font=("Arial", 15, "normal"), width=25,
                        command=restart_program)
button_restart.place(x=900, y=450)

# ---------------------------- AUTO PRONOUNCE CHECK BUTTON ------------------------------- #

# Create a BooleanVar to track the state of Auto Pronounce
auto_pronounce_var = BooleanVar()
auto_pronounce_var.set(auto_pronounce)  # Initialize the state

# Create a style for the Auto pronounce checkbox button
style = ttk.Style()
style.configure("TCheckbutton", font=("Arial", 13))
# Replace the "Toggle button for Auto-pronounce" section
auto_pronounce_switch = ttk.Checkbutton(root, text="Auto Pronounce", variable=auto_pronounce_var,
                                        command=toggle_auto_pronounce)
auto_pronounce_switch.place(x=900, y=189)

# ---------------------------- LOAD THE PROGRAM ------------------------------- #

# Call this at the beginning of the script to initialize flashcards with a default file
initialize_flashcards("data/words_to_learn.csv")

next_card()

root.mainloop()
