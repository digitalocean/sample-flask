from reportlab.pdfgen import canvas
from boxsdk import Client, OAuth2

CLIENT_ID = 'your-client-id'
CLIENT_SECRET = 'your-client-secret'
ACCESS_TOKEN = 'your-access-token'

folder_id = 'your-folder-id'

oauth2 = OAuth2(CLIENT_ID, CLIENT_SECRET, access_token=ACCESS_TOKEN)
client = Client(oauth2)


def run_stamp(stamp_data: dict):
    # Stamp variables
    pass

def generate_pdf():
    pass

def generate_graphics():
    pass


def generate_text():
    pass


def get_folder_contents():
    global folder_id, client
    folder = client.folder(folder_id).get()
    items = folder.get_items()
    return items
