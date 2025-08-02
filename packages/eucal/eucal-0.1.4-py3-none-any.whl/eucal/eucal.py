import click
from pprint import pprint
import pdfplumber
from pdfplumber.pdf import PDF

@click.command()
@click.argument('filename')
def main(filename: str):
    """Evaluation & Utilization of Clocked Activity Logs"""
    with pdfplumber.open(filename) as pdf:
        month_list = get_months(pdf)
        pprint(f"Month list: {month_list}")
        planned_hours = get_planned_hours(pdf)
        pprint(f"Planned hours: {planned_hours}")
        home_office_hours = get_home_office_hours(pdf)
        pprint(f"home office hours: {home_office_hours}")

    planned_hour_sum = 0.0
    for planned_hour in planned_hours:
        planned_hour_sum += float(planned_hour.replace(",", "."))
    
    
    print("Analysis summary".center(80, "-"))
    print(f"Total number of months: {len(month_list)}")
    print(f"Analyzed from {month_list[0]['month']} {month_list[0]['year']} to {month_list[-1]['month']} {month_list[-1]['year']}")
    print(f"Total planned hours: {planned_hour_sum:.2f} hours")

    home_office_hour_sum = 0.0
    for home_office_hour in home_office_hours:
        home_office_hour_sum += float(home_office_hour['hours'].replace(",", "."))
    print(f"Total home office hours: {home_office_hour_sum:.2f} hours")

    print(f"Relative Home office percentage: {home_office_hour_sum / planned_hour_sum * 100:.2f}%")


def get_home_office_hours(pdf: PDF):
    """Extract home office hours from a PDF file."""
    home_office_days = []
    for page_index, page in enumerate(pdf.pages):
        table = page.extract_table(table_settings={"horizontal_strategy": "lines"})

        for row in table:
            for cell in row:
                if cell and "Homeoffice" in cell and str(row[len(row)-4]):
                    home_office_days.append({"hours": row[len(row)-4], "day": row[0], "page_index": page_index})

    return home_office_days


def get_months(pdf: PDF):
    """determine months and page index."""
    months = []
    for page_index, page in enumerate(pdf.pages):
        text = page.extract_text()
        for line in text.split('\n'):
            if "Monat:" in line:
                date_string = line.split("Monat:")[1].strip()
                month, year = [part.strip() for part in date_string.split(' - ')]
                months.append({"month": month, "year": year, "page_index": page_index})
            elif "Month:" in line:
                date_string = line.split("Month:")[1].strip()
                month, year = [part.strip() for part in date_string.split(' - ')]
                months.append({"month": month, "year": year, "page_index": page_index})
    return months


def get_correct_sub_list(table, search_str: str):
    """For finding the planned working hours in a pdf file."""
    for row in table:
        if isinstance(row, list) and row and search_str in row[0]:
            return row
    return None


def get_planned_hours(pdf: PDF):
    """Extract planned hours from a PDF file."""
    planned_hours = []
    for page in pdf.pages:
        table = page.extract_table(table_settings={"horizontal_strategy": "lines"}) 

        for row in table:
            for cell in row:
                if cell and "mtl. Sollarbeitszeit" in cell:
                    # Find the row that contains the planned hours
                    planned_row = get_correct_sub_list(table, "mtl. Sollarbeitszeit")
                    if planned_row:
                        planned_hours.append(planned_row[1])
                elif cell and "Target hours" in cell:
                    # Find the row that contains the planned hours
                    planned_row = get_correct_sub_list(table, "Target hours")
                    if planned_row:
                        planned_hours.append(planned_row[1]) 
    return planned_hours


if __name__ == '__main__':
    main()
