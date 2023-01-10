from InquirerPy import inquirer
from InquirerPy.base import Choice

from codelimit.common.report.Report import Report
from codelimit.common.report.ReportUnit import format_report_unit, ReportUnit
from codelimit.common.source_utils import get_location_range


class Browser:
    def __init__(self, report: Report):
        self.report = report

    def show(self):
        units = [Choice(value=unit, name=format_report_unit(unit)) for unit in
                 self.report.all_report_units_sorted_by_length_asc()]
        while True:
            selected_unit: ReportUnit = inquirer.select(message='Select unit', choices=units).execute()
            with open(selected_unit['file']) as file:
                code = file.read()
            snippet = get_location_range(code, selected_unit['measurement']['start'], selected_unit['measurement']['end'])
            print(snippet)
