import pandas as pd

def export_flashcards_to_excel(flashcards, file_name='flashcards.xlsx'):
    """
    Exports flashcards to an Excel file.

    Args:
        flashcards (list of dict): List of flashcards where each flashcard is a dictionary.
        file_name (str): The name of the output Excel file.
    """
    df = pd.DataFrame(flashcards)
    df.to_excel(file_name, index=False)
    print(f"Flashcards successfully exported to {file_name}")
