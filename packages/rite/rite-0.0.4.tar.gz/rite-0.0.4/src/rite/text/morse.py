# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Provides Morse Class
====================

Todo:
-----

Links:
------

"""


# =============================================================================
# Import
# =============================================================================

# Import | Standard Library
import random

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Classes
# =============================================================================


class Morse(object):
    """
    Morse Class
    ==========

    """

    @staticmethod
    def to_morse_code(text: str) -> str:
        """
        Convert the text to Morse code.
        Example: 'HELP' -> '.... . .-.. .--.'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text in Morse code.
        """
        morse_dict = {
            "A": ".-",
            "B": "-...",
            "C": "-.-.",
            "D": "-..",
            "E": ".",
            "F": "..-.",
            "G": "--.",
            "H": "....",
            "I": "..",
            "J": ".---",
            "K": "-.-",
            "L": ".-..",
            "M": "--",
            "N": "-.",
            "O": "---",
            "P": ".--.",
            "Q": "--.-",
            "R": ".-.",
            "S": "...",
            "T": "-",
            "U": "..-",
            "V": "...-",
            "W": ".--",
            "X": "-..-",
            "Y": "-.--",
            "Z": "--..",
            " ": "/",
        }
        return " ".join(morse_dict.get(char.upper(), "") for char in text)

    @staticmethod
    def to_morse_code_decryption(text: str) -> str:
        """
        Decode Morse code back into text.
        Example: '.... . .-.. .-.. ---' -> 'HELLO'

        Parameters:
        text (str): The Morse code to decode.

        Returns:
        str: The decoded text.
        """
        morse_dict = {
            ".-": "A",
            "-...": "B",
            "-.-.": "C",
            "-..": "D",
            ".": "E",
            "..-.": "F",
            "--.": "G",
            "....": "H",
            "..": "I",
            ".---": "J",
            "-.-": "K",
            ".-..": "L",
            "--": "M",
            "-.": "N",
            "---": "O",
            ".--.": "P",
            "--.-": "Q",
            ".-.": "R",
            "...": "S",
            "-": "T",
            "..-": "U",
            "...-": "V",
            ".--": "W",
            "-..-": "X",
            "-.--": "Y",
            "--..": "Z",
            "/": " ",
        }
        return "".join(morse_dict.get(code, "") for code in text.split(" "))

    @staticmethod
    def to_morse_code_wordwise(text: str) -> str:
        """
        Converts each word to Morse code, maintaining word boundaries.
        Example: 'Hi' -> '.... ..'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text with each word converted to Morse code.
        """
        morse_dict = {
            "A": ".-",
            "B": "-...",
            "C": "-.-.",
            "D": "-..",
            "E": ".",
            "F": "..-.",
            "G": "--.",
            "H": "....",
            "I": "..",
            "J": ".---",
            "K": "-.-",
            "L": ".-..",
            "M": "--",
            "N": "-.",
            "O": "---",
            "P": ".--.",
            "Q": "--.-",
            "R": ".-.",
            "S": "...",
            "T": "-",
            "U": "..-",
            "V": "...-",
            "W": ".--",
            "X": "-..-",
            "Y": "-.--",
            "Z": "--..",
            " ": "/",
        }
        return " / ".join(
            " ".join(morse_dict.get(char.upper(), "") for char in word)
            for word in text.split()
        )


# =============================================================================
# Functions
# =============================================================================


def test():
    """
    Test Function
    """

    morse_code = Morse.to_morse_code("SOS")
    morse_code_decryption = Morse.to_morse_code_decryption(
        ".... . .-.. .-.. ---"
    )
    morse_code_wordwise = Morse.to_morse_code_wordwise("Hi")

    print("Morse Code Morse:", morse_code)
    print("Morse Code Decryption Morse:", morse_code_decryption)
    print("Morse Code Wordwise Morse:", morse_code_wordwise)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    """Main"""
    import doctest

    doctest.testmod()
    test()
