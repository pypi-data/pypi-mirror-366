#
#
#
import logging
import random
import string
import secrets
from python_byzatic_commons.random_string_generator.interfaces.RandomStringGeneratorInterface import RandomStringGeneratorInterface


class RandomStringGenerator(RandomStringGeneratorInterface):
    def __init__(self):
        self.logger = logging.getLogger("Application-logger")

    def get_string(self, letters_count: int, digits_count: int) -> str:
        letters = ''.join((random.choice(string.ascii_letters) for i in range(letters_count)))
        digits = ''.join((random.choice(string.digits) for i in range(digits_count)))
        # Convert resultant string to list and shuffle it to mix letters and digits
        sample_list = list(letters + digits)
        random.shuffle(sample_list)
        # convert list to string
        final_string = ''.join(sample_list)
        self.logger.debug(f"generated: {final_string}")
        return final_string

    def get_token(self, letters_count: int) -> str:
        final_string = secrets.token_hex(letters_count)
        self.logger.debug(f"generated: {final_string}")
        return final_string
