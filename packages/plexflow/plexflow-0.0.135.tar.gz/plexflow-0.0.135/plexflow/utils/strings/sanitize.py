import string

def remove_punctuation(text):
  """Removes all punctuation from a given string."""
  if not isinstance(text, str):
    return "" # Handle non-string input gracefully

  translator = str.maketrans('', '', string.punctuation)
  return text.translate(translator)

def clean_string(input_string, remove_spaces: bool = False):
    """
    Strips all punctuation and spaces from a string and converts it to lowercase.

    Args:
        input_string (str): The string to clean.

    Returns:
        str: The cleaned string.
    """
    # Create a translation table to remove punctuation
    # string.punctuation contains all standard punctuation characters
    translator = str.maketrans('', '', string.punctuation)

    # Remove punctuation using the translation table
    no_punctuation = input_string.translate(translator)

    # Remove all spaces
    no_spaces = no_punctuation.replace(" ", "") if remove_spaces else no_punctuation

    # Convert to lowercase
    cleaned_string = no_spaces.lower()

    return cleaned_string