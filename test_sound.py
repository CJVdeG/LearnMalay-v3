# from playsound import playsound
#
# def test_sound():
#     test_file = "test_audio.mp3"  # Replace with a valid mp3 file path
#     playsound(test_file)
#
# if __name__ == "__main__":
#     test_sound()

import pygame


def test_sound():
    pygame.mixer.init()
    pygame.mixer.music.load("test_audio.mp3")  # Replace with the path to your mp3 file
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)  # Wait until the audio finishes


if __name__ == "__main__":
    test_sound()