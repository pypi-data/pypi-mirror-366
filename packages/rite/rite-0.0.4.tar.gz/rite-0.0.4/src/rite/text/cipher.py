# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Provides Cipher Class
=====================

This class includes methods for encoding and decoding text using various
ciphers.
Currently implemented ciphers are the Caesar Cipher and Baconian Cipher.

Todo:
- Add more cipher methods.
- Implement error handling for edge cases.

Links:
- [Caesar Cipher](https://en.wikipedia.org/wiki/Caesar_cipher)
- [Baconian Cipher](https://en.wikipedia.org/wiki/Bacon%27s_cipher)

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


class Cipher(object):
    """
    Cipher Class
    ============

    Cipher Class for encoding and decoding text using various ciphers.
    Currently supports Caesar Cipher and Baconian Cipher.

    """

    @staticmethod
    def to_caesar_cipher(text: str, shift: int) -> str:
        """
        Encodes the text using a Caesar cipher with a given shift.
        Only alphabetic characters are shifted, others remain unchanged.

        Parameters:
        text (str): The text to encode.
        shift (int): The shift for the Caesar cipher.

        Returns:
        str: The encoded text.
        """
        encoded_text = []
        for char in text:
            if char.isalpha():
                start = 65 if char.isupper() else 97
                encoded_text.append(
                    chr((ord(char) - start + shift) % 26 + start)
                )
            else:
                encoded_text.append(char)
        return "".join(encoded_text)

    @staticmethod
    def from_caesar_cipher(encoded_text: str, shift: int) -> str:
        """
        Decodes the text from a Caesar cipher with a given shift.

        Parameters:
        encoded_text (str): The text to decode.
        shift (int): The shift used in the Caesar cipher.

        Returns:
        str: The decoded text.
        """
        return Cipher.to_caesar_cipher(encoded_text, -shift)

    @staticmethod
    def to_baconian_cipher(text: str) -> str:
        """
        Encodes text using the Baconian cipher. Non-alphabetic characters are
        ignored.

        Parameters:
        text (str): The text to encode.

        Returns:
        str: The encoded text using the Baconian cipher.
        """
        bacon_dict = {
            "a": "aaaaa",
            "b": "aaaab",
            "c": "aaaba",
            "d": "aaabb",
            "e": "aabaa",
            "f": "aabab",
            "g": "aabba",
            "h": "aabbb",
            "i": "abaaa",
            "j": "abaab",
            "k": "ababa",
            "l": "ababb",
            "m": "abbaa",
            "n": "abbab",
            "o": "abbba",
            "p": "abbbb",
            "q": "baaaa",
            "r": "baaab",
            "s": "baaba",
            "t": "baabb",
            "u": "babaa",
            "v": "babab",
            "w": "babba",
            "x": "babbb",
            "y": "bbaaa",
            "z": "bbaab",
        }
        return "".join(
            bacon_dict.get(char.lower(), "") for char in text if char.isalpha()
        )  # noqa E501

    @staticmethod
    def from_baconian_cipher(encoded_text: str) -> str:
        """
        Decodes text from the Baconian cipher. Assumes the text contains
        only 'a' and 'b'.

        Parameters:
        encoded_text (str): The text to decode.

        Returns:
        str: The decoded text from the Baconian cipher.
        """
        bacon_dict = {
            v: k
            for k, v in Cipher.to_baconian_cipher(
                "abcdefghijklmnopqrstuvwxyz"
            ).split()
        }  # noqa E501
        return "".join(
            bacon_dict.get(encoded_text[i : i + 5], "")
            for i in range(0, len(encoded_text), 5)
        )  # noqa E501

    @staticmethod
    def to_vigenere_cipher(text: str, key: str) -> str:
        """
        Encodes text using the Vigenère cipher.

        Parameters:
        text (str): The text to encode.
        key (str): The keyword used for encoding.

        Returns:
        str: The encoded text.
        """
        key = key.lower()
        key_length = len(key)
        key_as_int = [ord(i) for i in key]
        text_int = [ord(i) for i in text]
        encoded = ""
        for i in range(len(text_int)):
            if text[i].isalpha():
                value = (text_int[i] + key_as_int[i % key_length]) % 26
                encoded += (
                    chr(value + 65) if text[i].isupper() else chr(value + 97)
                )  # noqa E501
            else:
                encoded += text[i]
        return encoded

    @staticmethod
    def from_vigenere_cipher(encoded_text: str, key: str) -> str:
        """
        Decodes text from the Vigenère cipher.

        Parameters:
        encoded_text (str): The text to decode.
        key (str): The keyword used for encoding.

        Returns:
        str: The decoded text.
        """
        key = key.lower()
        key_length = len(key)
        key_as_int = [ord(i) for i in key]
        text_int = [ord(i) for i in encoded_text]
        decoded = ""
        for i in range(len(text_int)):
            if encoded_text[i].isalpha():
                value = (text_int[i] - key_as_int[i % key_length]) % 26
                decoded += (
                    chr(value + 65)
                    if encoded_text[i].isupper()
                    else chr(value + 97)
                )  # noqa E501
            else:
                decoded += encoded_text[i]
        return decoded

    @staticmethod
    def to_atbash_cipher(text: str) -> str:
        """
        Encodes and decodes text using the Atbash cipher (reversible).

        Parameters:
        text (str): The text to encode or decode.

        Returns:
        str: The encoded or decoded text.
        """
        return text.translate(
            str.maketrans(
                "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                "ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba",
            )
        )

    @staticmethod
    def to_rot13_cipher(text: str) -> str:
        """
        Encodes and decodes text using the Rot13 cipher (reversible).

        Parameters:
        text (str): The text to encode or decode.

        Returns:
        str: The encoded or decoded text.
        """
        return text.translate(
            str.maketrans(
                "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
                "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm",
            )
        )

    @staticmethod
    def to_binary_encoding(text: str) -> str:
        """
        Encodes text to binary.

        Parameters:
        text (str): The text to encode.

        Returns:
        str: The binary encoded text.
        """
        return " ".join(format(ord(char), "08b") for char in text)

    @staticmethod
    def from_binary_decoding(binary_text: str) -> str:
        """
        Decodes binary to text.

        Parameters:
        binary_text (str): The binary text to decode.

        Returns:
        str: The decoded text.
        """
        return "".join(chr(int(binary, 2)) for binary in binary_text.split())

    @staticmethod
    def to_rail_fence_cipher(text: str, num_rails: int) -> str:
        """
        Encodes text using the Rail Fence cipher.

        Parameters:
        text (str): The text to encode.
        num_rails (int): The number of rails.

        Returns:
        str: The encoded text.
        """
        fence = [[] for _ in range(num_rails)]
        rail = 0
        change = 1

        for char in text:
            fence[rail].append(char)
            rail += change

            if rail == num_rails - 1 or rail == 0:
                change = -change

        return "".join("".join(row) for row in fence)

    @staticmethod
    def from_rail_fence_cipher(encoded_text: str, num_rails: int) -> str:
        """
        Decodes text from the Rail Fence cipher.

        Parameters:
        encoded_text (str): The text to decode.
        num_rails (int): The number of rails.

        Returns:
        str: The decoded text.
        """
        fence = [[] for _ in range(num_rails)]
        rail_lengths = [0] * num_rails
        rail = 0
        change = 1

        for char in encoded_text:
            rail_lengths[rail] += 1
            rail += change
            if rail == num_rails - 1 or rail == 0:
                change = -change

        index = 0
        for i, length in enumerate(rail_lengths):
            fence[i] = list(encoded_text[index : index + length])
            index += length

        result = []
        rail = 0
        change = 1
        for _ in range(len(encoded_text)):
            result.append(fence[rail].pop(0))
            rail += change

            if rail == num_rails - 1 or rail == 0:
                change = -change

        return "".join(result)

    @staticmethod
    def to_xor_cipher(text: str, key: str) -> str:
        """
        Encodes and decodes text using the XOR cipher with a key.

        Parameters:
        text (str): The text to encode or decode.
        key (str): The key for the XOR cipher.

        Returns:
        str: The encoded or decoded text.
        """
        return "".join(
            chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text)
        )

    @staticmethod
    def to_reverse_cipher(text: str) -> str:
        """
        Reverses the text.

        Parameters:
        text (str): The text to reverse.

        Returns:
        str: The reversed text.
        """
        return text[::-1]

    @staticmethod
    def to_transposition_cipher(text: str, key: int) -> str:
        """
        Encodes text using a simple columnar transposition cipher.

        Parameters:
        text (str): The text to encode.
        key (int): The number of columns.

        Returns:
        str: The encoded text.
        """
        return "".join(text[i::key] for i in range(key))

    @staticmethod
    def from_transposition_cipher(encoded_text: str, key: int) -> str:
        """
        Decodes text from a simple columnar transposition cipher.

        Parameters:
        encoded_text (str): The text to decode.
        key (int): The number of columns.

        Returns:
        str: The decoded text.
        """
        num_rows = len(encoded_text) // key
        remainder = len(encoded_text) % key
        text = [""] * num_rows

        for col in range(key):
            start_index = (num_rows + 1) * min(
                col, remainder
            ) + num_rows * max(0, col - remainder)
            end_index = start_index + (
                num_rows + 1 if col < remainder else num_rows
            )
            for row, char in enumerate(encoded_text[start_index:end_index]):
                text[row] += char

        return "".join(text)

    @staticmethod
    def create_playfair_square(key: str):
        """
        Create a Playfair square with a given key.
        """
        alphabet = (
            "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # J is omitted in traditional Playfair
        )
        key = "".join(sorted(set(key.upper()), key=lambda x: key.index(x)))
        key += "".join([c for c in alphabet if c not in key])
        return [key[i : i + 5] for i in range(0, 25, 5)]

    @staticmethod
    def playfair_cipher_pair(pair, square, mode="encode"):
        """
        Cipher a pair of letters using the Playfair square.
        """

        def find_position(c):
            for row in square:
                if c in row:
                    return square.index(row), row.index(c)

        pos1 = find_position(pair[0])
        pos2 = find_position(pair[1])

        if pos1[0] == pos2[0]:  # Same row
            col_shift = 1 if mode == "encode" else -1
            return (
                square[pos1[0]][(pos1[1] + col_shift) % 5]
                + square[pos2[0]][(pos2[1] + col_shift) % 5]
            )
        elif pos1[1] == pos2[1]:  # Same column
            row_shift = 1 if mode == "encode" else -1
            return (
                square[(pos1[0] + row_shift) % 5][pos1[1]]
                + square[(pos2[0] + row_shift) % 5][pos2[1]]
            )
        else:  # Rectangle
            return square[pos1[0]][pos2[1]] + square[pos2[0]][pos1[1]]

    @staticmethod
    def to_playfair_cipher(text: str, key: str) -> str:
        """
        Encodes text using the Playfair cipher.

        Parameters:
        text (str): The text to encode.
        key (str): The key for the Playfair cipher.

        Returns:
        str: The encoded text.
        """

        def prepare_text(text):
            text = text.upper().replace("J", "I")
            prepared_text = ""
            i = 0
            while i < len(text):
                if i + 1 < len(text) and text[i] != text[i + 1]:
                    prepared_text += text[i : i + 2]
                    i += 2
                else:
                    prepared_text += text[i] + "X"
                    i += 1
            if len(prepared_text) % 2 != 0:
                prepared_text += "X"
            return prepared_text

        square = Cipher.create_playfair_square(key)
        prepared_text = prepare_text(text)
        encoded_text = ""

        for i in range(0, len(prepared_text), 2):
            encoded_text += Cipher.playfair_cipher_pair(
                prepared_text[i : i + 2], square, "encode"
            )

        return encoded_text

    @staticmethod
    def from_playfair_cipher(encoded_text: str, key: str) -> str:
        """
        Decodes text from the Playfair cipher.

        Parameters:
        encoded_text (str): The text to decode.
        key (str): The key for the Playfair cipher.

        Returns:
        str: The decoded text.
        """
        square = Cipher.create_playfair_square(key)
        decoded_text = ""

        for i in range(0, len(encoded_text), 2):
            decoded_text += Cipher.playfair_cipher_pair(
                encoded_text[i : i + 2], square, "decode"
            )

        return decoded_text

    @staticmethod
    def to_scytale_cipher(text: str, diameter: int) -> str:
        """
        Encodes text using the Scytale cipher.

        Parameters:
        text (str): The text to encode.
        diameter (int): The diameter (number of characters per turn) of the Scytale.

        Returns:
        str: The encoded text.
        """
        if diameter <= 0:
            return text

        padded_text = text + " " * (
            (diameter - len(text) % diameter) % diameter
        )
        encoded_text = [""] * diameter

        for i, char in enumerate(padded_text):
            encoded_text[i % diameter] += char

        return "".join(encoded_text)

    @staticmethod
    def from_scytale_cipher(encoded_text: str, diameter: int) -> str:
        """
        Decodes text from the Scytale cipher.

        Parameters:
        encoded_text (str): The text to decode.
        diameter (int): The diameter used in the Scytale cipher.

        Returns:
        str: The decoded text.
        """
        if diameter <= 0:
            return encoded_text

        num_columns = len(encoded_text) // diameter
        decoded_text = [""] * num_columns

        for i, char in enumerate(encoded_text):
            decoded_text[i // diameter] += char

        return "".join(decoded_text).rstrip()

    @staticmethod
    def to_autokey_cipher(text: str, key: str) -> str:
        """
        Encodes text using the Autokey cipher.

        Parameters:
        text (str): The text to encode.
        key (str): The key for the Autokey cipher.

        Returns:
        str: The encoded text.
        """

        def char_shift(c, k):
            return chr(((ord(c) - 97 + (ord(k) - 97)) % 26) + 97)

        key = key.lower() + text.lower()
        encoded_text = ""

        for i, char in enumerate(text.lower()):
            if char.isalpha():
                encoded_text += char_shift(char, key[i])
            else:
                encoded_text += char

        return encoded_text

    @staticmethod
    def from_autokey_cipher(encoded_text: str, key: str) -> str:
        """
        Decodes text from the Autokey cipher.

        Parameters:
        encoded_text (str): The text to decode.
        key (str): The key for the Autokey cipher.

        Returns:
        str: The decoded text.
        """

        def char_shift(c, k):
            return chr(((ord(c) - 97 - (ord(k) - 97)) % 26) + 97)

        key = key.lower()
        decoded_text = ""
        key_index = 0

        for char in encoded_text.lower():
            if char.isalpha():
                decoded_char = char_shift(char, key[key_index])
                decoded_text += decoded_char
                key += decoded_char  # Append the decoded char to the key
                key_index += 1
            else:
                decoded_text += char

        return decoded_text

    @staticmethod
    def generate_square(key: str):
        """
        Generate a 5x5 matrix for the Four-Square cipher using a key.
        """
        alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # Typically J is omitted
        key = "".join(sorted(set(key.upper()), key=lambda x: key.index(x)))
        key += "".join([c for c in alphabet if c not in key])
        return [key[i : i + 5] for i in range(0, 25, 5)]

    @staticmethod
    def four_square_cipher_pair(pair, square1, square2, mode="encode"):
        """
        Cipher a pair of letters using the Four-Square squares.
        """

        def find_position(letter, square):
            for row in square:
                if letter in row:
                    return square.index(row), row.index(letter)

        # Find positions in the standard square
        pos1 = find_position(pair[0], square1)
        pos2 = find_position(pair[1], square2)

        if mode == "encode":
            return square2[pos1[0]][pos2[1]] + square1[pos2[0]][pos1[1]]
        else:  # mode == 'decode'
            return square1[pos1[0]][pos2[1]] + square2[pos2[0]][pos1[1]]

    @staticmethod
    def to_four_square_cipher(text: str, key1: str, key2: str) -> str:
        """
        Encodes text using the Four-Square cipher.

        Parameters:
        text (str): The text to encode.
        key1 (str): The first key for the Four-Square cipher.
        key2 (str): The second key for the Four-Square cipher.

        Returns:
        str: The encoded text.
        """
        square1 = Cipher.generate_square(key1)
        square2 = Cipher.generate_square(key2)
        standard_square = Cipher.generate_square("")

        text = text.upper().replace("J", "I")
        if len(text) % 2 != 0:
            text += "X"

        encoded_text = ""

        for i in range(0, len(text), 2):
            encoded_text += Cipher.four_square_cipher_pair(
                text[i : i + 2],
                standard_square,
                standard_square,
                mode="encode",
            )

        return encoded_text

    @staticmethod
    def from_four_square_cipher(
        encoded_text: str, key1: str, key2: str
    ) -> str:
        """
        Decodes text from the Four-Square cipher.

        Parameters:
        encoded_text (str): The text to decode.
        key1 (str): The first key used in the Four-Square cipher.
        key2 (str): The second key used in the Four-Square cipher.

        Returns:
        str: The decoded text.
        """
        square1 = Cipher.generate_square(key1)
        square2 = Cipher.generate_square(key2)
        standard_square = Cipher.generate_square("")

        decoded_text = ""

        for i in range(0, len(encoded_text), 2):
            decoded_text += Cipher.four_square_cipher_pair(
                encoded_text[i : i + 2], square1, square2, mode="decode"
            )

        return decoded_text


# =============================================================================
# Functions
# =============================================================================


def test():
    """
    Test Function
    """

    # Example usage:
    caesar_cipher = Cipher.to_caesar_cipher("AB", 3)
    decoded_caesar = Cipher.from_caesar_cipher(caesar_cipher, 3)
    baconian_cipher = Cipher.to_baconian_cipher("Hello")
    decoded_baconian = Cipher.from_baconian_cipher(baconian_cipher)
    vigenere_cipher = Cipher.to_vigenere_cipher("Hello World", "Key")
    decoded_vigenere = Cipher.from_vigenere_cipher(vigenere_cipher, "Key")
    atbash_cipher = Cipher.to_atbash_cipher("Hello")
    rot13_cipher = Cipher.to_rot13_cipher("Hello")
    binary_encoded = Cipher.to_binary_encoding("Hello")
    binary_decoded = Cipher.from_binary_decoding(binary_encoded)
    rail_fence_cipher = Cipher.to_rail_fence_cipher("Hello World", 3)
    decoded_rail_fence = Cipher.from_rail_fence_cipher(rail_fence_cipher, 3)
    xor_cipher = Cipher.to_xor_cipher("Hello", "key")
    reverse_cipher = Cipher.to_reverse_cipher("Hello")
    transposition_cipher = Cipher.to_transposition_cipher("Hello World", 4)
    decoded_transposition = Cipher.from_transposition_cipher(
        transposition_cipher, 4
    )
    playfair_cipher = Cipher.to_playfair_cipher("Hello", "Key")
    decoded_playfair = Cipher.from_playfair_cipher(playfair_cipher, "Key")
    scytale_cipher = Cipher.to_scytale_cipher("Hello", 3)
    decoded_scytale = Cipher.from_scytale_cipher(scytale_cipher, 3)
    autokey_cipher = Cipher.to_autokey_cipher("Hello", "Key")
    decoded_autokey = Cipher.from_autokey_cipher(autokey_cipher, "Key")
    four_square_cipher = Cipher.to_four_square_cipher("Hello", "Key1", "Key2")
    decoded_four_square = Cipher.from_four_square_cipher(
        four_square_cipher, "Key1", "Key2"
    )

    print("Caesar Cipher:", caesar_cipher)
    print("Decoded Caesar:", decoded_caesar)
    print("Baconian Cipher:", baconian_cipher)
    print("Decoded Baconian:", decoded_baconian)
    print("Vigenère Cipher:", vigenere_cipher)
    print("Decoded Vigenère:", decoded_vigenere)
    print("Atbash Cipher:", atbash_cipher)
    print("Rot13 Cipher:", rot13_cipher)
    print("Binary Encoded:", binary_encoded)
    print("Binary Decoded:", binary_decoded)
    print("Rail Fence Cipher:", rail_fence_cipher)
    print("Decoded Rail Fence:", decoded_rail_fence)
    print("XOR Cipher:", xor_cipher)
    print("Reverse Cipher:", reverse_cipher)
    print("Transposition Cipher:", transposition_cipher)
    print("Decoded Transposition:", decoded_transposition)
    print("Playfair Cipher:", playfair_cipher)
    print("Decoded Playfair:", decoded_playfair)
    print("Scytale Cipher:", scytale_cipher)
    print("Decoded Scytale:", decoded_scytale)
    print("Autokey Cipher:", autokey_cipher)
    print("Decoded Autokey:", decoded_autokey)
    print("Four-Square Cipher:", four_square_cipher)
    print("Decoded Four-Square:", decoded_four_square)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    """Main"""
    import doctest

    doctest.testmod()
    test()
