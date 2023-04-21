from flask import (
    Blueprint, g, render_template, request, session,send_file
)
from datetime import datetime,timedelta
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.styles import PatternFill, Font,Alignment
from Backend.auth import auth
from .estrategiaDeFacturacion import *
from Backend.database.database import connect_db
from Backend.scriptGeneral import scriptGeneral



