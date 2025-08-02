import datetime as dt
from zoneinfo import ZoneInfo

import time_machine
from django.test import TestCase, override_settings
from edc_appointment_app.consents import consent_v1
from edc_appointment_app.models import SubjectVisit
from edc_appointment_app.visit_schedule import get_visit_schedule1, get_visit_schedule2
from edc_consent.site_consents import site_consents
from edc_facility.import_holidays import import_holidays
from edc_metadata.utils import get_crf_metadata_model_cls
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from edc_appointment.appointment_status_updater import AppointmentStatusUpdater
from edc_appointment.constants import IN_PROGRESS_APPT, INCOMPLETE_APPT, NEW_APPT
from edc_appointment.models import Appointment

from ..helper import Helper

utc_tz = ZoneInfo("UTC")


@override_settings(SITE_ID=10)
@time_machine.travel(dt.datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz))
class TestAppointmentStatus(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
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
        schedule_name = self.visit_schedule1.schedules.get("schedule1").name
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule1.name, schedule_name=schedule_name
        )

    def test_appointment_status(self):
        appointments = Appointment.objects.filter(subject_identifier=self.subject_identifier)
        self.assertEqual(appointments.count(), 4)

        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )

        self.assertGreater(get_crf_metadata_model_cls().objects.all().count(), 0)
        appointment = appointments[0]
        appointment.refresh_from_db()
        self.assertEqual(appointment.appt_status, IN_PROGRESS_APPT)
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()
        appointment.refresh_from_db()
        self.assertEqual(appointment.appt_status, INCOMPLETE_APPT)
        appointment.appt_status = IN_PROGRESS_APPT
        appointment.save()
        appointment.refresh_from_db()
        self.assertEqual(appointment.appt_status, IN_PROGRESS_APPT)

    def test_appointment_status2(self):
        appointments = Appointment.objects.filter(subject_identifier=self.subject_identifier)
        self.assertEqual(appointments.count(), 4)

        # complete baseline appt/visit
        appointment_baseline = appointments[0]
        appointment_baseline.appt_status = IN_PROGRESS_APPT
        appointment_baseline.save()
        appointment_baseline.refresh_from_db()

        SubjectVisit.objects.create(
            appointment=appointment_baseline,
            report_datetime=appointment_baseline.appt_datetime,
            reason=SCHEDULED,
        )
        self.assertGreater(get_crf_metadata_model_cls().objects.all().count(), 0)

        appointment = appointments[1]
        appointment.refresh_from_db()
        self.assertEqual(appointment.appt_status, NEW_APPT)
        appointment.appt_status = IN_PROGRESS_APPT
        appointment.save()
        appointment.refresh_from_db()
        appointment_baseline.refresh_from_db()
        self.assertEqual(appointment_baseline.appt_status, INCOMPLETE_APPT)
        self.assertEqual(appointment.appt_status, IN_PROGRESS_APPT)

    def test_appt_status_updater_init(self):
        appointments = Appointment.objects.filter(subject_identifier=self.subject_identifier)
        self.assertEqual(appointments.count(), 4)

        # complete baseline appt/visit
        appointment_baseline = appointments[0]
        AppointmentStatusUpdater(appointment=appointment_baseline)

    def test_appt_status_updater_init2(self):
        appointments = Appointment.objects.filter(subject_identifier=self.subject_identifier)
        appointment_baseline = appointments[0]
        appointment_1 = appointments[1]
        appointment_2 = appointments[2]
        appointment_3 = appointments[3]

        self.assertEqual(appointments.count(), 4)

        # complete baseline appt/visit
        appointment_baseline = appointments[0]
        SubjectVisit.objects.create(
            appointment=appointment_baseline,
            report_datetime=appointment_baseline.appt_datetime,
            reason=SCHEDULED,
        )
        appointment_baseline.refresh_from_db()
        self.assertEqual(appointment_baseline.appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointment_1.appt_status, NEW_APPT)
        self.assertEqual(appointment_2.appt_status, NEW_APPT)
        self.assertEqual(appointment_3.appt_status, NEW_APPT)

        # change to incomplete
        appointment_baseline.appt_status = INCOMPLETE_APPT
        appointment_baseline.save()
        appointment_baseline.refresh_from_db()

        self.assertEqual(appointment_baseline.appt_status, INCOMPLETE_APPT)
        self.assertEqual(appointment_1.appt_status, NEW_APPT)
        self.assertEqual(appointment_2.appt_status, NEW_APPT)
        self.assertEqual(appointment_3.appt_status, NEW_APPT)

        # use appointment status updater to change to in_progress
        AppointmentStatusUpdater(appointment=appointment_baseline, change_to_in_progress=True)
        appointment_baseline.refresh_from_db()
        self.assertEqual(appointment_baseline.appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointment_1.appt_status, NEW_APPT)
        self.assertEqual(appointment_2.appt_status, NEW_APPT)
        self.assertEqual(appointment_3.appt_status, NEW_APPT)

    def test_appt_status_updater_appt_1(self):
        appointments = Appointment.objects.filter(subject_identifier=self.subject_identifier)
        appointment_baseline = appointments[0]
        appointment_1 = appointments[1]
        appointment_2 = appointments[2]
        appointment_3 = appointments[3]

        self.assertEqual(appointments.count(), 4)
        # complete baseline appt/visit
        appointment_baseline = appointments[0]
        SubjectVisit.objects.create(
            appointment=appointment_baseline,
            report_datetime=appointment_baseline.appt_datetime,
            reason=SCHEDULED,
        )
        appointment_baseline.refresh_from_db()
        self.assertEqual(appointment_baseline.appt_status, IN_PROGRESS_APPT)

        # change to incomplete
        appointment_baseline.appt_status = INCOMPLETE_APPT
        appointment_baseline.save()
        appointment_baseline.refresh_from_db()

        SubjectVisit.objects.create(
            appointment=appointment_1,
            report_datetime=appointment_1.appt_datetime,
            reason=SCHEDULED,
        )

        appointment_baseline.refresh_from_db()
        appointment_1.refresh_from_db()
        appointment_2.refresh_from_db()
        appointment_3.refresh_from_db()

        self.assertEqual(appointment_baseline.appt_status, INCOMPLETE_APPT)
        self.assertEqual(appointment_1.appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointment_2.appt_status, NEW_APPT)
        self.assertEqual(appointment_3.appt_status, NEW_APPT)

        appointment_2.appt_status = IN_PROGRESS_APPT
        appointment_2.save()

        appointment_baseline.refresh_from_db()
        appointment_1.refresh_from_db()
        appointment_2.refresh_from_db()
        appointment_3.refresh_from_db()

        self.assertEqual(appointment_baseline.appt_status, INCOMPLETE_APPT)
        self.assertEqual(appointment_1.appt_status, INCOMPLETE_APPT)
        self.assertEqual(appointment_2.appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointment_3.appt_status, NEW_APPT)

    def test_appt_status_updater_appt_1_save_base(self):
        """Using save base and update_fields skips
        AppointmentStatusUpdater in the signal
        """
        appointments = Appointment.objects.filter(subject_identifier=self.subject_identifier)
        appointment_baseline = appointments[0]
        appointment_1 = appointments[1]
        appointment_2 = appointments[2]
        appointment_3 = appointments[3]

        self.assertEqual(appointments.count(), 4)

        # change
        appointment_baseline.appt_status = IN_PROGRESS_APPT
        appointment_baseline.save_base(update_fields=["appt_status"])
        self.assertEqual(appointment_baseline.appt_status, IN_PROGRESS_APPT)

        # check
        appointment_baseline.refresh_from_db()
        appointment_1.refresh_from_db()
        appointment_2.refresh_from_db()
        appointment_3.refresh_from_db()
        self.assertEqual(appointment_baseline.appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointment_1.appt_status, NEW_APPT)
        self.assertEqual(appointment_2.appt_status, NEW_APPT)
        self.assertEqual(appointment_3.appt_status, NEW_APPT)

        # change
        appointment_1.appt_status = IN_PROGRESS_APPT
        appointment_1.save_base(update_fields=["appt_status"])

        # check
        appointment_baseline.refresh_from_db()
        appointment_1.refresh_from_db()
        appointment_2.refresh_from_db()
        appointment_3.refresh_from_db()
        self.assertEqual(appointment_baseline.appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointment_1.appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointment_2.appt_status, NEW_APPT)
        self.assertEqual(appointment_3.appt_status, NEW_APPT)

    def test_appt_status_updater_appt_1_save_base2(self):
        """Using save base and update_fields skips
        AppointmentStatusUpdater in the signal
        """
        appointments = Appointment.objects.filter(subject_identifier=self.subject_identifier)
        appointment_baseline = appointments[0]
        appointment_1 = appointments[1]
        appointment_2 = appointments[2]
        appointment_3 = appointments[3]

        self.assertEqual(appointments.count(), 4)

        # change
        appointment_baseline.appt_status = IN_PROGRESS_APPT
        appointment_baseline.save_base()
        SubjectVisit.objects.create(
            appointment=appointment_baseline,
            report_datetime=appointment_baseline.appt_datetime,
            reason=SCHEDULED,
        )
        self.assertEqual(appointment_baseline.appt_status, IN_PROGRESS_APPT)

        # check
        appointment_baseline.refresh_from_db()
        appointment_1.refresh_from_db()
        appointment_2.refresh_from_db()
        appointment_3.refresh_from_db()
        self.assertEqual(appointment_baseline.appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointment_1.appt_status, NEW_APPT)
        self.assertEqual(appointment_2.appt_status, NEW_APPT)
        self.assertEqual(appointment_3.appt_status, NEW_APPT)

        # change
        appointment_1.appt_status = IN_PROGRESS_APPT
        appointment_1.save_base()

        # check
        appointment_baseline.refresh_from_db()
        appointment_1.refresh_from_db()
        appointment_2.refresh_from_db()
        appointment_3.refresh_from_db()
        self.assertEqual(appointment_baseline.appt_status, INCOMPLETE_APPT)
        self.assertEqual(appointment_1.appt_status, IN_PROGRESS_APPT)
        self.assertEqual(appointment_2.appt_status, NEW_APPT)
        self.assertEqual(appointment_3.appt_status, NEW_APPT)
