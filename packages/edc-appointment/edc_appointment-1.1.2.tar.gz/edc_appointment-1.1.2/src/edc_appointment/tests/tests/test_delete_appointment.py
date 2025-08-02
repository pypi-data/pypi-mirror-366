import datetime as dt
from zoneinfo import ZoneInfo

import time_machine
from django.db.models import ProtectedError
from django.db.models.signals import post_save
from django.test import TestCase, override_settings
from edc_appointment_app.consents import consent_v1
from edc_appointment_app.models import SubjectVisit
from edc_appointment_app.visit_schedule import get_visit_schedule1, get_visit_schedule2
from edc_consent.site_consents import site_consents
from edc_facility.import_holidays import import_holidays
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from edc_appointment.constants import INCOMPLETE_APPT
from edc_appointment.creators import UnscheduledAppointmentCreator
from edc_appointment.managers import AppointmentDeleteError
from edc_appointment.models import Appointment, appointments_on_post_delete
from edc_appointment.utils import delete_appointment_in_sequence

from ..helper import Helper

utc = ZoneInfo("UTC")


@override_settings(SITE_ID=10)
@time_machine.travel(dt.datetime(2019, 6, 11, 8, 00, tzinfo=utc))
class TestDeleteAppointment(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    @classmethod
    def tearDownClass(cls):
        post_save.connect(
            appointments_on_post_delete, dispatch_uid="appointments_on_post_delete"
        )

    def setUp(self):
        post_save.disconnect(dispatch_uid="appointments_on_post_delete")
        self.subject_identifier = "12345"
        site_visit_schedules._registry = {}
        self.visit_schedule1 = get_visit_schedule1()
        self.visit_schedule2 = get_visit_schedule2()
        site_visit_schedules.register(self.visit_schedule1)
        site_visit_schedules.register(self.visit_schedule2)
        site_consents.registry = {}
        site_consents.register(consent_v1)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            now=ResearchProtocolConfig().study_open_datetime,
        )
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule1.name, schedule_name="schedule1"
        )
        appointments = Appointment.objects.filter(subject_identifier=self.subject_identifier)
        self.assertEqual(appointments.count(), 4)

        appointment = Appointment.objects.get(timepoint=0.0)
        SubjectVisit.objects.create(
            appointment=appointment,
            subject_identifier=appointment.subject_identifier,
            report_datetime=appointment.appt_datetime,
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name="schedule1",
            visit_code="1000",
            reason=SCHEDULED,
        )
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save_base(update_fields=["appt_status"])
        appointment.refresh_from_db()

        for i in range(1, 4):
            creator = UnscheduledAppointmentCreator(
                subject_identifier=self.subject_identifier,
                visit_schedule_name=self.visit_schedule1.name,
                schedule_name="schedule1",
                visit_code="1000",
                suggested_visit_code_sequence=appointment.visit_code_sequence + 1,
            )
            creator.appointment.appt_status = INCOMPLETE_APPT
            creator.appointment.save_base(update_fields=["appt_status"])
            appointment = creator.appointment

        self.appt_datetimes = [
            o.appt_datetime for o in Appointment.objects.all().order_by("appt_datetime")
        ]

    def test_delete_0_appointment_in_sequence(self):
        self.assertEqual(
            [0, 1, 2, 3],
            [
                o.visit_code_sequence
                for o in Appointment.objects.filter(visit_code="1000").order_by(
                    "appt_datetime"
                )
            ],
        )
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=0)
        # raises ProtectedError because Subjectvisit exists
        self.assertRaises(ProtectedError, delete_appointment_in_sequence, appointment)
        SubjectVisit.objects.get(appointment=appointment).delete()
        # raises AppointmentDeleteError (from manager) because not allowed by manager
        self.assertRaises(AppointmentDeleteError, delete_appointment_in_sequence, appointment)
        # assert nothing was done
        self.assertEqual(
            [0, 1, 2, 3],
            [
                o.visit_code_sequence
                for o in Appointment.objects.filter(visit_code="1000").order_by(
                    "appt_datetime"
                )
            ],
        )

    def test_delete_first_appointment_in_sequence(self):
        self.assertEqual(
            [0, 1, 2, 3],
            [
                o.visit_code_sequence
                for o in Appointment.objects.filter(visit_code="1000").order_by(
                    "appt_datetime"
                )
            ],
        )
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=1)
        delete_appointment_in_sequence(appointment)
        self.assertEqual(
            [0, 1, 2],
            [
                o.visit_code_sequence
                for o in Appointment.objects.filter(visit_code="1000").order_by(
                    "appt_datetime"
                )
            ],
        )

    def test_delete_second_appointment_in_sequence(self):
        self.assertEqual(
            [0, 1, 2, 3],
            [
                o.visit_code_sequence
                for o in Appointment.objects.filter(visit_code="1000").order_by(
                    "appt_datetime"
                )
            ],
        )
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=2)
        delete_appointment_in_sequence(appointment)
        self.assertEqual(
            [0, 1, 2],
            [
                o.visit_code_sequence
                for o in Appointment.objects.filter(visit_code="1000").order_by(
                    "appt_datetime"
                )
            ],
        )

    def test_delete_third_appointment_in_sequence(self):
        self.assertEqual(
            [0, 1, 2, 3],
            [
                o.visit_code_sequence
                for o in Appointment.objects.filter(visit_code="1000").order_by(
                    "appt_datetime"
                )
            ],
        )
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=3)
        delete_appointment_in_sequence(appointment)
        self.assertEqual(
            [0, 1, 2],
            [
                o.visit_code_sequence
                for o in Appointment.objects.filter(visit_code="1000").order_by(
                    "appt_datetime"
                )
            ],
        )
