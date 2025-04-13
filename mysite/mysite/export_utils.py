import pandas as pd

def export_card_set_to_excel(card_set, file_name="flashcard_set.xlsx"):
    """
    Export a card set to an Excel file.

    :param card_set: List of dictionaries where each dictionary represents a card.
                     Each dictionary should have 'Question' and 'Answer' keys.
    :param file_name: Name of the Excel file to save. Default is "flashcard_set.xlsx".
    """
    # Ensure the card set is properly formatted
    if not isinstance(card_set, list) or not all(isinstance(card, dict) for card in card_set):
        raise ValueError("Card set must be a list of dictionaries with 'Question' and 'Answer' keys.")
    
    # Convert the card set into a pandas DataFrame
    df = pd.DataFrame(card_set)
    
    # Ensure the DataFrame has the correct columns
    if 'Question' not in df.columns or 'Answer' not in df.columns:
        raise ValueError("Each card must have 'Question' and 'Answer' keys.")
    
    # Export the DataFrame to an Excel file
    try:
        df.to_excel(file_name, index=False, engine="openpyxl")
        return file_name
    except Exception as e:
        raise Exception(f"Failed to export card set to Excel: {e}")
