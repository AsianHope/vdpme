from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test import Client
from mande.forms import IntakeSurveyForm
from mande.forms import IntakeInternalForm
from mande.forms import IntakeUpdateForm
from mande.forms import ExitSurveyForm
from mande.forms import PostExitSurveyForm
from mande.forms import SpiritualActivitiesSurveyForm
from mande.forms import DisciplineForm
from mande.forms import TeacherForm
from mande.forms import ClassroomForm
from mande.forms import ClassroomTeacherForm
from mande.forms import ClassroomEnrollmentForm
from mande.forms import IndividualClassroomEnrollmentForm
from mande.forms import AttendanceForm
from mande.forms import AcademicForm
from mande.forms import HealthForm
from mande.forms import HealthDentalForm
from mande.forms import HealthCheckupForm
from mande.forms import StudentEvaluationForm
from mande.forms import StudentPublicSchoolHistoryForm
from mande.forms import AcademicMarkingPeriodForm
from mande.forms import EvaluationMarkingPeriodForm


class IntakeSurveyTestCase(TestCase):
    fixtures = ['schools.json']
    def test_IntakeSurveyForm_valid(self):
        data = {
            "date":"2017-01-01",
            "site":1,
            "dob": "2000-01-01",
            "name":"abc",
            "gender":"F",
            "guardian1_name":"abc",
            "guardian1_relationship":"FATHER",
            "guardian1_phone":"00000",
            "guardian1_profession":"test",
            "guardian1_employment":1,
            "minors":0,
            "minors_in_public_school":0,
            "minors_in_other_school":0,
            "address": "test", "notes": "test",
            "enrollment_date":"2017-01-01",
            "starting_grade":1
        }
        form = IntakeSurveyForm(data)
        self.assertTrue(form.is_valid())
    def test_IntakeSurveyForm_invalid(self):
        data = {
            "date":"2017-01-01",
            "site":1,
            "dob": "2000-01-01",
            "name":"abc",
            "gender":"F",
            "guardian1_name":"abc",
            "guardian1_relationship":"FATHER",
            "guardian1_phone":"00000",
            "guardian1_profession":"test",
            "guardian1_employment":1,
            "minors":0,
            "minors_in_public_school":0,
            "minors_in_other_school":0,
            "address": "test", "notes": "test",
        }
        form = IntakeSurveyForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
            {'enrollment_date': [u'This field is required.'], 'starting_grade': [u'This field is required.']}
        )
class IntakeInternalFormTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_IntakeInternalForm_valid(self):
        data = {
            "student_id":1,
            "enrollment_date":"2017-01-01",
            "starting_grade":1
        }
        form = IntakeInternalForm(data)
        self.assertTrue(form.is_valid())
    def test_IntakeInternalForm_invalid(self):
        data={
            "enrollment_date":"2017-01-01",
            "starting_grade":1
        }
        form = IntakeInternalForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
            {'student_id': [u'This field is required.']}
        )
class IntakeUpdateFormTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_IntakeUpdateForm_valid(self):
        data = {
            "date":"2017-01-01",
            "student_id":1,
            "address":"test",
            "guardian1_relationship":"FATHER",
            "guardian1_employment":2,
            "minors":1,
            "minors_in_public_school":1,
            "minors_in_other_school":0,
        }
        form = IntakeUpdateForm(data)
        self.assertTrue(form.is_valid())
    def test_IntakeUpdateForm_invalid(self):
        data = {
            "date":"2017-01-01",
            "address":"test",
            "guardian1_relationship":"FATHER",
            "guardian1_employment":2,
            "minors":1,
            "minors_in_public_school":1,
            "minors_in_other_school":0,
        }
        form = IntakeUpdateForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
            {'student_id': [u'This field is required.']}
        )
class ExitSurveyFormTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_ExitSurveyForm_valid(self):
        data = {
            "survey_date":"2017-01-01",
            "student_id":1,
            "exit_date":"2017-01-01",
            "early_exit":"Y",
            "last_grade":0,
            "early_exit_reason":"MOVING",
            "secondary_enrollment":"Y"
        }
        form = ExitSurveyForm(data)
        self.assertTrue(form.is_valid())
    def test_ExitSurveyForm_invalid(self):
        data = {
            "survey_date":"2017-01-01",
            "exit_date":"2017-01-01",
            "early_exit":"Y",
            "last_grade":2,
            "early_exit_reason":"MOVING",
            "early_exit_comment":"test",
            "secondary_enrollment":"N",
        }
        form = ExitSurveyForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
            {'student_id': [u'This field is required.']}
        )

class PostExitSurveyFormTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_PostExitSurveyForm_valid(self):
        data = {
            "post_exit_survey_date":"2017-01-01",
            "student_id":1,
            "exit_date":"2017-01-01",
            "early_exit":"Y",
            "guardian1_relationship":"FATHER",
            "guardian1_profession":1,
            "guardian1_employment":1,
            "minors":1,
            "enrolled":"Y",
            "grade_current":1,
            "grade_previous":1
        }
        form = PostExitSurveyForm(data)
        self.assertTrue(form.is_valid())
    def test_PostExitSurveyForm_invalid(self):
            data = {
                "post_exit_survey_date":"2017-01-01",
                "exit_date":"2017-01-01",
                "early_exit":"Y",
                "guardian1_relationship":"FATHER",
                "guardian1_profession":1,
                "guardian1_employment":1,
                "minors":1,
                "enrolled":"Y",
                "grade_current":1,
                "grade_previous":1
            }
            form = PostExitSurveyForm(data)
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors,
                {'student_id': [u'This field is required.']}
            )
class SpiritualActivitiesSurveyFormTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_SpiritualActivitiesSurveyForm_valid(self):
        data = {
            "date":"2017-01-01",
            "student_id":1,
            "personal_attend_church":"Y",
            "frequency_of_attending":"EVERY_WEEK"
        }
        data2 = {
            "date":"2017-01-01",
            "student_id":1,
            "personal_attend_church":"N",
        }
        form = SpiritualActivitiesSurveyForm(data)
        form2 = SpiritualActivitiesSurveyForm(data2)
        self.assertTrue(form.is_valid())
        self.assertTrue(form2.is_valid())
    def test_SpiritualActivitiesSurveyForm_invalid(self):
            data = {
                "date":"2017-01-01",
                "student_id":1,
                "personal_attend_church":"Y"
            }
            form = SpiritualActivitiesSurveyForm(data)
            self.assertFalse(form.is_valid())
            # frequency_of_attending is required when personal_attend_church = Yes
            self.assertEqual(form.errors,
                {'frequency_of_attending': [u'This field is required.']}
            )
class DisciplineFormTestCase(TestCase):
    fixtures = ['classrooms.json','schools.json','intakesurveys.json']
    def test_DisciplineForm_valid(self):
        data = {
            "student_id":1,
            "classroom_id":1,
            "incident_date":"2017-01-01",
            "incident_code":1,
            "incident_description":"test"
        }
        form = DisciplineForm(data)
        self.assertTrue(form.is_valid())
    def test_DisciplineForm_invalid(self):
            data = {
                "classroom_id":1,
                "incident_date":"2017-01-01",
                "incident_code":1,
                "incident_description":"test"
            }
            form = DisciplineForm(data)
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors,
                {'student_id': [u'This field is required.']}
            )
class TeacherFormTestCase(TestCase):
    def test_TeacherForm_valid(self):
        data = {
            "name":"test",
        }
        form = TeacherForm(data)
        self.assertTrue(form.is_valid())
    def test_TeacherForm_invalid(self):
            data = {}
            form = TeacherForm(data)
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors,
                {'name': [u'This field is required.']}
            )
class ClassroomFormTestCase(TestCase):
    fixtures = ['schools.json']
    def test_ClassroomForm_valid(self):
        data={
        "cohort":1,
        "school_id":1,
        }
        form = ClassroomForm(data)

        self.assertTrue(form.is_valid())
    def test_ClassroomForm_invalid(self):
            data={
            "cohort":1,
            }
            form = ClassroomForm(data)
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors,
                {'school_id': [u'This field is required.']}
            )
class ClassroomTeacherFormTestCase(TestCase):
    fixtures = ['schools.json','classrooms.json','teachers.json']
    def test_ClassroomTeacherForm_valid(self):
        data={
        "classroom_id":1,
        "teacher_id":1,
        }
        form = ClassroomTeacherForm(data)
        self.assertTrue(form.is_valid())
    def test_ClassroomTeacherForm_invalid(self):
            data={}
            form = ClassroomTeacherForm(data)
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors,
                {'classroom_id': [u'This field is required.'],'teacher_id':[u'This field is required.']}
            )
class ClassroomEnrollmentFormTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json','classrooms.json']
    def test_ClassroomEnrollmentForm_invalid_passing_student_id(self):
        data={
        "student_id":1,
        "enrollment_date":"2017-01-01",
        "classroom_id":1
        }
        form = ClassroomEnrollmentForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
            {'student_id':[u'Enter a list of values.']}
        )
    def test_ClassroomEnrollmentForm_invalid(self):
            data={
                "enrollment_date":"2017-01-01",
                'classroom_id':1
            }
            form = ClassroomEnrollmentForm(data)
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors,
                {
                'student_id':[u'This field is required.'],
                }
            )

class IndividualClassroomEnrollmentFormTestCase(TestCase):
    fixtures = ['classrooms.json','schools.json','intakesurveys.json']
    def test_IndividualClassroomEnrollmentForm_valid(self):
        data={
            "student_id":1,
            "classroom_id":1,
            "drop_date":"2017-01-01"
        }
        form = IndividualClassroomEnrollmentForm(data)
        self.assertTrue(form.is_valid())
    def test_IndividualClassroomEnrollmentForm_invalid(self):
            data={
                "classroom_id":1,
                "drop_date":"2017-01-01"
            }
            form = IndividualClassroomEnrollmentForm(data)
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors,
                {'student_id': [u'This field is required.']}
            )
class AttendanceFormTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_AttendanceForm_valid(self):
        data={
            "student_id":1,
            "date":"2017-01-01",
            "attendance":"P"
        }
        form = AttendanceForm(data)
        self.assertTrue(form.is_valid())
    def test_AttendanceForm_invalid(self):
            data={
                "date":"2017-01-01",
                "attendance":"P"
            }
            form = AttendanceForm(data)
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors,
                {'student_id': [u'This field is required.']}
            )
class AcademicFormTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_AcademicForm_valid(self):
        data={
            "student_id":1,
            "test_date":"2017-01-01",
            "test_level":1,
            "promote" : False,
            "test_grade_math":1,
            "test_grade_khmer":1
        }
        form = AcademicForm(data)
        self.assertTrue(form.is_valid())
    def test_AcademicForm_invalid(self):
            data={
                "test_date":"2017-01-01",
                "test_level":1,
                "promote" : False,
                "test_grade_math":1,
                "test_grade_khmer":1
            }
            form = AcademicForm(data)
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors,
                {'student_id': [u'This field is required.']}
            )
class HealthFormTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_HealthForm_valid(self):
        data={
            "student_id":1,
            "appointment_date":"2017-01-01",
            "appointment_type":"DENTAL",
        }
        form = HealthForm(data)
        self.assertTrue(form.is_valid())
    def test_HealthForm_invalid(self):
        data={
            "appointment_date":"2017-01-01",
            "appointment_type":"DENTAL",
        }
        form = HealthForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
            {'student_id': [u'This field is required.']}
        )
class HealthDentalFormTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_HealthDentalForm_valid(self):
        data={
            "student_id":1,
            "appointment_date":"2017-01-01",
            "appointment_type":"DENTAL",
        }
        form = HealthDentalForm(data)
        self.assertTrue(form.is_valid())
    def test_HealthDentalForm_invalid(self):
        data={
            "appointment_date":"2017-01-01",
            "appointment_type":"DENTAL",
        }
        form = HealthDentalForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
            {'student_id': [u'This field is required.']}
        )
class HealthCheckupFormTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_HealthCheckupForm_valid(self):
        data={
            "student_id":1,
            "appointment_date":"2017-01-01",
            "appointment_type":"CHECKUP",
        }
        form = HealthCheckupForm(data)
        self.assertTrue(form.is_valid())
    def test_HealthCheckupForm_invalid(self):
        data={
            "appointment_date":"2017-01-01",
            "appointment_type":"CHECKUP",
        }
        form = HealthCheckupForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
            {'student_id': [u'This field is required.']}
        )
class StudentEvaluationFormTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_StudentEvaluationForm_valid(self):
        data={
            "student_id":1,
            "date":"2017-01-01",
            "test_level":1,
            "academic_score":1,
            "study_score":1,
            "personal_score":1,
            "hygiene_score":1,
            "faith_score":1,
            "comments":"test"
        }
        form = StudentEvaluationForm(data)
        self.assertTrue(form.is_valid())
    def test_StudentEvaluationForm_invalid(self):
        data={
            "date":"2017-01-01",
            "test_level":1,
            "academic_score":1,
            "study_score":1,
            "personal_score":1,
            "hygiene_score":1,
            "faith_score":1,
            "comments":"test"
        }
        form = StudentEvaluationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
            {'student_id': [u'This field is required.']}
        )
class StudentPublicSchoolHistoryFormTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json']
    def test_StudentPublicSchoolHistoryForm_valid(self):
        enrolled={
            "student_id":1,
            "status":"Y",
            "grade":1,
            "enroll_date":"2017-01-01",
            "drop_date":"2017-01-01",
            "school_name":"test",
        }
        not_enrolled={
            "student_id":1,
            "status":"N",
            "enroll_date":"2017-01-01",
            "drop_date":"2017-01-01",
            "reasons":"test",
        }
        form = StudentPublicSchoolHistoryForm(enrolled)
        form2 = StudentPublicSchoolHistoryForm(not_enrolled)
        self.assertTrue(form.is_valid())
        self.assertTrue(form2.is_valid())
    def test_StudentPublicSchoolHistoryForm_invalid_enrolled(self):
        data={
            "student_id":1,
            "status":"Y",
            "grade":1,
            "enroll_date":"2017-01-01",
            "drop_date":"2017-01-01",
        }
        form = StudentPublicSchoolHistoryForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
            {'school_name': [u'This field is required.']}
        )
    def test_StudentPublicSchoolHistoryForm_invalid_notenrolled(self):
        data={
            "student_id":1,
            "status":"N",
            "enroll_date":"2017-01-01",
            "drop_date":"2017-01-01",
        }
        form = StudentPublicSchoolHistoryForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
            {'reasons': [u'This field is required.']}
        )
    def test_StudentPublicSchoolHistoryForm_invalid_date(self):
        data={
            "student_id":1,
            "status":"N",
            "enroll_date":"2018-01-01",
            "drop_date":"2017-01-01",
            "reasons":"test",
        }
        form = StudentPublicSchoolHistoryForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
            {'drop_date': [u'To date should be greater than From date']}
        )
class AcademicMarkingPeriodFormTestCase(TestCase):
    def test_AcademicMarkingPeriodForm_valid(self):
        data={
            "description":"test",
            "test_date":"2017-01-01",
            "marking_period_start":"2017-01-01",
            "marking_period_end":"2017-01-01",
        }
        form = AcademicMarkingPeriodForm(data)
        self.assertTrue(form.is_valid())
    def test_AcademicMarkingPeriodForm_invalid(self):
        data={
            "description":"test",
            "marking_period_start":"2017-01-01",
            "marking_period_end":"2017-01-01",
        }
        form = AcademicMarkingPeriodForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
            {'test_date': [u'This field is required.']}
        )


class EvaluationMarkingPeriodFormTestCase(TestCase):
    def test_evaluation_marking_period_form_valid(self):
        data={
            "description":"test",
            "test_date":"2017-01-01",
            "marking_period_start":"2017-01-01",
            "marking_period_end":"2017-01-01",
        }
        form = EvaluationMarkingPeriodForm(data)
        self.assertTrue(form.is_valid())
        
    def test_evaluation_marking_period_form_invalid(self):
        data={
            "description":"test",
            "marking_period_start":"2017-01-01",
            "marking_period_end":"2017-01-01",
        }
        form = EvaluationMarkingPeriodForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
            {'test_date': [u'This field is required.']}
        )
