from django.db import models
from django.contrib.auth.models import User
import datetime

GENDERS = (
	('M', 'Male'),
	('F', 'Female'),
)

YN = (
	('Y', 'Yes'),
	('N', 'No'),
	('NA', 'Not Applicable'),
)

SITES = (
	(1,'PKPN'),
	(2,'PPT'),
	(3,'TK')

)
EMPLOYMENT = (
	('1', '1 - Very Low Wage'),
	('2', '2'),
	('3', '3'),
	('4', '4'),
	('5', '5'),
	('6', '6'),
	('7', '7'),
	('8', '8'),
	('9', '9'),
	('10', 'Middle Class (or higher)'),
)

GRADES = (
	(-1,'Not Applicable'),
	(0,'Not Enrolled'),
	(1,'Grade 1'),
	(2,'Grade 2'),
	(3,'Grade 3'),
	(4,'Grade 4'),
	(5,'Grade 5'),
	(6,'Grade 6'),
	(7,'Grade 7'),
	(8,'Grade 8'),
	(9,'Grade 9'),
	(10,'Grade 10'),
	(11,'Grade 11'),
	(12,'Grade 12'),
	(50,'English'),
	(60,'Computers'),
	(70,'Vietnamese')
)

SCORES = (
	(1,'1 - Little to no Growth'),
	(2,'2'),
	(3,'3'),
	(4,'4'),
	(5,'5 - Huge Growth'),

)

COHORTS = (
	(2014,'2014-2015'),
	(2015,'2015-2016'),
	(2016,'2016-2017'),
	(2017,'2017-2018'),
	(2018,'2018-2019'),
	(2019,'2019-2020'),
	(2020,'2020-2021'),
	(2021,'2021-2022'),
	(2022,'2022-2023'),
	(2023,'2023-2024'),
	(2024,'2024-2025'),
)

ATTENDANCE_CODES = (
	('P','Present'),
	('UA','Unapproved Absence'),
	('AA','Approved Absence'),
)

DISCIPLINE_CODES = (
	(1,'Bullying'),
	(2,'Cheating'),
	(3,'Lying'),
	(4,'Cursing'),
	(5,'Other'),
)


APPOINTMENT_TYPES = (
	('DENTAL', 'Dental'),
	('CHECKUP', 'Check-up'),
)

EXIT_REASONS = (
	('MOVING', 'Moving to another location'),
	('MOTIVATION','Don\'t want to continue.'),
	('EMPLOYMENT','Got a job'),
	('OTHER','Other')
)
class School(models.Model):
	school_id = models.AutoField(primary_key=True)
	school_name = models.CharField('School Code',max_length=128)
	school_location = models.CharField('Location',max_length=128)
	def __unicode__(self):
		return self.school_name

class Classroom(models.Model):
	classroom_id = models.AutoField(primary_key=True)
	cohort = models.IntegerField('Target Grade',choices=GRADES,default=2014,max_length=8)
	school_id = models.ForeignKey(School)
	classroom_number = models.CharField('Description',max_length=16)
	classroom_location = models.CharField('Classroom Location',max_length=128)
	def __unicode__(self):
		return unicode(self.school_id)+ ' - '+ unicode(self.classroom_number)+' - '+unicode(self.classroom_location)

class Teacher(models.Model):
	teacher_id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=32,default='')
	def __unicode__(self):
		return unicode(self.teacher_id)+ ' - '+ unicode(self.name)

class IntakeSurvey(models.Model):

	student_id = models.AutoField(primary_key=True)
	date = models.DateField('Date of Intake')
	site = models.ForeignKey('School')

	#Student Biographical Information
	name = models.CharField('Name',max_length=64,default='')
	dob = models.DateField('DOB')
	grade_appropriate = models.IntegerField('Appropriate Grade',choices=GRADES,default=1)
	#graduation = models.DateField('Expected 6th Grade Graduation') #can calculate this based on dob
	gender = models.CharField(max_length=1,choices=GENDERS,default='M')
	address = models.TextField('Home Address')
	enrolled = models.CharField('Currently enrolled in (public) school?',max_length=2,choices=YN,default='N')
	grade_current = models.IntegerField('Current grade in [public] school (if enrolled)',choices=GRADES,default=-1)
	grade_last = models.IntegerField('Last grade attended (if not enrolled)',choices=GRADES,default=-1)
	reasons = models.TextField('Reasons for not attening',blank=True)

	#Father's Information
	father_name = models.CharField('Father\'s Name',max_length=64)
	father_phone = models.CharField('Father\'s Phone',max_length=128)
	father_profession = models.CharField('Father\'s Profession',max_length=64)
	father_employment = models.CharField('Father\'s Employment',max_length=1,choices=EMPLOYMENT,default=1)

	#Mother's Information
	mother_name = models.CharField('Mother\'s Name',max_length=64)
	mother_phone = models.CharField('Mother\'s Phone',max_length=128)
	mother_profession = models.CharField('Mother\'s Profession',max_length=64)
	mother_employment= models.CharField('Mother\'s Employment',max_length=1,choices=EMPLOYMENT,default=1)

	#Household Information
	minors = models.IntegerField('Number of children living in household (including student)',default=0)
	minors_in_school = models.IntegerField('Number of children enrolled in school last year',default=0)
	minors_working = models.IntegerField('Number of children under 18 working 15+ hours per week',default=0)
	minors_profession = models.CharField('What are they doing for work?',max_length=256, blank=True)
	minors_encouraged = models.CharField('Did you encourage them to take this job?',max_length=2,choices=YN)
	minors_training = models.CharField('Did they receive any vocational training?',max_length=2,choices=YN)
	minors_training_type = models.CharField('What kind of vocational training did they receive?',max_length=256,blank=True)

	notes = models.TextField(blank=True)

	def __unicode__(self):
	   return unicode(self.student_id)+' - '+self.name

class IntakeInternal(models.Model):
	student_id = models.ForeignKey(IntakeSurvey)
	enrollment_date = models.DateField('Enrollment Date')
	starting_grade = models.IntegerField(choices=GRADES,default=1)

	def __unicode__(self):
		return unicode(self.student_id)

class IntakeUpdate(models.Model):

	student_id = models.ForeignKey(IntakeSurvey)
	date = models.DateTimeField('Date of Update')
	address = models.TextField('Home Address')

	father_name = models.CharField('Father\'s Name',max_length=64,blank=True)
	father_phone = models.CharField('Father\'s Phone',max_length=128,blank=True)
	father_profession = models.CharField('Father\'s Profession',max_length=64,default='NA',blank=True)
	father_employment = models.CharField('Father\'s Employment',max_length=1,choices=EMPLOYMENT,default=1)


	mother_name = models.CharField('Mother\'s Name',max_length=64,blank=True)
	mother_phone = models.CharField('Mother\'s Phone',max_length=128,blank=True)
	mother_profession = models.CharField('Mother\'s Profession',max_length=64,default='NA',blank=True)
	mother_employment= models.CharField('Mother\'s Employment',max_length=1,choices=EMPLOYMENT,default=1)

	minors = models.IntegerField(default=0)
	minors_in_school = models.IntegerField(default=0)
	minors_working = models.IntegerField(default=0)
	minors_profession = models.CharField('What are they doing for work?',max_length=256, default='NA')
	minors_encouraged = models.CharField('Did you encourage them to take this job?',max_length=2,choices=YN,default='NA')
	minors_training = models.CharField('Did they receive any vocational training?',max_length=2,choices=YN,default='NA')
	minors_training_type = models.CharField('What kind of vocational training did they receive?',max_length=256,default='NA',blank=True)

	enrolled = models.CharField('Currently enrolled in formal school?',max_length=2,choices=YN,default='N')
	grade_current = models.IntegerField('Current grade in (public) school?',choices=GRADES,default=1)
	grade_last = models.IntegerField(choices=GRADES,default=1)
	reasons = models.TextField(default='NA')
	notes = models.TextField(default='NA',blank=True)

	def __unicode__(self):
		return unicode(self.date)+' - '+unicode(self.student_id)

class StudentEvaluation(models.Model):
	student_id = models.ForeignKey(IntakeSurvey)
	date = models.DateField('Observation Date')
	academic_score = models.IntegerField('Academic Growth Score')
	study_score = models.IntegerField('Study/Learning Skills Score')
	personal_score = models.IntegerField('Life Skills/Personal Development Score')
	hygiene_score = models.IntegerField('Hygeine Score')
	faith_score = models.IntegerField('Christian Growth Score')
	comments = models.TextField('Overall comments',blank=True)

	def __unicode__(self):
		return unicode(self.date)+' - '+unicode(self.student_id)

class SpiritualActivitiesSurvey(models.Model):
	student_id = models.ForeignKey(IntakeSurvey)
	date = models.DateField('Survey Date')
	family_attend_church = models.CharField('Does your family currently attend church?',max_length=2,choices=YN,default='NA')
	personal_attend_church = models.CharField('Do you currently attend church?',max_length=2,choices=YN,default='NA')
	personal_prayer = models.CharField('Have you prayed on your own within the last week?',max_length=2,choices=YN,default='NA')
	personal_baptism = models.CharField('Have you been baptized?',max_length=2,choices=YN,default='NA')
	personal_bible_reading = models.CharField('Have you spent time reading the Bible in the last week?',max_length=2,choices=YN,default='NA')
	personal_prayer_aloud = models.CharField('Have you prayed aloud in the last week?',max_length=2,choices=YN,default='NA')
	def __unicode__(self):
		return unicode(self.date)+' - '+unicode(self.student_id)

class ExitSurvey(models.Model):
	student_id = models.ForeignKey(IntakeSurvey)
	survey_date = models.DateField('Exit Survey Performed',default=datetime.date.today)
	exit_date = models.DateField('Exit Date')
	early_exit = models.CharField('Early Exit (before achieveing age appropriate level)',max_length=2,choices=YN,default='NA')
	last_grade = models.IntegerField('Public School Grade at exit',choices=GRADES,default=1)
	early_exit_reason = models.CharField('Reason for Leaving Early',choices=EXIT_REASONS,max_length=32)
	early_exit_comment = models.TextField('Comment',blank=True)
	secondary_enrollment = models.CharField('Plan to enroll in secondary school?',max_length=2,choices=YN,default='NA')
	def __unicode__(self):
		return unicode(self.exit_date)+' - '+unicode(self.student_id)

class PostExitSurvey(models.Model):
	student_id = models.ForeignKey(IntakeSurvey)
	post_exit_survey_date = models.DateField('Date of Survey',default=datetime.date.today)
	exit_date = models.DateField('Exit Date')
	early_exit = models.CharField('Early (before achieving grade level) Exit',max_length=2,choices=YN,default='NA')
	father_profession = models.CharField('Father\'s Profession',max_length=64,default='NA')
	father_employment = models.CharField('Father\'s Employment',max_length=1,choices=EMPLOYMENT,default=1)
	mother_profession = models.CharField('Mother\'s Profession',max_length=64,default='NA')
	mother_employment= models.CharField('Mother\'s Employment',max_length=1,choices=EMPLOYMENT,default=1)
	minors = models.IntegerField('How many children (under 18) are working?',default=0)
	enrolled = models.CharField('Currently in school? [Primary Child]',max_length=2,choices=YN,default='NA')
	grade_current = models.IntegerField('Current Grade in formal school (if in school)',choices=GRADES,default=1)
	grade_previous = models.IntegerField('Last Grade attended (if not in school)',choices=GRADES,default=1)
	reasons = models.TextField('Reasons for not attending',blank=True)
	def __unicode__(self):
		return unicode(self.exit_date)+' - '+unicode(self.student_id)

class AttendanceDayOffering(models.Model):
	classroom_id = models.ForeignKey(Classroom)
	date = models.DateField()
	offered = models.CharField(max_length=2,choices=YN,default='Y')
	def __unicode__(self):
		return unicode(self.classroom_id)+' - '+unicode(self.date)

class Attendance(models.Model):
	student_id = models.ForeignKey(IntakeSurvey)
	date = models.DateField('Attendance Day',default=datetime.date.today)
	attendance = models.CharField(max_length=2,choices=ATTENDANCE_CODES,default='P',null=True)
	notes = models.CharField(max_length=256,blank=True)
	def __unicode__(self):
		return unicode(self.date) + ': '+ self.attendance + ' - ' + unicode(self.student_id)
	class Meta:
		unique_together = (('student_id', 'date'),)

class Discipline(models.Model):
	student_id = models.ForeignKey(IntakeSurvey)
	classroom_id = models.ForeignKey(Classroom)
	incident_date = models.DateField('Incident Date',default=datetime.date.today)
	incident_code = models.IntegerField(choices=DISCIPLINE_CODES,default=1)
	incident_description = models.CharField(max_length=256,default='')

	def __unicode__(self):
			return unicode(self.incident_date)+ ':'+unicode(self.student_id)

class Academic(models.Model):
	student_id = models.ForeignKey(IntakeSurvey)
	test_date = models.DateField(default=datetime.date.today)
	test_level = models.IntegerField(choices=GRADES,default=0)
	test_grade_math = models.IntegerField(max_length=3,null=True,blank=True)
	test_grade_khmer = models.IntegerField(max_length=3,null=True,blank=True)
	promote = models.BooleanField(default=False)

	def __unicode__(self):
		return unicode(self.test_date)+ ':'+unicode(self.student_id)
		unique_together = (('student_id','test_date'))

class Health(models.Model):
	student_id = models.ForeignKey(IntakeSurvey)
	appointment_date = models.DateField(default=datetime.date.today)
	appointment_type = models.CharField(choices=APPOINTMENT_TYPES,default='Check-up',max_length=16)
	height = models.DecimalField(max_digits=5,decimal_places=2)
	weight = models.DecimalField(max_digits=5,decimal_places=2)
	extractions = models.IntegerField(max_length=1,default=0)
	sealent = models.IntegerField(max_length=2,default=0)
	filling = models.IntegerField(max_length=2,default=0)
	endo = models.IntegerField(max_length=2,default=0)
	scaling = models.IntegerField(max_length=2,default=0)
	pulped = models.IntegerField(max_length=2,default=0)
	xray = models.IntegerField(max_length=2,default=0)
	notes = models.TextField(blank=True)

	def __unicode__(self):
		return unicode(self.appointment_date) + ': '+self.appointment_type+ ' - '+unicode(self.student_id)

class ClassroomEnrollment(models.Model):
	student_id = models.ForeignKey(IntakeSurvey)
	classroom_id = models.ForeignKey(Classroom)
	enrollment_date = models.DateField(default=datetime.date.today)
	drop_date = models.DateField(null=True,blank=True)

	def __unicode__(self):
		return unicode(self.student_id)+unicode(self.classroom_id)

class ClassroomTeacher(models.Model):
	classroom_id = models.ForeignKey(Classroom)
	teacher_id = models.ForeignKey(Teacher)
	def __unicode__(self):
		return unicode(self.teacher_id)+unicode(self.classroom_id)

class NotificationLog(models.Model):
	date = models.DateTimeField(auto_now=True)
	user = models.ForeignKey(User, blank=True)
	user_generated = models.BooleanField(default=True)
	text = models.TextField()
	font_awesome_icon = models.TextField(max_length=16,default="fa-bolt") #a font-awesome icon name

	def __unicode__(self):
		return unicode(self.date) + ' - '+ unicode(self.user) + ' ' + unicode(self.text)

	class Meta:
		get_latest_by = 'date'
