import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, csv, os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch

records = []
output_directory = "Reports"
os.makedirs(output_directory, exist_ok=True)

# ── PDF Generation ─────────────────────────────────────────────────────────────
def generate_pdf(data_list, report_type):
    if not data_list:
        raise ValueError("No records found. Please add data first.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_directory, f"{report_type}_Report_{timestamp}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=A4, leftMargin=0.75*inch, rightMargin=0.75*inch,
                    topMargin=0.75*inch,  bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story  = []

    # Title
    title_style = ParagraphStyle("t", parent=styles["Title"], fontSize=20, textColor=colors.HexColor("#2C3E50"), spaceAfter=4)
    story.append(Paragraph(f"{report_type} Report", title_style))

    # Date subtitle
    sub_style = ParagraphStyle("s", parent=styles["Normal"], fontSize=10, textColor=colors.grey, spaceAfter=14)
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y  %H:%M')}", sub_style))
    story.append(Spacer(1, 0.1*inch))

    # Column headers based on report type
    headers = (["Name","ID","Email","Course","Performance"] if report_type == "Student"
               else ["Name","ID","Email","Department/Role","Details"])
    keys = ["name","id","email","dept_role","performance"]

    # Build table
    rows = [headers] + [[str(r.get(k, "-")) for k in keys] for r in data_list]
    tbl  = Table(rows, colWidths=[1.3*inch,0.8*inch,1.8*inch,1.5*inch,1.5*inch], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0,0),(-1,0), colors.white),
        ("FONTNAME", (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0),(-1,0), 11),
        ("ALIGN", (0,0),(-1,-1), "CENTER"),
        ("VALIGN", (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [colors.HexColor("#ECF0F1"), colors.white]),
        ("GRID", (0,0),(-1,-1), 0.5, colors.HexColor("#BDC3C7")),
        ("TOPPADDING", (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph(f"Total records: {len(data_list)}", styles["Normal"]))
    doc.build(story)
    return filename

# ── GUI App ────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF Report Generator")
        self.geometry("780x560")
        self.resizable(False, False)
        self.configure(bg="aliceblue")
        self.report_type = tk.StringVar(value="Student")
        self.building_ui()

    def building_ui(self):
        # Header bar
        hdr = tk.Frame(self, bg="#2C3E50", height=58)
        hdr.pack(fill="x")
        tk.Label(hdr, text="PDF Report Generator", font=("Helvetica",16,"bold"),
                 bg="#2C3E50", fg="white").pack(side="left", padx=20, pady=12)

        # Report type selector
        top = tk.Frame(self, bg="aliceblue")
        top.pack(fill="x", padx=20, pady=(10,0))
        tk.Label(top, text="Report Type:", bg="aliceblue",
                 font=("Helvetica",10,"bold")).pack(side="left")
        for rt in ("Student", "Company"):
            tk.Radiobutton(top, text=rt, variable=self.report_type, value=rt,
                           bg="aliceblue", font=("Helvetica",10)).pack(side="left", padx=8)

        # Input form
        form = tk.LabelFrame(self, text=" Enter Record ", bg="aliceblue",
                             font=("Helvetica",10,"bold"), padx=12, pady=6)
        form.pack(fill="x", padx=20, pady=8)
        self.entries = {}
        for i, lbl in enumerate(["Name","ID","Email","Course / Role","Performance / Details"]):
            tk.Label(form, text=lbl+":", bg="aliceblue", width=20, anchor="w").grid(row=i, column=0, pady=2)
            e = tk.Entry(form, width=52, relief="solid", bd=1)
            e.grid(row=i, column=1, pady=2, sticky="w")
            self.entries[lbl] = e

        # Action buttons
        bf = tk.Frame(self, bg="aliceblue")
        bf.pack(pady=6)
        for txt, col, cmd in [
            ("Add Record",    "mediumseagreen", self.add_record),
            ("Load CSV/JSON", "steelblue", self.load_file),
            ("Generate PDF",  "crimson", self.generate_pdf),
            ("Clear All",     "lightslategray", self.clear_all)]:
            tk.Button(bf, text=txt, bg=col, fg="white", width=15,
                      font=("Helvetica",10,"bold"), relief="flat",
                      cursor="hand2", command=cmd).pack(side="left", padx=5)

        # Live preview table
        tf = tk.LabelFrame(self, text=" Records Preview ", bg="aliceblue",
                           font=("Helvetica",10,"bold"))
        tf.pack(fill="both", expand=True, padx=20, pady=(4,10))
        cols = ("Name","ID","Email","Course/Role","Performance")
        self.tree = ttk.Treeview(tf, columns=cols, show="headings", height=8)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=130, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=4, pady=4)

        # Status bar
        self.status = tk.StringVar(value="Ready  |  Records: 0")
        tk.Label(self, textvariable=self.status, bg="#2C3E50", fg="white",
                 anchor="w", padx=10).pack(fill="x", side="bottom")

    # ── Helpers ──
    def create_record(self):
        v = {k: e.get().strip() for k, e in self.entries.items()}
        if not v["Name"] or not v["ID"]:
            raise ValueError("Name and ID cannot be empty.")
        return {"name": v["Name"], "id": v["ID"], "email": v["Email"],
                "dept_role": v["Course / Role"], "performance": v["Performance / Details"]}

    def refresh_status(self):
        self.status.set(f"Ready  |  Records: {len(records)}")

    # ── Button actions ──
    def add_record(self):
        try:
            rec = self.create_record()
            records.append(rec)
            self.tree.insert("", "end", values=list(rec.values()))
            for e in self.entries.values(): e.delete(0, "end")
            self.refresh_status()
        except ValueError as ex:
            messagebox.showwarning("Missing Data", str(ex))

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV / JSON","*.csv *.json")])
        if not path: return
        try:
            loaded = []
            if path.endswith(".csv"):
                with open(path, newline="", encoding="utf-8") as f:
                    for row in csv.DictReader(f):
                        loaded.append({k.lower().replace(" ","_"): v for k,v in row.items()})
            else:
                with open(path, encoding="utf-8") as f:
                    loaded = json.load(f)
            for rec in loaded:
                r = {"name": rec.get("name",""), "id": rec.get("id",""),
                     "email": rec.get("email",""), "dept_role": rec.get("dept_role",""),
                     "performance": rec.get("performance","")}
                records.append(r)
                self.tree.insert("", "end", values=list(r.values()))
            self.refresh_status()
            messagebox.showinfo("Loaded", f"{len(loaded)} records loaded successfully.")
        except Exception as ex:
            messagebox.showerror("Load Error", str(ex))

    def generate_pdf(self):
        try:
            fname = generate_pdf(records, self.report_type.get())
            messagebox.showinfo("PDF Saved", f"Report saved to:\n{fname}")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def clear_all(self):
        records.clear()
        self.tree.delete(*self.tree.get_children())
        self.refresh_status()

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    App().mainloop()