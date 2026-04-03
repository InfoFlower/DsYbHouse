import os
from dotenv import load_dotenv
load_dotenv()
BASE_DIR = os.getenv('WD')

WORKSPACE = f"{BASE_DIR}/src/AUTOMATE/"


from AUTOMATE.TASKS import RequestHandler