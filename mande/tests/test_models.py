from django.test import TestCase
from django.test import Client
from datetime import date
from mande.models import School
from mande.models import Classroom
from mande.models import AttendanceDayOffering
from mande.models import Teacher
from mande.models import IntakeSurvey
from mande.models import IntakeUpdate
from mande.models import SpiritualActivitiesSurvey
from mande.models import Academic
from mande.models import IntakeInternal
from mande.models import PublicSchoolHistory
from mande.models import StudentEvaluation
from mande.models import ExitSurvey
from mande.models import PostExitSurvey
from mande.models import Attendance
from mande.models import Discipline
from mande.models import Health
from mande.models import ClassroomEnrollment
from mande.models import ClassroomTeacher
from mande.models import NotificationLog
from mande.models import AttendanceLog
from mande.models import PublicSchoolHistory
from mande.models import AcademicMarkingPeriod
from mande.models import CurrentStudentInfo
from mande.models import EvaluationMarkingPeriod
from django.contrib.auth.models import User

class SchoolTestCase(TestCase):
    def setUp(self):
        School.objects.create(school_name="Test School", school_location="Somewhere")
        School.objects.create(school_name="Test School 2", school_location="Somewhere Else")

    def test_schools_exist(self):
        schools = School.objects.all();
        self.assertEqual(len(schools),2)
    def test_school_creation(self):
		entry = School.objects.create(school_name="test",school_location="test")
		self.assertIsInstance(entry, School)
		self.assertEqual(entry.__unicode__(), entry.school_name)
class ClassroomTestCase(TestCase):
    fixtures = ['schools.json','classrooms.json']
    def test_classroom_creation(self):
        entry = Classroom.objects.create(cohort=1,school_id=School.objects.get(pk=1),classroom_number="testclass")
        self.assertIsInstance(entry,Classroom)
        self.assertEqual(entry.__unicode__(),unicode(entry.school_id)+' - '+unicode(entry.get_cohort_display())+' - '+unicode(entry.classroom_number))
    def test_classroom_attendance_calendar_is_none(self):
        entry = Classroom.objects.create(cohort=1,school_id=School.objects.get(pk=1))
        # create attendancedayoffering
        AttendanceDayOffering.objects.create(classroom_id=entry,date="2017-01-01")
        # master calendar
        self.assertIn(AttendanceDayOffering.objects.get(classroom_id=entry),entry.getAttendanceDayOfferings())
    def test_classroom_attendance_calendar_not_none(self):
        entry = Classroom.objects.create(cohort=1,school_id=School.objects.get(pk=1),attendance_calendar=Classroom.objects.get(classroom_id=1))
        # create attendancedayoffering
        AttendanceDayOffering.objects.create(classroom_id=entry,date="2017-01-01")
        # not master calendar
        self.assertNotIn(AttendanceDayOffering.objects.get(classroom_id=entry),entry.getAttendanceDayOfferings())
class TeacherTestCase(TestCase):
    def test_teacher_creation(self):
        entry = Teacher.objects.create(name="test",active=True)
        self.assertIsInstance(entry,Teacher)
        self.assertEqual(entry.__unicode__(),unicode(entry.teacher_id)+' - '+unicode(entry.name))
class IntakeSurveyTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json','intakeupdates.json','intakeinternals.json']
    def setUp(self):
        self.intake = IntakeSurvey.objects.get(pk=2)
    def test_intakesurvey_creation(self):
        entry = IntakeSurvey.objects.create(
            date="2017-01-01",site=School.objects.get(pk=1),name="test",dob="2017-01-01",
            grade_appropriate=1,gender="F",address="test",guardian1_name="test",
            guardian1_relationship="FATHER",guardian1_phone="test",guardian1_profession="test",
            guardian1_employment=1
        )
        self.assertIsInstance(entry,IntakeSurvey)
        self.assertEqual(entry.__unicode__(),unicode(entry.student_id)+' - '+unicode(entry.name))
    def test_getRecentFields_guardian_info(self):
        IntakeUpdate.objects.create(student_id=self.intake,date="2017-01-01",guardian1_phone="123")
        IntakeUpdate.objects.create(student_id=self.intake,date="2017-01-02",guardian1_phone="")
        self.assertNotEqual(self.intake.getRecentFields()['guardian1_phone'],"123")
        self.assertEqual(self.intake.getRecentFields()['guardian1_phone'],"")
    def test_getRecentFields_other_field(self):
        IntakeUpdate.objects.create(student_id=self.intake,date="2017-01-01",address="test")
        IntakeUpdate.objects.create(student_id=self.intake,date="2017-01-02",address="")
        self.assertNotEqual(self.intake.getRecentFields()['address'],"")
        self.assertEqual(self.intake.getRecentFields()['address'],"test")
    def test_getRecentFields_church(self):
        survey1 = SpiritualActivitiesSurvey.objects.create(student_id=self.intake,date="2017-01-01",personal_attend_church="N")
        survey2 = SpiritualActivitiesSurvey.objects.create(student_id=self.intake,date="2017-01-02",personal_attend_church="Y")
        self.assertTrue(self.intake.getRecentFields().has_key("church"))
        self.assertNotEqual(self.intake.getRecentFields()["church"],survey1)
        self.assertEqual(self.intake.getRecentFields()["church"],survey2)
    def test_getNote(self):
        IntakeUpdate.objects.create(student_id=self.intake,date="2017-01-02",notes="")
        self.assertEqual(self.intake.getNotes(),[])

        update = IntakeUpdate.objects.create(student_id=self.intake,date="2017-01-02",notes="test")
        notes = []
        notes.append({'date':IntakeUpdate.objects.get(pk=update.id).date,'note':update.notes})
        self.assertEqual(self.intake.getNotes(),notes)

    def test_current_vdp_grade_promote_true(self):
        self.assertEqual(self.intake.current_vdp_grade(),1)
        Academic.objects.create(student_id=self.intake,test_date="2017-01-02",test_level=1,promote=True)
        self.assertNotEqual(self.intake.current_vdp_grade(),1)
        self.assertEqual(self.intake.current_vdp_grade(),2)
    def test_current_vdp_grade_promote_false(self):
        self.assertEqual(self.intake.current_vdp_grade(),1)
        Academic.objects.create(student_id=self.intake,test_date="2017-01-02",test_level=1,promote=False)
        self.assertNotEqual(self.intake.current_vdp_grade(),2)
        self.assertEqual(self.intake.current_vdp_grade(),1)
    def test_current_vdp_grade_promote_to_english(self):
        self.assertEqual(self.intake.current_vdp_grade(),1)
        Academic.objects.create(student_id=self.intake,test_date="2017-01-02",test_level=6,promote=True)
        self.assertNotEqual(self.intake.current_vdp_grade(),6)
        self.assertEqual(self.intake.current_vdp_grade(),50)
    def test_date_enrolled_grade(self):
        a = Academic.objects.create(student_id=self.intake,test_date="2017-01-02",test_level=1,promote=True)
        self.assertNotEqual(self.intake.date_enrolled_grade(2),"2005-07-01")
        self.assertEqual(self.intake.date_enrolled_grade(2).isoformat(),a.test_date)
    def test_age_appropriate_grade(self):
        # dob = 2005-08-01
        if date.today().month < 8:
            self.assertEqual(self.intake.age_appropriate_grade(view_date="2017-01-09"),6)
        else:
            self.assertEqual(self.intake.age_appropriate_grade(view_date="2017-01-09"),7)
    def test_get_intakeinternal(self):
        intakesurvey = IntakeSurvey.objects.create(
            date="2017-01-01",site=School.objects.get(pk=1),name="test",dob="2017-01-01",
            grade_appropriate=1,gender="F",address="test",guardian1_name="test",
            guardian1_relationship="FATHER",guardian1_phone="test",guardian1_profession="test",
            guardian1_employment=1
        )
        self.assertEqual(intakesurvey.get_intakeinternal(),"Not enrolled")
        intakeinternal = IntakeInternal.objects.create(enrollment_date="2017-01-01",student_id=intakesurvey,starting_grade=1)
        self.assertEqual(intakesurvey.get_intakeinternal(),intakeinternal)
    def test_latest_public_school(self):
        self.assertEqual(self.intake.latest_public_school(),None)
        pschool1 = PublicSchoolHistory.objects.create(student_id=self.intake,
        status="Y",grade=1,enroll_date="2017-01-01",school_name="test")
        pschool2 = PublicSchoolHistory.objects.create(student_id=self.intake,
        status="Y",grade=1,enroll_date="2017-01-02",school_name="test")
        self.assertNotEqual(self.intake.latest_public_school(),pschool1)
        self.assertEqual(self.intake.latest_public_school(),pschool2)
    def test_get_pschool(self):
        # check if not public shool
        pschool = self.intake.get_pschool()
        self.assertEqual(pschool.student_id,self.intake)
        self.assertEqual(pschool.status,"N")
        self.assertEqual(pschool.last_grade,0)
        self.assertEqual(pschool.reasons,"Not Entered")

        # check if enrolled in public school
        p = PublicSchoolHistory.objects.create(
            student_id = self.intake,
            status = "Y",
            grade = 1,
            enroll_date = "2017-01-01"
        )
        pschool1 = self.intake.get_pschool()
        self.assertEqual(pschool1.status,'Y')
        self.assertEqual(pschool1.status,p.status)
        self.assertEqual(pschool1.grade,p.grade)
        self.assertFalse(hasattr(pschool1, 'last_grade'))

        # check if not enrolled in public school
        PublicSchoolHistory.objects.create(
            student_id = self.intake,
            status = "N",
            enroll_date = "2017-01-02"
        )
        pschool2 = self.intake.get_pschool()
        self.assertTrue(hasattr(pschool2,"last_grade"))
        self.assertTrue(pschool2.status,"N")
        self.assertTrue(pschool2.last_grade,pschool1.grade)
class IntakeInternalTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_IntakeInternal_creation(self):
        entry = IntakeInternal.objects.create(
            student_id=IntakeSurvey.objects.get(pk=1),
            enrollment_date="2017-01-02",
            starting_grade=1)
        self.assertIsInstance(entry,IntakeInternal)
        self.assertEqual(entry.__unicode__(),unicode(entry.student_id))
class IntakeUpdateTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_IntakeUpdate_creation(self):
        entry = IntakeUpdate.objects.create(
            student_id=IntakeSurvey.objects.get(pk=1),
            date="2017-01-01",
            address="test")
        self.assertIsInstance(entry,IntakeUpdate)
        self.assertEqual(entry.__unicode__(),unicode(entry.date)+' - '+unicode(entry.student_id))
class StudentEvaluationTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_StudentEvaluation_creation(self):
        entry = StudentEvaluation.objects.create(
            student_id=IntakeSurvey.objects.get(pk=1),
            date="2017-01-01",
            academic_score=10)
        self.assertIsInstance(entry,StudentEvaluation)
        self.assertEqual(entry.__unicode__(),unicode(entry.date)+' - '+unicode(entry.student_id))
class SpiritualActivitiesSurveyTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_SpiritualActivitiesSurvey_creation(self):
        entry = SpiritualActivitiesSurvey.objects.create(
            student_id=IntakeSurvey.objects.get(pk=1),
            date="2017-01-01",
            personal_attend_church="Y")
        self.assertIsInstance(entry,SpiritualActivitiesSurvey)
        self.assertEqual(entry.__unicode__(),unicode(entry.date)+' - '+unicode(entry.student_id))
class ExitSurveyTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_ExitSurvey_creation(self):
        entry = ExitSurvey.objects.create(
            student_id=IntakeSurvey.objects.get(pk=1),
            survey_date="2017-01-01",
            exit_date="2017-01-01",
        )
        self.assertIsInstance(entry,ExitSurvey)
        self.assertEqual(entry.__unicode__(),unicode(entry.exit_date)+' - '+unicode(entry.student_id))
class PostExitSurveyTestCass(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_PostExitSurvey_creation(self):
        entry = PostExitSurvey.objects.create(
            student_id=IntakeSurvey.objects.get(pk=1),
            post_exit_survey_date="2017-01-01",
            exit_date="2017-01-01",
        )
        self.assertIsInstance(entry,PostExitSurvey)
        self.assertEqual(entry.__unicode__(),unicode(entry.exit_date)+' - '+unicode(entry.student_id))
class AttendanceDayOfferingTestCass(TestCase):
    fixtures = ['schools.json','classrooms.json']
    def test_AttendanceDayOffering_creation(self):
        entry = AttendanceDayOffering.objects.create(
            classroom_id=Classroom.objects.get(pk=1),
            date="2017-01-01",
            offered="Y",
        )
        self.assertIsInstance(entry,AttendanceDayOffering)
        self.assertEqual(entry.__unicode__(),unicode(entry.classroom_id)+' - '+unicode(entry.date))
class AttendanceTestCass(TestCase):
    fixtures = ['schools.json','classrooms.json','intakesurveys.json']
    def test_Attendance_creation(self):
        entry = Attendance.objects.create(
            student_id=IntakeSurvey.objects.get(pk=1),
            classroom = Classroom.objects.get(pk=1),
            date="2017-01-01",
            attendance="P",
        )
        self.assertIsInstance(entry,Attendance)
        self.assertEqual(entry.__unicode__(),unicode(entry.date) + ' - '+entry.attendance+' - ' + unicode(entry.student_id))
class DisciplineTestCass(TestCase):
    fixtures = ['schools.json','classrooms.json','intakesurveys.json']
    def test_Discipline_creation(self):
        entry = Discipline.objects.create(
            student_id=IntakeSurvey.objects.get(pk=1),
            classroom_id = Classroom.objects.get(pk=1),
            incident_date="2017-01-01",
            incident_code=1,
            incident_description="test"
        )
        self.assertIsInstance(entry,Discipline)
        self.assertEqual(entry.__unicode__(),unicode(entry.incident_date)+' - '+unicode(entry.student_id))
class AcademicTestCass(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_Academic_creation(self):
        entry = Academic.objects.create(
            student_id=IntakeSurvey.objects.get(pk=1),
            test_level=1,
            test_date="2017-01-01",
            test_grade_math=1,
            test_grade_khmer = 1,
        )
        self.assertIsInstance(entry,Academic)
        self.assertEqual(entry.__unicode__(),unicode(entry.test_date)+' - '+unicode(entry.student_id))
class HealthTestCass(TestCase):
    fixtures = ['schools.json','classrooms.json','intakesurveys.json']
    def test_Health_creation(self):
        entry = Health.objects.create(
            student_id=IntakeSurvey.objects.get(pk=1),
            appointment_date="2017-01-01",
            appointment_type="CHECKUP",
            height=1,
            weight=1,
        )
        self.assertIsInstance(entry,Health)
        self.assertEqual(entry.__unicode__(),unicode(entry.appointment_date) + ' - '+entry.appointment_type+ ' - '+unicode(entry.student_id))
class ClassroomEnrollmentTestCass(TestCase):
    fixtures = ['schools.json','classrooms.json','intakesurveys.json']
    def test_ClassroomEnrollment_creation(self):
        entry = ClassroomEnrollment.objects.create(
            student_id=IntakeSurvey.objects.get(pk=1),
            classroom_id=Classroom.objects.get(pk=1),
            enrollment_date="2017-01-01",
            drop_date="2017-01-01",
        )
        self.assertIsInstance(entry,ClassroomEnrollment)
        self.assertEqual(entry.__unicode__(),unicode(entry.student_id)+' - '+unicode(entry.classroom_id))
class ClassroomTeacherTestCass(TestCase):
    fixtures = ['schools.json','classrooms.json','teachers.json']
    def test_ClassroomTeacher_creation(self):
        entry = ClassroomTeacher.objects.create(
            teacher_id=Teacher.objects.get(pk=1),
            classroom_id=Classroom.objects.get(pk=1)
        )
        self.assertIsInstance(entry,ClassroomTeacher)
        self.assertEqual(entry.__unicode__(),unicode(entry.teacher_id)+' - '+unicode(entry.classroom_id))
class NotificationLogTestCass(TestCase):
    fixtures = ['users.json']
    def test_NotificationLog_creation(self):
        entry = NotificationLog.objects.create(
            date="2017-01-01",
            user=User.objects.get(pk=1),
            user_generated=True,
            text="test",
            font_awesome_icon="fa-user-plus"
        )
        self.assertIsInstance(entry,NotificationLog)
        self.assertEqual(entry.__unicode__(),unicode(entry.date) + ' - '+ unicode(entry.user) + ' - ' + unicode(entry.text))
class AttendanceLogTestCass(TestCase):
    fixtures = ['schools.json','classrooms.json']
    def test_AttendanceLog_creation(self):
        entry = AttendanceLog.objects.create(
            date="2017-01-01",
            classroom=Classroom.objects.get(pk=1),
            absent=1,
            present=1,
        )
        self.assertIsInstance(entry,AttendanceLog)
        self.assertEqual(entry.__unicode__(),unicode(entry.classroom) + ' - '+ unicode(entry.date))
class PublicSchoolHistoryTestCass(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_PublicSchoolHistory_creation(self):
        entry = PublicSchoolHistory.objects.create(
            student_id=IntakeSurvey.objects.get(pk=1),
            status="Y",
            grade=1,
            enroll_date="2017-01-01",
            school_name="test"
        )
        self.assertIsInstance(entry,PublicSchoolHistory)
        self.assertEqual(entry.__unicode__(),unicode(entry.student_id) + ' - '+ unicode(entry.grade))
class AcademicMarkingPeriodTestCass(TestCase):
    def test_AcademicMarkingPeriod_creation(self):
        entry = AcademicMarkingPeriod.objects.create(
            description="test",
            test_date="2017-01-01",
            marking_period_start="2017-01-01",
            marking_period_end="2017-01-01"
        )
        self.assertIsInstance(entry,AcademicMarkingPeriod)
        self.assertEqual(entry.__unicode__(),unicode(entry.description) + ' - '+ unicode(entry.test_date))
class EvaluationMarkingPeriodTestCass(TestCase):
    def test_evaluation_marking_period_creation(self):
        entry = EvaluationMarkingPeriod.objects.create(
            description="test",
            test_date="2017-01-01",
            marking_period_start="2017-01-01",
            marking_period_end="2017-01-01"
        )
        self.assertIsInstance(entry,EvaluationMarkingPeriod)
        self.assertEqual(entry.__unicode__(),unicode(entry.description) + ' - '+ unicode(entry.test_date))
