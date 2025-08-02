import pandas as pd
import glob
from fpdf import FPDF
from pathlib import Path
import os


def generate(invoices_path, pdfs_path, id, name, amount_purchased, price, total_price):
    files = glob.glob(f"{invoices_path}/*.xlsx")

    for file in files:

        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()

        filename = Path(file).stem.split("-")[0]
        date = Path(file).stem.split("-")[1]

        pdf.set_font(family="Times", size=16, style="B")
        pdf.cell(w=50, h=8, txt=f"Invoice: {filename}", ln=1)

        pdf.set_font(family="Times", size=12)
        pdf.cell(w=50, h=8, txt=f"Date: {date}", ln=1)

        df = pd.read_excel(file, sheet_name="Sheet 1")
        for col in list(df.columns):
            pdf.set_font(family="Times", size=12, style="B")
            if col != "product_name":
                pdf.cell(w=30, h=8, txt=str(col.replace("_", " ").title()), border=1)
            else:
                pdf.cell(w=70, h=8, txt=str(col.replace("_", " ").title()), border=1)
        pdf.ln(8)
        for idx, row in df.iterrows():
            pdf.set_font(family="Times", size=12)
            pdf.cell(w=30, h=8, txt=str(row[id]), border=1)
            pdf.cell(w=70, h=8, txt=str(row[name]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[amount_purchased]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[price]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[total_price]), border=1, ln=1)

        total_sum = df[total_price].sum()
        pdf.set_font(family="Times", size=12)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=70, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt=str(total_sum), border=1, ln=1)

        pdf.set_font(family="Times", size=12)
        pdf.cell(w=30, h=8, txt=f"The total price is {total_sum}")
        if not os.path.exists(pdfs_path):
            os.makedirs(pdfs_path)
        pdf.output(f"{pdfs_path}/{filename}.pdf")
