from openpyxl import Workbook
import pandas as pd
from openpyxl import Workbook
def format_data_for_spreadsheet(data):
    if not data:
        return []

    headers = sorted(set(key for item in data for key in item.keys()))
    formatted_data = [headers]
    for item in data:
        row = [item.get(header, 'N/A') for header in headers]
        formatted_data.append(row)
    return formatted_data
def write_to_excel(filename, data, sheet_name):
    df = pd.DataFrame(data[1:], columns=data[0])
    if os.path.exists(filename):
        # Load existing workbook and add a new sheet with the given name
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        # Create a new workbook and add the sheet with the given name
        with pd.ExcelWriter(filename, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
