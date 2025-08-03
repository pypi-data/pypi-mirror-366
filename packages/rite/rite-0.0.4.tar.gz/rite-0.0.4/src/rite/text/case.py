# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Provides Case Class
===================

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


class Case(object):
    """
    Case Class
    ==========

    """

    def to_camel_case(text: str) -> str:
        """
        Convert the text to camel case.
        Example: 'hello world' -> 'helloWorld'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text converted to camel case.
        """
        words = text.split()
        return words[0].lower() + "".join(
            word.capitalize() for word in words[1:]
        )  # noqa E501

    @staticmethod
    def to_snake_case(text: str) -> str:
        """
        Convert the text to snake case.
        Example: 'Hello World' -> 'hello_world'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text converted to snake case.
        """
        words = text.split()
        return "_".join(word.lower() for word in words)

    @staticmethod
    def to_kebab_case(text: str) -> str:
        """
        Convert the text to kebab case (similar to spinal case).
        Lowers the case of each word and joins them with hyphens.
        Example: 'Hello World' -> 'hello-world'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text converted to kebab case.
        """
        words = text.split()
        return "-".join(word.lower() for word in words)

    @staticmethod
    def to_spinal_case(text: str) -> str:
        """
        Convert the text to spinal case (similar to kebab case).
        Lowers the case of each word and joins them with hyphens.
        Example: 'Hello World' -> 'hello-world'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text converted to spinal case.
        """
        words = text.split()
        return "-".join(word.lower() for word in words)

    @staticmethod
    def to_title_case(text: str) -> str:
        """
        Convert the text to title case.
        Example: 'hello world' -> 'Hello World'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text converted to title case.
        """
        return text.title()

    @staticmethod
    def to_upper_case(text: str) -> str:
        """
        Convert the text to upper case.
        Example: 'hello world' -> 'HELLO WORLD'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text converted to upper case.
        """
        return text.upper()

    @staticmethod
    def to_lower_case(text: str) -> str:
        """
        Convert the text to lower case.
        Example: 'Hello World' -> 'hello world'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text converted to lower case.
        """
        return text.lower()

    @staticmethod
    def to_sentence_case(text: str) -> str:
        """
        Convert the text to sentence case.
        Example: 'hello world. it's a test' -> 'Hello world. It's a test'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text converted to sentence case.
        """
        sentences = text.split(". ")
        return ". ".join(sentence.capitalize() for sentence in sentences)

    @staticmethod
    def to_constant_case(text: str) -> str:
        """
        Convert the text to constant case.
        Capitalizes each word and joins them with underscores, creating
        a format commonly used for constants.
        Example: 'Hello World' -> 'HELLO_WORLD'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text converted to constant case.
        """
        words = text.split()
        return "_".join(word.upper() for word in words)

    @staticmethod
    def to_pascal_case(text: str) -> str:
        """
        Convert the text to pascal case.
        Similar to camel case, but the first letter of each word is
        capitalized.
        Example: 'hello world' -> 'HelloWorld'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text converted to pascal case.
        """
        words = text.split()
        return "".join(word.capitalize() for word in words)

    @staticmethod
    def to_dot_case(text: str) -> str:
        """
        Convert the text to dot case.
        Words are separated by dots.
        Example: 'Hello World' -> 'hello.world'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text converted to dot case.
        """
        words = text.split()
        return ".".join(word.lower() for word in words)

    @staticmethod
    def to_path_case(text: str) -> str:
        """
        Convert the text to path case.
        Words are separated by forward slashes, similar to a file path.
        Example: 'Hello World' -> 'hello/world'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text converted to path case.
        """
        words = text.split()
        return "/".join(word.lower() for word in words)

    @staticmethod
    def to_reverse_case(text: str) -> str:
        """
        Reverse the text.
        Reverses the order of characters in the text.
        Example: 'Hello World' -> 'dlroW olleH'

        Parameters:
        text (str): The text to reverse.

        Returns:
        str: The reversed text.
        """
        return text[::-1]

    @staticmethod
    def to_swap_case(text: str) -> str:
        """
        Swap the case of each character in the text.
        Example: 'Hello World' -> 'hELLO wORLD'

        Parameters:
        text (str): The text whose case is to be swapped.

        Returns:
        str: The text with swapped case.
        """
        return text.swapcase()

    @staticmethod
    def to_random_case(text: str) -> str:
        """
        Randomly change the case of each character in the text.
        Example: 'Hello World' -> 'hElLO wOrLD'

        Parameters:
        text (str): The text to randomize case.

        Returns:
        str: The text with randomized case.
        """
        return "".join(
            random.choice([char.upper(), char.lower()]) for char in text
        )  # noqa E501

    @staticmethod
    def to_slug_case(text: str) -> str:
        """
        Convert the text to slug case (URL-friendly format).
        Example: 'Hello World' -> 'hello-world'

        Parameters:
        text (str): The text to convert to slug case.

        Returns:
        str: The text in slug case.
        """
        words = text.split()
        return "-".join(word.lower() for word in words)

    @staticmethod
    def to_mocking_spongebob_case(text: str) -> str:
        """
        Convert the text to 'Mocking Spongebob' case (alternating case).
        Example: 'Hello World' -> 'hElLo wOrLd'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text in 'Mocking Spongebob' case.
        """
        return "".join(
            char.lower() if i % 2 else char.upper()
            for i, char in enumerate(text)
        )  # noqa E501

    @staticmethod
    def to_vowel_uppercase_case(text: str) -> str:
        """
        Convert all vowels in the text to uppercase.
        Example: 'Hello World' -> 'HEllO WOrld'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text with uppercase vowels.
        """
        vowels = "aeiou"
        return "".join(
            char.upper() if char.lower() in vowels else char for char in text
        )  # noqa E501

    @staticmethod
    def to_consonant_uppercase_case(text: str) -> str:
        """
        Convert all consonants in the text to uppercase.
        Example: 'Hello World' -> 'hEllO wOrld'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text with uppercase consonants.
        """
        vowels = "aeiou"
        return "".join(
            char.upper() if char.lower() not in vowels else char
            for char in text
        )  # noqa E501

    @staticmethod
    def to_leet_speak_case(text: str) -> str:
        """
        Convert the text to leet speak (1337) case.
        Example: 'Leet Speak' -> '1337 5p34k'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text in leet speak.
        """
        leet_dict = {
            "a": "4",
            "e": "3",
            "l": "1",
            "o": "0",
            "s": "5",
            "t": "7",
            "i": "1",
            "g": "9",
        }
        return "".join(leet_dict.get(char.lower(), char) for char in text)

    @staticmethod
    def to_first_letter_uppercase_case(text: str) -> str:
        """
        Convert only the first letter of each word in the text to uppercase,
        the rest to lowercase.
        Example: 'hello world' -> 'Hello World'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text with the first letter of each word in uppercase.
        """
        return " ".join(
            word[0].upper() + word[1:].lower() if word else ""
            for word in text.split()
        )  # noqa E501

    @staticmethod
    def to_backwards_words_case(text: str) -> str:
        """
        Reverse the order of characters in each word of the text.
        Example: 'Hello World' -> 'olleH dlroW'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text with each word reversed.
        """
        return " ".join(word[::-1] for word in text.split())

    @staticmethod
    def to_alternate_uppercase_lowercase_case(text: str) -> str:
        """
        Alternates between uppercase and lowercase starting from the second
        character.
        Example: 'hello world' -> 'hElLo WoRlD'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text with alternating uppercase and lowercase letters.
        """
        return "".join(
            char.upper() if i % 2 else char.lower()
            for i, char in enumerate(text)
        )  # noqa E501

    @staticmethod
    def to_nato_phonetic_alphabet_case(text: str) -> str:
        """
        Translates each letter to its corresponding NATO phonetic alphabet
        word.
        Example: 'AB' -> 'Alpha Bravo'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text in NATO phonetic alphabet.
        """
        nato_dict = {
            "A": "Alpha",
            "B": "Bravo",
            "C": "Charlie",
            "D": "Delta",
            "E": "Echo",
            "F": "Foxtrot",
            "G": "Golf",
            "H": "Hotel",
            "I": "India",
            "J": "Juliett",
            "K": "Kilo",
            "L": "Lima",
            "M": "Mike",
            "N": "November",
            "O": "Oscar",
            "P": "Papa",
            "Q": "Quebec",
            "R": "Romeo",
            "S": "Sierra",
            "T": "Tango",
            "U": "Uniform",
            "V": "Victor",
            "W": "Whiskey",
            "X": "X-ray",
            "Y": "Yankee",
            "Z": "Zulu",
            " ": " ",
        }
        return " ".join(nato_dict.get(char.upper(), "") for char in text)

    @staticmethod
    def to_binary_case(text: str) -> str:
        """
        Convert the text to binary form.
        Example: 'AB' -> '01000001 01000010'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text in binary form.
        """
        return " ".join(format(ord(char), "08b") for char in text)

    @staticmethod
    def to_hexadecimal_case(text: str) -> str:
        """
        Convert the text to hexadecimal form.
        Example: 'AB' -> '41 42'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text in hexadecimal form.
        """
        return " ".join(format(ord(char), "x") for char in text)

    @staticmethod
    def to_upside_down_case(text: str) -> str:
        """
        Flips the text upside down.
        Note: This method uses a limited character set for flipping.

        Parameters:
        text (str): The text to flip.

        Returns:
        str: The flipped text.
        """
        flip_dict = {
            "a": "ɐ",
            "b": "q",
            "c": "ɔ",
            "d": "p",
            "e": "ǝ",
            "f": "ɟ",
            "g": "ƃ",
            "h": "ɥ",
            "i": "ᴉ",
            "j": "ɾ",
            "k": "ʞ",
            "l": "l",
            "m": "ɯ",
            "n": "u",
            "o": "o",
            "p": "d",
            "q": "b",
            "r": "ɹ",
            "s": "s",
            "t": "ʇ",
            "u": "n",
            "v": "ʌ",
            "w": "ʍ",
            "x": "x",
            "y": "ʎ",
            "z": "z",
            "A": "∀",
            "B": "𐐒",
            "C": "Ɔ",
            "D": "ᗡ",
            "E": "Ǝ",
            "F": "Ⅎ",
            "G": "⅁",
            "H": "H",
            "I": "I",
            "J": "ſ",
            "K": "⋊",
            "L": "˥",
            "M": "W",
            "N": "N",
            "O": "O",
            "P": "Ԁ",
            "Q": "Q",
            "R": "ᴚ",
            "S": "S",
            "T": "⊥",
            "U": "∩",
            "V": "Λ",
            "W": "M",
            "X": "X",
            "Y": "⅄",
            "Z": "Z",
            "1": "Ɩ",
            "2": "ᄅ",
            "3": "Ɛ",
            "4": "ㄣ",
            "5": "ϛ",
            "6": "9",
            "7": "ㄥ",
            "8": "8",
            "9": "6",
            "0": "0",
            ".": "˙",
            ",": "'",
            "?": "¿",
            "!": "¡",
            '"': "„",
            "'": ",",
            "(": ")",
            ")": "(",
            "[": "]",
            "]": "[",
            "{": "}",
            "}": "{",
            "<": ">",
            ">": "<",
            "&": "⅋",
            "_": "‾",
            ";": "؛",
            ":": "∶",
            "-": "-",
            "+": "⁺",
            "=": "⁼",
            "/": "\\",
            "\\": "/",
            "|": "|",
            "@": "@",
            "#": "#",
            "$": "$",
            "%": "%",
            "^": "︿",
            "&": "⅋",
            "*": "*",
            "~": "~",
        }
        return "".join(flip_dict.get(char, char) for char in reversed(text))

    @staticmethod
    def to_emoji_case(text: str) -> str:
        """
        Replace certain words with corresponding emojis.
        Note: This is a limited implementation; only a few words are replaced.

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text with words replaced by emojis.
        """
        emoji_dict = {
            "love": "❤️",
            "happy": "😊",
            "sad": "😢",
            "dog": "🐶",
            "cat": "🐱",
            "tree": "🌳",
        }
        return " ".join(emoji_dict.get(word, word) for word in text.split())

    @staticmethod
    def to_zalgo_text_case(text: str) -> str:
        """
        Add a glitch-like effect to the text with Zalgo characters.
        Note: This is a simplified version for demonstration.

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text with Zalgo effect.
        """
        zalgo_chars = [chr(i) for i in range(0x0300, 0x036F)]
        return "".join(
            char + "".join(random.choices(zalgo_chars, k=2)) for char in text
        )  # noqa E501

    @staticmethod
    def to_inverted_case(text: str) -> str:
        """
        Invert the case of each letter in the text.

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text with inverted case.
        """
        return "".join(
            char.upper() if char.islower() else char.lower() for char in text
        )  # noqa E501

    @staticmethod
    def to_rainbow_case(text: str) -> str:
        """
        Assigns a different color code to each letter.
        Note: Actual color cannot be represented in plain text; using symbolic
        representation.

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text with symbolic color codes.
        """
        colors = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪"]
        return "".join(
            f"{colors[i % len(colors)]}{char}" for i, char in enumerate(text)
        )  # noqa E501

    @staticmethod
    def to_acronym_case(text: str) -> str:
        """
        Convert a phrase to its acronym.
        Example: 'Random Access Memory' -> 'RAM'

        Parameters:
        text (str): The phrase to convert.

        Returns:
        str: The acronym of the phrase.
        """
        return "".join(word[0].upper() for word in text.split() if word)

    @staticmethod
    def to_spongebob_meme_case(text: str) -> str:
        """
        Alternates the case of each letter in a mocking manner, starting with
        uppercase.
        Example: 'spongebob case' -> 'SpOnGeBoB cAsE'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text in Spongebob Meme case.
        """
        return "".join(
            char.upper() if i % 2 else char.lower()
            for i, char in enumerate(text)
        )  # noqa E501

    @staticmethod
    def to_reversed_sentence_case(text: str) -> str:
        """
        Reverses the order of words in a sentence.
        Example: 'Hello world' -> 'world Hello'

        Parameters:
        text (str): The sentence to reverse.

        Returns:
        str: The sentence with reversed word order.
        """
        return " ".join(reversed(text.split()))

    @staticmethod
    def to_pig_latin_case(text: str) -> str:
        """
        Translates text into Pig Latin.
        Example: 'hello' -> 'ellohay'

        Parameters:
        text (str): The text to translate.

        Returns:
        str: The text in Pig Latin.
        """

        def convert_word(word):
            if word[0] in "aeiou":
                return word + "way"
            return word[1:] + word[0] + "ay"

        return " ".join(convert_word(word) for word in text.split())

    @staticmethod
    def to_reverse_words_case(text: str) -> str:
        """
        Reverse each individual word in the text.
        Example: 'Hello World' -> 'olleH dlroW'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text with each word reversed.
        """
        return " ".join(word[::-1] for word in text.split())

    @staticmethod
    def to_random_shuffle_case(text: str) -> str:
        """
        Randomly shuffle the letters in each word of the text.
        Example: 'hello' -> 'lleoh' (output may vary)

        Parameters:
        text (str): The text to shuffle.

        Returns:
        str: The text with letters in each word shuffled.
        """

        def shuffle_word(word):
            word_list = list(word)
            random.shuffle(word_list)
            return "".join(word_list)

        return " ".join(shuffle_word(word) for word in text.split())

    @staticmethod
    def to_vowel_removal_case(text: str) -> str:
        """
        Remove all vowels from the text.
        Example: 'Hello World' -> 'Hll Wrld'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text with all vowels removed.
        """
        vowels = "aeiouAEIOU"
        return "".join(char for char in text if char not in vowels)

    @staticmethod
    def to_first_letter_of_each_word_case(text: str) -> str:
        """
        Takes the first letter of each word to form a new string.
        Example: 'Hello World' -> 'HW'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: A string formed by the first letter of each word.
        """
        return "".join(word[0] for word in text.split() if word)

    @staticmethod
    def to_scramble_middle_letters_case(text: str) -> str:
        """
        Scrambles the middle letters of each word, keeping the first and last
        letter intact.
        Example: 'Hello' -> 'Hlelo' (output may vary)

        Parameters:
        text (str): The text to scramble.

        Returns:
        str: The text with middle letters of each word scrambled.
        """

        def scramble_middle(word):
            if len(word) > 3:
                middle = list(word[1:-1])
                random.shuffle(middle)
                return word[0] + "".join(middle) + word[-1]
            return word

        return " ".join(scramble_middle(word) for word in text.split())

    @staticmethod
    def to_ascii_value_case(text: str) -> str:
        """
        Converts each character to its ASCII value.
        Example: 'AB' -> '65 66'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: A string of ASCII values for each character.
        """
        return " ".join(str(ord(char)) for char in text)

    @staticmethod
    def to_repeated_letters_case(text: str) -> str:
        """
        Repeats each letter in the word based on its position.
        Example: 'Hello' -> 'Heelllllooooo'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text with each letter repeated based on its position.
        """
        return " ".join(
            "".join(char * (i + 1) for i, char in enumerate(word))
            for word in text.split()
        )  # noqa E501

    @staticmethod
    def to_numeric_words_to_numbers_case(text: str) -> str:
        """
        Converts numeric words to their numeral equivalents.
        Example: 'one two three' -> '1 2 3'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text with numeric words converted to numbers.
        """
        num_dict = {
            "one": "1",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "eight": "8",
            "nine": "9",
            "zero": "0",
        }
        return " ".join(num_dict.get(word, word) for word in text.split())

    @staticmethod
    def to_reverse_each_vowel_case(text: str) -> str:
        """
        Reverses the order of vowels in each word.
        Example: 'Hello' -> 'Holle'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text with vowels in each word reversed.
        """
        vowels = "aeiouAEIOU"

        def reverse_vowels(word):
            vowel_list = [char for char in word if char in vowels]
            return "".join(
                vowel_list.pop() if char in vowels else char for char in word
            )

        return " ".join(reverse_vowels(word) for word in text.split())

    @staticmethod
    def to_vowel_concatenation_case(text: str) -> str:
        """
        Concatenates all vowels from the text.
        Example: 'Hello World' -> 'eoo'

        Parameters:
        text (str): The text to process.

        Returns:
        str: A string of all vowels concatenated.
        """
        vowels = "aeiouAEIOU"
        return "".join(char for char in text if char in vowels)

    @staticmethod
    def to_diagonal_text_case(text: str) -> str:
        """
        Creates a diagonal representation of the text.
        Note: This is a symbolic representation.
        Example: 'Hello' -> 'H\n e\n  l\n   l\n    o'

        Parameters:
        text (str): The text to convert.

        Returns:
        str: The text in a diagonal representation.
        """
        return "\n".join(" " * i + char for i, char in enumerate(text))

    @staticmethod
    def to_braille_transcription_case(text: str) -> str:
        """
        Transcribes text into simulated Braille.
        Note: This is a highly simplified and symbolic representation.

        Parameters:
        text (str): The text to transcribe.

        Returns:
        str: The text transcribed into simulated Braille.
        """
        # Placeholder implementation; real Braille transcription is more complex
        return "Braille: " + text

    @staticmethod
    def to_palindrome_check_case(text: str) -> bool:
        """
        Checks if the text is a palindrome.
        Example: 'racecar' -> True

        Parameters:
        text (str): The text to check.

        Returns:
        bool: True if the text is a palindrome, False otherwise.
        """
        cleaned_text = "".join(char.lower() for char in text if char.isalnum())
        return cleaned_text == cleaned_text[::-1]

    @staticmethod
    def to_interleave_words_case(text1: str, text2: str) -> str:
        """
        Interleaves two different strings word by word.
        Example: ('abc def', 'ghi jkl') -> 'abc ghi def jkl'

        Parameters:
        text1 (str): The first text to interleave.
        text2 (str): The second text to interleave.

        Returns:
        str: The interleaved text.
        """
        words1 = text1.split()
        words2 = text2.split()
        interleaved = [val for pair in zip(words1, words2) for val in pair]
        interleaved.extend(words1[len(words2) :] or words2[len(words1) :])
        return " ".join(interleaved)

    @staticmethod
    def to_alternate_character_deletion_case(text: str) -> str:
        """
        Deletes every alternate character in the text.
        Example: 'Hello' -> 'Hlo'

        Parameters:
        text (str): The text to process.

        Returns:
        str: The text with every alternate character deleted.
        """
        return text[::2]

    @staticmethod
    def to_numeronym_case(text: str) -> str:
        """
        Converts a word into a numeronym.
        Example: 'Internationalization' -> 'i18n'

        Parameters:
        text (str): The word to convert.

        Returns:
        str: The word converted into a numeronym.
        """
        if len(text) <= 3:
            return text
        return text[0] + str(len(text) - 2) + text[-1]

    @staticmethod
    def to_word_count_case(text: str) -> int:
        """
        Counts the number of words in the text.
        Example: 'Hello world' -> 2

        Parameters:
        text (str): The text to count words in.

        Returns:
        int: The number of words in the text.
        """
        return len(text.split())

    @staticmethod
    def to_reverse_word_order_case(text: str) -> str:
        """
        Reverses the order of words in the text.
        Example: 'Hello world' -> 'world Hello'

        Parameters:
        text (str): The text to reverse word order.

        Returns:
        str: The text with reversed word order.
        """
        return " ".join(reversed(text.split()))

    @staticmethod
    def to_alphabet_position_case(text: str) -> str:
        """
        Replaces each letter with its position in the alphabet.
        Example: 'ab' -> '1 2'

        Parameters:
        text (str): The text to process.

        Returns:
        str: A string with each letter replaced by its alphabet position.
        """
        return " ".join(
            str(ord(char.lower()) - 96) for char in text if char.isalpha()
        )

    @staticmethod
    def to_double_every_second_word_case(text: str) -> str:
        """
        Doubles every second word in the text.
        Example: 'Hello world program' -> 'Hello Hello world world program
        program'

        Parameters:
        text (str): The text to process.

        Returns:
        str: The text with every second word doubled.
        """
        words = text.split()
        return " ".join(
            word if i % 2 == 0 else word + " " + word
            for i, word in enumerate(words)
        )

    @staticmethod
    def to_longest_word_case(text: str) -> str:
        """
        Finds the longest word in the text.
        Example: 'This is a test' -> 'test'

        Parameters:
        text (str): The text to search.

        Returns:
        str: The longest word in the text.
        """
        return max(text.split(), key=len)

    @staticmethod
    def to_character_frequency_count_case(text: str) -> dict:
        """
        Counts the frequency of each character in the text.
        Example: 'hello' -> {'h': 1, 'e': 1, 'l': 2, 'o': 1}

        Parameters:
        text (str): The text to analyze.

        Returns:
        dict: A dictionary with the frequency count of each character.
        """
        return dict(Counter(text))

    @staticmethod
    def to_reverse_words_individually_case(text: str) -> str:
        """
        Reverses each word in the text individually.
        Example: 'Hello world' -> 'olleH dlrow'

        Parameters:
        text (str): The text to reverse.

        Returns:
        str: The text with each word reversed individually.
        """
        return " ".join(word[::-1] for word in text.split())

    @staticmethod
    def to_substitute_numbers_with_words_case(text: str) -> str:
        """
        Replaces numbers in the text with their word equivalents.
        Example: 'I have 2 dogs and 3 cats' -> 'I have two dogs and three cats'

        Parameters:
        text (str): The text to process.

        Returns:
        str: The text with numbers replaced by words.
        """
        num_to_word_dict = {
            "0": "zero",
            "1": "one",
            "2": "two",
            "3": "three",
            "4": "four",
            "5": "five",
            "6": "six",
            "7": "seven",
            "8": "eight",
            "9": "nine",
        }
        return " ".join(
            num_to_word_dict.get(word, word) for word in text.split()
        )

    @staticmethod
    def to_abbreviation_case(text: str) -> str:
        """
        Converts text to its abbreviation.
        Example: 'As Soon As Possible' -> 'ASAP'

        Parameters:
        text (str): The text to abbreviate.

        Returns:
        str: The abbreviation of the text.
        """
        return "".join(
            word[0].upper() for word in text.split() if word.isalpha()
        )

    @staticmethod
    def to_shuffle_sentences_case(text: str) -> str:
        """
        Randomly shuffles the sentences in the text.
        Example: 'This is sentence one. This is sentence two.' -> 'This is sentence two. This is sentence one.'

        Parameters:
        text (str): The text to shuffle.

        Returns:
        str: The text with shuffled sentences.
        """
        sentences = text.split(". ")
        random.shuffle(sentences)
        return ". ".join(sentences)

    @staticmethod
    def to_mirror_text_case(text: str) -> str:
        """
        Creates a mirrored version of the text.
        Example: 'Hello' -> 'Hello olleH'

        Parameters:
        text (str): The text to mirror.

        Returns:
        str: The mirrored text.
        """
        return text + " " + text[::-1]

    @staticmethod
    def to_insert_random_spaces_case(text: str) -> str:
        """
        Inserts random spaces within the text.
        Example: 'Hello' -> 'H e l l o' (output may vary)

        Parameters:
        text (str): The text to process.

        Returns:
        str: The text with random spaces inserted.
        """
        return " ".join(" ".join(char) for char in text)


# =============================================================================
# Functions
# =============================================================================


def test():
    """
    Test Function
    """

    # Example usage:
    text = "example TEXT for Conversion. it's a test"

    camel_case = Case.to_camel_case(text)
    snake_case = Case.to_snake_case(text)
    kebab_case = Case.to_kebab_case(text)
    spinal_case = Case.to_spinal_case(text)
    title_case = Case.to_title_case(text)
    upper_case = Case.to_upper_case(text)
    lower_case = Case.to_lower_case(text)
    sentence_case = Case.to_sentence_case(text)
    constant_case = Case.to_constant_case(text)
    pascal_case = Case.to_pascal_case(text)
    dot_case = Case.to_dot_case(text)
    path_case = Case.to_path_case(text)
    reverse_case = Case.to_reverse_case(text)
    swap_case = Case.to_swap_case(text)
    random_case = Case.to_random_case(text)
    slug_case = Case.to_slug_case(text)
    mocking_spongebob_case = Case.to_mocking_spongebob_case(text)
    vowel_uppercase_case = Case.to_vowel_uppercase_case(text)
    consonant_uppercase_case = Case.to_consonant_uppercase_case(text)
    leet_speak_case = Case.to_leet_speak_case(text)
    first_letter_uppercase_case = Case.to_first_letter_uppercase_case(text)
    backwards_words_case = Case.to_backwards_words_case(text)
    alternate_case = Case.to_alternate_uppercase_lowercase_case(text)
    nato_case = Case.to_nato_phonetic_alphabet_case("ABCD")
    binary_case = Case.to_binary_case(text)
    hexadecimal_case = Case.to_hexadecimal_case(text)
    upside_down_case = Case.to_upside_down_case(text)
    emoji_case = Case.to_emoji_case(text)
    zalgo_text_case = Case.to_zalgo_text_case("Zalgo")
    inverted_case = Case.to_inverted_case(text)
    rainbow_case = Case.to_rainbow_case("Rainbow")
    acronym_case = Case.to_acronym_case("Central Processing Unit")
    spongebob_meme_case = Case.to_spongebob_meme_case("spongebob case")
    reversed_sentence_case = Case.to_reversed_sentence_case(text)
    pig_latin_case = Case.to_pig_latin_case("hello")
    reverse_words_case = Case.to_reverse_words_case(text)
    random_shuffle_case = Case.to_random_shuffle_case(text)
    vowel_removal_case = Case.to_vowel_removal_case(text)
    first_letter_of_each_word_case = Case.to_first_letter_of_each_word_case(
        text
    )
    scramble_middle_letters_case = Case.to_scramble_middle_letters_case(text)
    ascii_value_case = Case.to_ascii_value_case("AB")
    repeated_letters_case = Case.to_repeated_letters_case("Hello")
    numeric_words_to_numbers_case = Case.to_numeric_words_to_numbers_case(text)
    reverse_each_vowel_case = Case.to_reverse_each_vowel_case("Hello")
    vowel_concatenation_case = Case.to_vowel_concatenation_case(text)
    diagonal_text_case = Case.to_diagonal_text_case("Hello")
    braille_transcription_case = Case.to_braille_transcription_case("Hello")
    palindrome_check = Case.to_palindrome_check_case(text)
    # interleaved_text = Case.to_interleave_words_case(text1, text2)
    alternate_character_deletion = Case.to_alternate_character_deletion_case(
        "Hello"
    )
    numeronym = Case.to_numeronym_case("Internationalization")
    word_count = Case.to_word_count_case(text)
    reversed_word_order = Case.to_reverse_word_order_case(text)
    alphabet_position = Case.to_alphabet_position_case("ab")
    double_every_second_word = Case.to_double_every_second_word_case(text)
    longest_word = Case.to_longest_word_case("This is a test")
    character_frequency_count = Case.to_character_frequency_count_case("hello")
    reverse_words_individually = Case.to_reverse_words_individually_case(
        "Hello world"
    )
    substitute_numbers_with_words = Case.to_substitute_numbers_with_words_case(
        text
    )
    abbreviation = Case.to_abbreviation_case(text)
    shuffled_sentences = Case.to_shuffle_sentences_case(
        "This is sentence one. This is sentence two."
    )
    mirror_text = Case.to_mirror_text_case("Hello")
    insert_random_spaces = Case.to_insert_random_spaces_case("Hello")

    print("Camel Case:", camel_case)
    print("Snake Case:", snake_case)
    print("Kebab Case:", kebab_case)
    print("Spinal Case:", spinal_case)
    print("Title Case:", title_case)
    print("Upper Case:", upper_case)
    print("Lower Case:", lower_case)
    print("Sentence Case:", sentence_case)
    print("Constant Case:", constant_case)
    print("Pascal Case:", pascal_case)
    print("Dot Case:", dot_case)
    print("Path Case:", path_case)
    print("Reverse Case:", reverse_case)
    print("Swap Case:", swap_case)
    print("Random Case:", random_case)
    print("Slug Case:", slug_case)
    print("Mocking Spongebob Case:", mocking_spongebob_case)
    print("Vowel Uppercase Case:", vowel_uppercase_case)
    print("Consonant Uppercase Case:", consonant_uppercase_case)
    print("Leet Speak Case:", leet_speak_case)
    print("First Letter Uppercase Case:", first_letter_uppercase_case)
    print("Backwards Words Case:", backwards_words_case)
    print("Alternate Uppercase Lowercase Case:", alternate_case)
    print("NATO Phonetic Alphabet Case:", nato_case)
    print("Binary Case:", binary_case)
    print("Hexadecimal Case:", hexadecimal_case)
    print("Upside Down Case:", upside_down_case)
    print("Emoji Case:", emoji_case)
    print("Zalgo Text Case:", zalgo_text_case)
    print("Inverted Case:", inverted_case)
    print("Rainbow Case:", rainbow_case)
    print("Acronym Case:", acronym_case)
    print("Spongebob Meme Case:", spongebob_meme_case)
    print("Reversed Sentence Case:", reversed_sentence_case)
    print("Pig Latin Case:", pig_latin_case)
    print("Reverse Words Case:", reverse_words_case)
    print("Random Shuffle Case:", random_shuffle_case)
    print("Vowel Removal Case:", vowel_removal_case)
    print("First Letter of Each Word Case:", first_letter_of_each_word_case)
    print("Scramble Middle Letters Case:", scramble_middle_letters_case)
    print("ASCII Value Case:", ascii_value_case)
    print("Repeated Letters Case:", repeated_letters_case)
    print("Numeric Words to Numbers Case:", numeric_words_to_numbers_case)
    print("Reverse Each Vowel Case:", reverse_each_vowel_case)
    print("Vowel Concatenation Case:", vowel_concatenation_case)
    print("Diagonal Text Case:", diagonal_text_case)
    print("Braille Transcription Case:", braille_transcription_case)
    print("Palindrome Check:", palindrome_check)
    # print("Interleaved Text:", interleaved_text)
    print("Alternate Character Deletion:", alternate_character_deletion)
    print("Numeronym:", numeronym)
    print("Word Count:", word_count)
    print("Reversed Word Order:", reversed_word_order)
    print("Alphabet Position:", alphabet_position)
    print("Double Every Second Word:", double_every_second_word)
    print("Longest Word:", longest_word)
    print("Character Frequency Count:", character_frequency_count)
    print("Reverse Words Individually:", reverse_words_individually)
    print("Substitute Numbers with Words:", substitute_numbers_with_words)
    print("Abbreviation:", abbreviation)
    print("Shuffled Sentences:", shuffled_sentences)
    print("Mirror Text:", mirror_text)
    print("Insert Random Spaces:", insert_random_spaces)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    """Main"""
    import doctest

    doctest.testmod()
    test()
