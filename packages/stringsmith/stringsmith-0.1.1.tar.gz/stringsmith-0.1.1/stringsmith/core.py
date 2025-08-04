import random
import string


class StringSmith:

    @staticmethod
    def get_random_numbers(length : int):

        # Generate a random string of digits only.
        return ''.join(random.choices(string.digits, k=length))


    @staticmethod
    def get_random_alphabets(length : int):

        return ''.join(random.choices(string.ascii_letters, k=length))


    @staticmethod
    def get_random_alphanumeric(length : int, include_special_characters : bool = False):

        chars = string.ascii_letters + string.digits
        if include_special_characters:
            chars += string.punctuation
        return ''.join(random.choices(chars, k=length))