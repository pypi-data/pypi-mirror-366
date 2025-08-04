"""
project python_project_template_byteorium
file    my_submodule.py
brief   This module defines the logic of a submodule.
author  mab0189
"""

########################################################################################################################
# IMPORTS
########################################################################################################################
from enum import Enum


########################################################################################################################
# DEFINES
########################################################################################################################
class Language(Enum):
    """
    Enum of supported languages.
    """

    German = 1
    English = 2
    Polish = 3


########################################################################################################################
# FUNCTION DEFINITIONS
########################################################################################################################
def language_difficulty(language: Language) -> str:
    """
    Ranks the difficulty of a language.
    language: The language to rank.
    return: The difficulty of the language as a string.
    """
    match language:
        case Language.English:
            return "Easy"
        case Language.German:
            return "Medium"
        case Language.Polish:
            return "Hard"
        case _:
            return "Unknown language"


########################################################################################################################
# END OF FILE
########################################################################################################################
