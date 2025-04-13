from django.http import JsonResponse, HttpResponse
from .export_utils import export_card_set_to_excel
import os

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
            import json
            card_set = json.loads(card_set)

            # Export the card set to an Excel file
            file_name = export_card_set_to_excel(card_set)

            # Open the file and return it as an HTTP response
            with open(file_name, 'rb') as excel_file:
                response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_name)}"'
                return response
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)