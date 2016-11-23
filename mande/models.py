from django.db import models
from django.contrib.auth.models import User
import datetime
from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from mande.permissions import perms_required

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
	(2,'TK'),
	(3,'PPT')

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
	(70,'Vietnamese'),
	(999,'No Grade / Never Studied')

)

SCORES = (
	(None, '-----'),
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
#Attendance codes with an A in their code are counted as absences
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

RELATIONSHIPS = (
	('FATHER','Father'),
	('MOTHER','Mother'),
	('GRANDFATHER','Grandfather'),
	('GRANDMOTHER','Grandmother'),
	('AUNT','Aunt'),
	('UNCLE','Uncle'),
	('OTHER','Other'),
	('NONE','No guardian')
)
PUBLIC_SCHOOL_GRADES = (
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
	(12,'Grade 12')
)
STATUS = (
	('COMPLETED','Completed'),
	('DROPPED','Dropped out'),
	('ON_GOING','On going')
)
def generate_activity_permissions(perms_required):
	perms = []
	for key,activity in perms_required.iteritems():
		perms.append(('view_'+key,('Can view '+key)[:30]))
	perms = tuple(perms)
	return perms
testperm = generate_activity_permissions(perms_required)

class JethroPerms(models.Model):
	class Meta:
		permissions = testperm

class School(models.Model):
	school_id = models.AutoField(primary_key=True)
	school_name = models.CharField('School Code',max_length=128)
	school_location = models.CharField('Location',max_length=128)
	def __unicode__(self):
		return self.school_name

class Classroom(models.Model):
	classroom_id = models.AutoField(primary_key=True)
	cohort = models.IntegerField('Target Grade',choices=GRADES,default=2014)
	school_id = models.ForeignKey(School)
	classroom_number = models.CharField('Description',max_length=16,blank=True)
	classroom_location = models.CharField('Classroom Location',max_length=128,blank=True)
	active = models.BooleanField('Active',default=True)
	attendance_calendar = models.ForeignKey('self',default=None,blank=True,null=True)

	def getAttendanceDayOfferings(self,attendance_date=None):

		attendance_calendar_to_fetch = self
		if self.attendance_calendar is not None:
			attendance_calendar_to_fetch = self.attendance_calendar
		if attendance_date is not None:
			offered = AttendanceDayOffering.objects.filter(classroom_id=attendance_calendar_to_fetch,
                                                			date=attendance_date)
		else:
			offered = AttendanceDayOffering.objects.filter(classroom_id=attendance_calendar_to_fetch)

		return offered


	def __unicode__(self):
		return unicode(self.school_id)+ ' - '+ unicode(self.get_cohort_display())+' - '+unicode(self.classroom_number)

class Teacher(models.Model):
	teacher_id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=32,default='',unique=True)
	active = models.BooleanField(default=True)
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

	gender = models.CharField(max_length=1,choices=GENDERS,default='M')
	address = models.TextField('Home Address')
	enrolled = models.CharField('Currently enrolled in (public) school?',max_length=2,choices=YN,default='N')
	grade_current = models.IntegerField('Current grade in [public] school (if enrolled)',choices=GRADES,default=-1)
	grade_last = models.IntegerField('Last grade attended (if not enrolled)',choices=GRADES,default=-1)
	public_school_name = models.CharField('Public School Name',max_length=128,blank=True)
	reasons = models.TextField('Reasons for not attending',blank=True)

	#Guardian 1's Information
	guardian1_name = models.CharField('Guardian 1\'s Name',max_length=64)
	guardian1_relationship = models.CharField('Guardian 1\'s relationship to child',max_length=64,choices=RELATIONSHIPS,default='FATHER')
	guardian1_phone = models.CharField('Guardian 1\'s Phone',max_length=128)
	guardian1_profession = models.CharField('Guardian 1\'s Profession',max_length=64)
	guardian1_employment = models.CharField('Guardian 1\'s Employment',max_length=1,choices=EMPLOYMENT,default=1)


	#Guardian 2's Information
	guardian2_name = models.CharField('Guardian 2\'s Name',max_length=64,blank=True,null=True)
	guardian2_relationship = models.CharField('Guardian 2\'s relationship to child',max_length=64,blank=True,null=True,choices=RELATIONSHIPS,default='MOTHER')
	guardian2_phone = models.CharField('Guardian 2\'s Phone',max_length=128,blank=True,null=True)
	guardian2_profession = models.CharField('Guardian 2\'s Profession',max_length=64,default='NA',blank=True,null=True)
	guardian2_employment= models.CharField('Guardian 2\'s Employment',max_length=1,choices=EMPLOYMENT,default=1,blank=True,null=True)

	#Household Information
	minors = models.IntegerField('Number of children living in household (including student)',default=0)
	minors_in_public_school = models.IntegerField('Number of children enrolled in public school last year',default=0)
	minors_in_other_school = models.IntegerField('Number of children enrolled in private school last year',default=0)
	minors_working = models.IntegerField('Number of children under 18 working 15+ hours per week',default=0)
	minors_profession = models.CharField('What are they doing for work?',max_length=256, blank=True)
	minors_encouraged = models.CharField('Did you encourage them to take this job?',max_length=2,choices=YN,default='NA')
	minors_training = models.CharField('Did they receive any vocational training?',max_length=2,choices=YN,default='NA')
	minors_training_type = models.CharField('What kind of vocational training did they receive?',max_length=256,blank=True)

	notes = models.TextField(blank=True)

	def __unicode__(self):
	   return unicode(self.student_id)+' - '+self.name

	#return the most up to date information
	def getRecentFields(self,view_date=None):
		list_of_field = [
			'guardian1_name',
			'guardian1_relationship',
			'guardian1_phone',
			'guardian1_profession',
			'guardian1_employment',
			'guardian2_name',
			'guardian2_relationship',
			'guardian2_phone',
			'guardian2_profession',
			'guardian2_employment'
			]
		recent = {}
		#seed recent with the intake survey
		for field in self._meta.fields:
			recent[field.name] = getattr(self,field.name)
		#loop through all updates, oldest to most recent
		if view_date != None:
			updates = IntakeUpdate.objects.all().filter(student_id=self.student_id).filter(date__lte=view_date).order_by('date')
		else:
			updates = IntakeUpdate.objects.all().filter(student_id=self.student_id).filter().order_by('date')
		for update in updates:
			for field in self._meta.fields:
				try:
					attr = getattr(update,field.name)
					# if field in guardian
					if field.name in list_of_field:
						recent[field.name] = attr
					else:
						if attr is not None and field.name != 'student_id':
							if isinstance(attr, (str, unicode)):
								if len(attr)>0: #for unicode things, only if they're of value
									recent[field.name] = attr #most recent non null update wins!
							else:
								recent[field.name] = attr #most recent non null update wins!
				except (AttributeError, TypeError) as e:
					#print 'caught:  '+str(type(e))+' while processing '+field.name+'()'+str(type(attr))+')'
					pass
		return recent

	def getNotes(self):
		if self.notes is not None and len(self.notes)>1:
			notes=[{'date': self.date, 'note':self.notes}]
		else:
			notes=[]
		updates = IntakeUpdate.objects.all().filter(student_id=self.student_id).filter().order_by('date')
		updates = updates.exclude(notes=None).exclude(notes='')
		for update in updates:
			notes.append({'date':update.date,'note':update.notes})

		return notes;

	def current_vdp_grade(self,view_date=datetime.datetime.now()):
		academics = self.academic_set.all().filter(test_date__lte=view_date).order_by('-test_level')
		intake = self.intakeinternal_set.all().filter().order_by('-enrollment_date')
		if len(intake) > 0:
			recent_intake = intake[0]
		else:
			recent_intake = 'Not enrolled'

		try:
		    #their current grade is one more than that of the last test they passed
			current_grade = (academics.filter(promote=True).latest('test_level').test_level)+1
			if current_grade > 6:
				current_grade = 50 #magic numbers are bad. should pull this from models.py
		except ObjectDoesNotExist:
			current_grade = recent_intake.starting_grade if type(recent_intake) != str else 0

		return current_grade
	# -------------------------------------------
	def date_enrolled_grade(self,current_grade):
		grade = current_grade-1
		academics = self.academic_set.all().filter().order_by('-test_level')
		intake = self.intakeinternal_set.all().filter().order_by('-enrollment_date')
		if len(intake) > 0:
			recent_intake = intake[0]
		else:
			recent_intake = 'Not enrolled'

		try:
			date_enrolled_grade = academics.filter(promote=True,test_level=grade).latest('test_level').test_date
		except ObjectDoesNotExist:
			date_enrolled_grade = recent_intake.enrollment_date
		return date_enrolled_grade
	# -------------------------------------------
	def age_appropriate_grade(self,view_date=datetime.datetime.now()):
		if self.dob == None:
		    return 'DOB not entered'
		# if view_date passed with date type or not
		if isinstance(view_date, datetime.date) == False:
			# convert to date
			view_date = datetime.datetime.strptime(view_date, "%Y-%m-%d").date()
		else:
			view_date = view_date

		#Look at calendar year child was born in to calculate their age
		approximate_age = view_date.year - self.dob.year
		#if today is before grades change in August
		if date.today().month < 8:
		    age_appropriate_grade = approximate_age - 6
		else:
		    age_appropriate_grade = approximate_age - 5

		return age_appropriate_grade

class IntakeInternal(models.Model):
	student_id = models.ForeignKey(IntakeSurvey,unique=True)
	enrollment_date = models.DateField('Enrollment Date')
	starting_grade = models.IntegerField(choices=GRADES,default=1)

	def __unicode__(self):
		return unicode(self.student_id)

class IntakeUpdate(models.Model):

	student_id = models.ForeignKey(IntakeSurvey)
	date = models.DateTimeField('Date of Update')
	address = models.TextField('Home Address')

	guardian1_name = models.CharField('Guardian 1\'s Name',max_length=64,blank=True)
	guardian1_relationship = models.CharField('Guardian 1\'s relationship to child',max_length=64,choices=RELATIONSHIPS,default='FATHER')
	guardian1_phone = models.CharField('Guardian 1\'s Phone',max_length=128,blank=True)
	guardian1_profession = models.CharField('Guardian 1\'s Profession',max_length=64,default='NA',blank=True)
	guardian1_employment = models.CharField('Guardian 1\'s Employment',max_length=1,choices=EMPLOYMENT,default=1)


	guardian2_name = models.CharField('Guardian 2\'s Name',max_length=64,blank=True,null=True)
	guardian2_relationship = models.CharField('Guardian 2\'s relationship to child',max_length=64,blank=True,null=True,choices=RELATIONSHIPS,default='MOTHER')
	guardian2_phone = models.CharField('Guardian 2\'s Phone',max_length=128,blank=True,null=True)
	guardian2_profession = models.CharField('Guardian 2\'s Profession',max_length=64,default='NA',blank=True,null=True)
	guardian2_employment= models.CharField('Guardian 2\'s Employment',max_length=1,choices=EMPLOYMENT,default=1,blank=True,null=True)

	minors = models.IntegerField('Number of children living in household (including student)',default=0)
	minors_in_public_school = models.IntegerField('Number of children enrolled in public school last year',default=0)
	minors_in_other_school = models.IntegerField('Number of children enrolled in private school last year',default=0)
	minors_working = models.IntegerField('Number of minors working',default=0)
	minors_profession = models.CharField('What are they doing for work?',max_length=256, default='NA')
	minors_encouraged = models.CharField('Did you encourage them to take this job?',max_length=2,choices=YN,default='NA')
	minors_training = models.CharField('Did they receive any vocational training?',max_length=2,choices=YN,default='NA')
	minors_training_type = models.CharField('What kind of vocational training did they receive?',max_length=256,default='NA',blank=True)

	enrolled = models.CharField('Currently enrolled in formal school?',max_length=2,choices=YN,default='N')
	grade_current = models.IntegerField('Current grade in (public) school?',choices=GRADES,default=1)
	grade_last = models.IntegerField('Last grade in public school (if not currently enrolled)',choices=GRADES,default='-1')
	public_school_name = models.CharField('Public School Name',max_length=128,blank=True)
	reasons = models.TextField('Reasons for not attending school',default='NA',blank=True,null=True)
	notes = models.TextField(default='NA',blank=True)

	def __unicode__(self):
		return unicode(self.date)+' - '+unicode(self.student_id)

class StudentEvaluation(models.Model):
	student_id = models.ForeignKey(IntakeSurvey)
	date = models.DateField('Observation Date')
	academic_score = models.IntegerField('Academic Growth Score',blank=True,null=True,default=None)
	#academic_notes = models.CharField('Academic Growth Notes',blank=True,null=True)
	study_score = models.IntegerField('Study/Learning Skills Score',blank=True,null=True,default=None)
	#study_notes = models.CharField('Academic Growth Notes',blank=True,null=True)
	personal_score = models.IntegerField('Life Skills/Personal Development Score',blank=True,null=True,default=None)
	#personal_notes = models.CharField('Life Skills/Personal Development Notes',blank=True,null=True)
	hygiene_score = models.IntegerField('Hygeine Knowledge Score',blank=True,null=True,default=None)
	#hygiene_notes = models.CharField('Hygeine Knowledge Notes',blank=True,null=True)
	faith_score = models.IntegerField('Christian Growth Score',blank=True,null=True,default=None)
	#faith_notes = models.CharField('Christian Growth Notes',blank=True,null=True)
	#replacing individual notes fields with overall comments
	comments = models.TextField('Overall comments',blank=True)

	def __unicode__(self):
		return unicode(self.date)+' - '+unicode(self.student_id)
	class Meta:
		unique_together = (('student_id', 'date'),)


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

	guardian1_relationship = models.CharField('Guardian 1\'s relationship to child',max_length=64,choices=RELATIONSHIPS,default='FATHER')
	guardian1_profession = models.CharField('Guardian 1\'s Profession',max_length=64,default='NA')
	guardian1_employment = models.CharField('Guardian 1\'s Employment',max_length=1,choices=EMPLOYMENT,default=1)

	guardian2_relationship = models.CharField('Guardian 2\'s relationship to child',max_length=64,blank=True,null=True,choices=RELATIONSHIPS,default='MOTHER')
	guardian2_profession = models.CharField('Guardian 2\'s Profession',max_length=64,default='NA',blank=True,null=True)
	guardian2_employment= models.CharField('Guardian 2\'s Employment',max_length=1,choices=EMPLOYMENT,default=1,blank=True,null=True)

	minors = models.IntegerField('How many children in the household?',default=0)
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
	class Meta:
		unique_together = (('classroom_id','date'))


class Attendance(models.Model):
	student_id = models.ForeignKey(IntakeSurvey)
	classroom = models.ForeignKey(Classroom, blank=True,null=True)
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
	test_grade_math = models.IntegerField(null=True,blank=True)
	test_grade_khmer = models.IntegerField(null=True,blank=True)
	promote = models.BooleanField(default=False)

	def __unicode__(self):
		return unicode(self.test_date)+ ':'+unicode(self.student_id)
	class Meta:
		unique_together = (('student_id','test_date','test_level','promote'))

class Health(models.Model):
	student_id = models.ForeignKey(IntakeSurvey)
	appointment_date = models.DateField(default=datetime.date.today)
	appointment_type = models.CharField(choices=APPOINTMENT_TYPES,default='Check-up',max_length=16)
	height = models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True) 	#Medical
	weight = models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True) 	#Medical
	extractions = models.IntegerField(default=0,null=True,blank=True) 	#dental
	sealent = models.IntegerField(default=0,null=True,blank=True) 		#dental
	filling = models.IntegerField(default=0,null=True,blank=True)		#dental
	endo = models.IntegerField(default=0,null=True,blank=True)			#dental
	scaling = models.IntegerField(default=0,null=True,blank=True)		#dental
	pulped = models.IntegerField(default=0,null=True,blank=True)			#dental
	xray = models.IntegerField(default=0,null=True,blank=True)			#dental
	notes = models.TextField(blank=True)									#all

	def __unicode__(self):
		return unicode(self.appointment_date) + ': '+self.appointment_type+ ' - '+unicode(self.student_id)

	class Meta:
		unique_together = (('student_id','appointment_date','appointment_type'))

class ClassroomEnrollment(models.Model):
	student_id = models.ForeignKey(IntakeSurvey)
	classroom_id = models.ForeignKey(Classroom)
	enrollment_date = models.DateField(default=datetime.date.today)
	drop_date = models.DateField(null=True,blank=True)

	def __unicode__(self):
		return unicode(self.student_id)+unicode(self.classroom_id)
	class Meta:
		unique_together = (('student_id','classroom_id'))

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

class AttendanceLog(models.Model):
	classroom = models.ForeignKey(Classroom)
	date = models.DateField()
	absent = models.IntegerField(default=0)
	present = models.IntegerField(default=0)

	def __unicode__(self):
		return unicode(self.classroom) + ': '+ unicode(self.date)
	class Meta:
			unique_together = (('classroom','date'))

class PublicSchoolHistory(models.Model):
	student_id = models.ForeignKey(IntakeSurvey)
	academic_year = models.IntegerField(choices=COHORTS)
	grade = models.IntegerField('Public School Grade',choices=PUBLIC_SCHOOL_GRADES)
	status = models.CharField(choices=STATUS,default='COMPLETED',max_length=16)
	enroll_date = models.DateField()
	drop_date = models.DateField(null=True,blank=True)
	school_name = models.CharField('Public School Name',max_length=128,blank=True)
	reasons = models.TextField('Reasons for not attending',blank=True)
	def __unicode__(self):
		return unicode(self.student_id) + ' - '+ unicode(self.grade)
