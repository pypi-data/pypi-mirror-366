from datetime import datetime

FORMATS = [
    '%d/%m/%Y %H:%M:%S',       # e.g., 16/04/2019 23:45:10
    '%m/%d/%Y %I:%M:%S %p',    # e.g., 4/16/2019 12:02:51 AM
]

def convert_dotnet_datetime_to_python_datetime(csharp_datetime_str: str) -> datetime:
    for fmt in FORMATS:
        try:
            return datetime.strptime(csharp_datetime_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized datetime format: '{csharp_datetime_str}'")
