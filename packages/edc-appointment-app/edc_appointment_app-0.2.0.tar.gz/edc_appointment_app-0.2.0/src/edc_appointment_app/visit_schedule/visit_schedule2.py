from dateutil.relativedelta import relativedelta
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Visit
from edc_visit_schedule.visit_schedule import VisitSchedule

from ..consents import consent_v1
from .crfs import crfs, crfs_missed, requisitions


def get_visit_schedule2() -> VisitSchedule:
    visit_schedule2 = VisitSchedule(
        name="visit_schedule2",
        offstudy_model="edc_appointment_app.subjectoffstudy",
        death_report_model="edc_appointment_app.deathreport",
    )

    schedule2 = Schedule(
        name="schedule2",
        onschedule_model="edc_appointment_app.onscheduletwo",
        offschedule_model="edc_appointment_app.offscheduletwo",
        appointment_model="edc_appointment.appointment",
        consent_definitions=[consent_v1],
        base_timepoint=4,
    )

    visits = []
    for index in range(4, 8):
        visits.append(
            Visit(
                code=f"{1 if index == 0 else index + 1}000",
                title=f"Day {1 if index == 0 else index + 1}",
                timepoint=index,
                rbase=relativedelta(days=7 * index),
                rlower=relativedelta(days=0),
                rupper=relativedelta(days=6),
                requisitions=requisitions,
                crfs=crfs,
                crfs_missed=crfs_missed,
                facility_name="7-day-clinic",
            )
        )
    for visit in visits:
        schedule2.add_visit(visit)

    visit_schedule2.add_schedule(schedule2)
    return visit_schedule2
