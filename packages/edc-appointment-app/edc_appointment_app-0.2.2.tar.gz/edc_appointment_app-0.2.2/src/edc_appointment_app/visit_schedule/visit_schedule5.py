from dateutil.relativedelta import relativedelta
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Visit
from edc_visit_schedule.visit_schedule import VisitSchedule

from edc_appointment_app.consents import consent_v1
from edc_appointment_app.visit_schedule.crfs import crfs, crfs_missed


def get_visit_schedule5() -> VisitSchedule:
    visit_schedule5 = VisitSchedule(
        name="visit_schedule5",
        offstudy_model="edc_appointment_app.subjectoffstudy",
        death_report_model="edc_appointment_app.deathreport",
    )

    schedule5 = Schedule(
        name="monthly_schedule",
        onschedule_model="edc_appointment_app.onschedulethree",
        offschedule_model="edc_appointment_app.offschedulethree",
        appointment_model="edc_appointment.appointment",
        consent_definitions=[consent_v1],
    )

    visits = [
        Visit(
            code="1000",
            title="Baseline",
            timepoint=0,
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=0),
            add_window_gap_to_lower=True,
            requisitions=None,
            crfs=crfs,
            crfs_missed=crfs_missed,
            facility_name="7-day-clinic",
        )
    ]
    for index, visit_code in [
        (1, "1010"),
        (2, "1020"),
        (3, "1030"),
        (4, "1040"),
        (5, "1050"),
        (6, "1060"),
        (7, "1070"),
        (8, "1080"),
        (9, "1090"),
    ]:
        visits.append(
            Visit(
                code=visit_code,
                title=f"Month {index}",
                timepoint=index,
                rbase=relativedelta(months=index),
                rlower=relativedelta(days=15),
                rupper=relativedelta(days=15),
                add_window_gap_to_lower=True,
                max_window_gap_to_lower=None,
                requisitions=None,
                crfs=crfs,
                crfs_missed=crfs_missed,
                facility_name="7-day-clinic",
                allow_unscheduled=True,
            )
        )
    for visit in visits:
        schedule5.add_visit(visit)

    visit_schedule5.add_schedule(schedule5)
    return visit_schedule5
