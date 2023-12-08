from reportlab.pdfgen import canvas
from boxsdk import JWTAuth, Client as boxClient
from datetime import datetime

box_config = JWTAuth.from_settings_file('box_config.json')
box_client = boxClient(box_config)
folder_id = 'your-folder-id'


def run_stamp(stamp_data: dict):
    # Stamp variables
    box_url: str = stamp_data["boxURL"]

    project_name: str = stamp_data["projectName"]
    project_number: str = stamp_data["projectNumber"]
    job_code: str = stamp_data["jobCode"]
    prepared_by: int = stamp_data["preparedBy"]
    prepared_for: str = stamp_data["preparedFor"]
    client: str = stamp_data["client"]
    is_revision: bool = stamp_data["isRevision"]
    revision_number: int = stamp_data["revisionNumber"]

    date_format: int = stamp_data["dateFormat"]

    job_phase_int: int = stamp_data["jobPhase"]
    issued_date_dict: dict = stamp_data["issuedDate"]
    revision_date_dict: dict = stamp_data["revisionDate"]

    issued_date: str = date_to_string(issued_date_dict, date_format)
    revision_date: str = date_to_string(revision_date_dict, date_format)


def date_to_string(date_dict: dict, format_code: int):
    # Extract year, month, and day from the dictionary
    year = int(date_dict['year'])
    month = int(date_dict['month'])
    day = int(date_dict['day'])

    # Create a datetime object
    date = datetime(year, month, day)

    # Define the formats
    formats = ["%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"]

    # Return the date string in the specified format
    return date.strftime(formats[format_code])


def generate_pdf():
    pass


def get_folder_contents():
    global folder_id, box_client
    folder = box_client.folder(folder_id).get()
    items = folder.get_items()
    return items
