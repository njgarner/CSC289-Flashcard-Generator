from django.http import JsonResponse, HttpResponse
import os
import json
import pandas as pd


def export_card_set(request):
    """
    Handle request to export a card set to Excel.
    """
    if request.method == "POST":
        card_set = request.POST.get('card_set')

        # Validate card set
        if not card_set:
            return JsonResponse({"error": "No card set data provided"}, status=400)
        
        try:
            # Convert card_set from JSON string to Python object
            card_set = json.loads(card_set)

            # Export the card set to an Excel file
            file_name = export_card_set_to_excel(card_set)

            # Open the file and return it as an HTTP response
            with open(file_name, 'rb') as excel_file:
                response = HttpResponse(
                    excel_file.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_name)}"'
                return response
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


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
