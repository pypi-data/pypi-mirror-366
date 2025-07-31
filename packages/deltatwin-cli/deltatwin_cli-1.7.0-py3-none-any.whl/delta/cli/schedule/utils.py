import json

from rich.console import Console
from rich.table import Table

from delta.cli.utils import Utils

SCHEDULE = "Schedule"
SCHEDULE_NEXT = "Next schedule"
SCHEDULE_TYPE = "Type"
SCHEDULE_ID = "Id"
SCHEDULE_NAME = "Name"
DT_NAME = "DeltaTwin"
SCHEDULE_AUTHOR = "Owner"
SCHEDULE_INPUTS = "Input"


def display_line(console, name, value):
    console.print(name, f"[bold]{value}[/bold]", sep=":")


def display_schedule_detailed(schedule):
    console = Console(highlight=False)

    display_line(console, SCHEDULE_ID, schedule.get("schedule_id"))
    display_line(console, SCHEDULE_NAME, schedule.get("schedule_name"))
    display_line(console, SCHEDULE_AUTHOR, schedule.get("owner"))
    display_line(console, SCHEDULE, schedule.get("schedule"))
    display_line(console, SCHEDULE_NEXT, schedule.get("next_schedule"))
    display_line(console, SCHEDULE_TYPE, schedule.get("type"))
    display_line(
        console,
        DT_NAME,
        f"{schedule.get('deltatwin_name')}:{schedule.get('deltatwin_version')}"
    )

    Utils.display_table_schedule_parameter(
        console, SCHEDULE_INPUTS,
        schedule.get("inputs"))


def format_schedules(schedules: list):
    for sched in schedules:
        try:
            sched['schedule'] = Utils.format_date(
                sched['schedule'],
                "%Y-%m-%d %H:%M:%S"
            )
            sched['next_schedule'] = Utils.format_date(
                sched['next_schedule'],
                "%Y-%m-%d %H:%M:%S+00:00"
            )
        except ValueError:
            pass
    return schedules


def format_schedule(schedule: dict):
    try:
        schedule['schedule'] = Utils.format_date(
            schedule['schedule'],
            "%Y-%m-%d %H:%M:%S"
        )
        schedule['next_schedule'] = Utils.format_date(
            schedule['next_schedule'],
            "%Y-%m-%d %H:%M:%S+00:00"
        )
    except ValueError:
        pass
    return schedule


def display_list_detailed(schedules):
    table = Table(show_lines=True)
    table.add_column(SCHEDULE_ID)
    table.add_column(SCHEDULE)
    table.add_column(SCHEDULE_TYPE)
    table.add_column(SCHEDULE_NEXT)
    table.add_column(DT_NAME)
    table.add_column(SCHEDULE_AUTHOR)
    table.add_column(SCHEDULE_INPUTS)

    for dt in schedules:
        table.add_row(
            dt['schedule_id'],
            dt['schedule'],
            dt['type'],
            dt['next_schedule'],
            f"{dt['deltatwin_name']}:{dt['deltatwin_version']}",
            dt['owner'],
            str(json.dumps(dt['inputs'], indent=2)))

    console = Console()
    console.print(table)
