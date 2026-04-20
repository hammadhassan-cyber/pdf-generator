PDF Report Generator:
  A simple desktop application to generate professional PDF reports for student or company data, built with Python, Tkinter, and ReportLab.

Requirements:
- Python 3.7 or higher
- reportlab library

Installation:
- Install reportlab library
pip install reportlab

Features:
- Add student or company records manually through a form
- Load bulk data from CSV or JSON files
- Preview all records in a table before generating
- Generate a professionally formatted PDF report
- Supports two report types: Student and Company
- PDF files are saved automatically with a timestamp in the reports/ folder
- Clear all data and start fresh at any time

Output:
  Generated PDF reports are saved in a folder named reports/ in the same directory as the script.

Notes:
- Name and ID fields are required. All other fields are optional.
- The reports/ folder is created automatically if it does not exist.
- Each time you run the app, it starts with an empty record list.
- Column headers in your CSV file must be lowercase and match exactly.

Author:
  Hammad Hassan
  hammad.hassan1857@gmail.com
