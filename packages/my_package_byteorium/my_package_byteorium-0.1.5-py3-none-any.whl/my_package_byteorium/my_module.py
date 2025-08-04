"""
project python_project_template_byteorium
file    my_module.py
brief   This module defines the logic of my_package_byteorium.
author  mab0189
"""

########################################################################################################################
# IMPORTS
########################################################################################################################
from .my_subpackage.my_submodule import Language

########################################################################################################################
# DEFINES
########################################################################################################################


########################################################################################################################
# FUNCTION DEFINITIONS
########################################################################################################################
def hello_world() -> str:
    """
    This is a classic hello world function.
    :return: The string 'Hello World!'.
    """
    return "Hello World!"


########################################################################################################################
# CLASS DEFINITIONS
########################################################################################################################
class Greeter:
    """
    Greeter class.
    Can print a greeting in the chosen language.
    """

    def __init__(self, language: Language):
        """
        Constructor for the greeter.
        :param language: The language that the greeter will use.
        """
        self.language = language

    def greet(self) -> str:
        """
        Prints a greeting for the chosen language.
        :return: None.
        """
        match self.language:
            case Language.English:
                return "Hello World!"

            case Language.German:
                return "Hallo Welt!"

            case Language.Polish:
                return "Witaj świecie!"

            case _:
                return "Unknown language."


########################################################################################################################
# END OF FILE
########################################################################################################################
