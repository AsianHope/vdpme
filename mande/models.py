from django.db import models
from django.contrib.auth.models import User
import datetime
from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from mande.permissions import perms_required
from django.utils.translation import ugettext_lazy as _


GENDERS = (
	('M', _('Male')),
	('F', _('Female')),
)

YN = (
	('Y', _('Yes')),
	('N', _('No')),
	('NA', _('Not Applicable')),
)
YESNO = (
	('Y', _('Yes')),
	('N', _('No')),
)

SITES = (
	(1,'PKPN'),
	(2,'TK'),
	(3,'PPT')

)
EMPLOYMENT = (
	('1', _('1 - Very Low Wage')),
	('2', _('2')),
	('3', _('3')),
	('4', _('4')),
	('5', _('5')),
	('6', _('6')),
	('7', _('7')),
	('8', _('8')),
	('9', _('9')),
	('10', _('Middle Class (or higher)')),
)

GRADES = (
	(-1,_('Not Applicable')),
	(0,_('Not Enrolled')),
	(1,_('Grade 1')),
	(2,_('Grade 2')),
	(3,_('Grade 3')),
	(4,_('Grade 4')),
	(5,_('Grade 5')),
	(6,_('Grade 6')),
	(7,_('Grade 7')),
	(8,_('Grade 8')),
	(9,_('Grade 9')),
	(10,_('Grade 10')),
	(11,_('Grade 11')),
	(12,_('Grade 12')),
	(50,_('English')),
	(60,_('Computers')),
	(70,_('Vietnamese')),
	(999,_('No Grade / Never Studied'))

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
	('P', _('Present')),
	('UA', _('Unapproved Absence')),
	('AA', _('Approved Absence')),
)

DISCIPLINE_CODES = (
	(1, _('Bullying')),
	(2, _('Cheating')),
	(3, _('Lying')),
	(4, _('Cursing')),
	(5, _('Other')),
)


APPOINTMENT_TYPES = (
	('DENTAL', _('Dental')),
	('CHECKUP', _('Check-up')),
)

EXIT_REASONS = (
	('MOVING', _('Moving to another location')),
	('MOTIVATION',_('Don\'t want to continue.')),
	('EMPLOYMENT',_('Got a job')),
	('OTHER',_('Other'))
)

RELATIONSHIPS = (
	('FATHER',_('Father')),
	('MOTHER',_('Mother')),
	('GRANDFATHER',_('Grandfather')),
	('GRANDMOTHER',_('Grandmother')),
	('AUNT',_('Aunt')),
	('UNCLE',_('Uncle')),
	('OTHER',_('Other')),
	('NONE',_('No guardian'))
)
PUBLIC_SCHOOL_GRADES = (
	(1, _('Grade 1')),
	(2, _('Grade 2')),
	(3, _('Grade 3')),
	(4, _('Grade 4')),
	(5, _('Grade 5')),
	(6, _('Grade 6')),
	(7, _('Grade 7')),
	(8, _('Grade 8')),
	(9, _('Grade 9')),
	(10, _('Grade 10')),
	(11, _('Grade 11')),
	(12, _('Grade 12'))
)
STATUS = (
	('COMPLETED', _('Completed')),
	('DROPPED', _('Dropped out')),
	('ON_GOING', _('On going'))
)
FREQUENCY = (
	('NA',_('Not Applicable')),
	('EVERY_WEEK', _('Almost every week')),
	('EVERY_MONTH', _('Once every 1-2 months')),
	('EVERY_YEAR', _('Once or twice per year'))
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
	school_id = models.AutoField(_('School ID'),primary_key=True)
	school_name = models.CharField(_('School Code'),max_length=128)
	school_location = models.CharField(_('Location'),max_length=128)
	def __unicode__(self):
		return self.school_name

class Classroom(models.Model):
	classroom_id = models.AutoField(_('Classroom ID'),primary_key=True)
	cohort = models.IntegerField(_('Target Grade'),choices=GRADES,default=2014)
	school_id = models.ForeignKey(School,verbose_name=_('School ID'))
	classroom_number = models.CharField(_('Description'),max_length=16,blank=True)
	classroom_location = models.CharField(_('Classroom Location'),max_length=128,blank=True)
	active = models.BooleanField(_('Active'),default=True)
	attendance_calendar = models.ForeignKey('self',default=None,blank=True,null=True,verbose_name=_('Attendance calendar'))

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
	teacher_id = models.AutoField(primary_key=True,verbose_name=_('Teacher ID'))
	name = models.CharField(_('Name'),max_length=32,default='',unique=True)
	active = models.BooleanField(_('Active'),default=True)
	def __unicode__(self):
		return unicode(self.teacher_id)+ ' - '+ unicode(self.name)

class IntakeSurvey(models.Model):

	student_id = models.AutoField(_('Student ID'),primary_key=True)
	date = models.DateField(_('Date of Intake'))
	site = models.ForeignKey('School',verbose_name=_('Site'))

	#Student Biographical Information
	name = models.CharField(_('Name'),max_length=64,default='')
	dob = models.DateField(_('DOB'))
	grade_appropriate = models.IntegerField(_('Appropriate Grade'),choices=GRADES,default=1)

	gender = models.CharField(_('Gender'),max_length=1,choices=GENDERS,default='M')
	address = models.TextField(_('Home Address'))

	#Guardian 1's Information
	guardian1_name = models.CharField(_('Guardian 1\'s Name'),max_length=64)
	guardian1_relationship = models.CharField(_('Guardian 1\'s relationship to child'),max_length=64,choices=RELATIONSHIPS,default='FATHER')
	guardian1_phone = models.CharField(_('Guardian 1\'s Phone'),max_length=128)
	guardian1_profession = models.CharField(_('Guardian 1\'s Profession'),max_length=64)
	guardian1_employment = models.CharField(_('Guardian 1\'s Employment'),max_length=1,choices=EMPLOYMENT,default=1)


	#Guardian 2's Information
	guardian2_name = models.CharField(_('Guardian 2\'s Name'),max_length=64,blank=True,null=True)
	guardian2_relationship = models.CharField(_('Guardian 2\'s relationship to child'),max_length=64,blank=True,null=True,choices=RELATIONSHIPS,default='MOTHER')
	guardian2_phone = models.CharField(_('Guardian 2\'s Phone'),max_length=128,blank=True,null=True)
	guardian2_profession = models.CharField(_('Guardian 2\'s Profession'),max_length=64,default='NA',blank=True,null=True)
	guardian2_employment= models.CharField(_('Guardian 2\'s Employment'),max_length=1,choices=EMPLOYMENT,default=1,blank=True,null=True)

	#Household Information
	minors = models.IntegerField(_('Number of children living in household (including student)'),default=0)
	minors_in_public_school = models.IntegerField(_('Number of children enrolled in public school last year'),default=0)
	minors_in_other_school = models.IntegerField(_('Number of children enrolled in private school last year'),default=0)
	minors_working = models.IntegerField(_('Number of children under 18 working 15+ hours per week'),default=0)
	minors_profession = models.CharField(_('What are they doing for work?'),max_length=256, blank=True)
	minors_encouraged = models.CharField(_('Did you encourage them to take this job?'),max_length=2,choices=YN,default='NA')
	minors_training = models.CharField(_('Did they receive any vocational training?'),max_length=2,choices=YN,default='NA')
	minors_training_type = models.CharField(_('What kind of vocational training did they receive?'),max_length=256,blank=True)

	notes = models.TextField(_('Notes'),blank=True)

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
			'guardian2_employment',
			]
		recent = {}
		# get latest SpiritualActivitiesSurvey
		try:
			recent['church']=SpiritualActivitiesSurvey.objects.all().filter(student_id=self.student_id).latest('date')
			pass
		except:
			pass

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

	def get_intakeinternal(self):
		intake = self.intakeinternal_set.all().filter().order_by('-enrollment_date')
		if len(intake) > 0:
			recent_intake = intake[0]
		else:
			recent_intake = 'Not enrolled'
	    	return recent_intake
	def latest_public_school(self):
		try:
			pschool = self.publicschoolhistory_set.all().filter().latest('enroll_date')
		except ObjectDoesNotExist:
			pschool = None
		return pschool
class IntakeInternal(models.Model):
	student_id = models.ForeignKey(IntakeSurvey,unique=True,verbose_name=_('Student ID'))
	enrollment_date = models.DateField(_('Enrollment Date'))
	starting_grade = models.IntegerField(_('Starting grade'),choices=GRADES,default=1)

	def __unicode__(self):
		return unicode(self.student_id)

class IntakeUpdate(models.Model):

	student_id = models.ForeignKey(IntakeSurvey,verbose_name=_('Student ID'))
	date = models.DateTimeField(_('Date of Update'))
	address = models.TextField(_('Home Address'))

	guardian1_name = models.CharField(_('Guardian 1\'s Name'),max_length=64,blank=True)
	guardian1_relationship = models.CharField(_('Guardian 1\'s relationship to child'),max_length=64,choices=RELATIONSHIPS,default='FATHER')
	guardian1_phone = models.CharField(_('Guardian 1\'s Phone'),max_length=128,blank=True)
	guardian1_profession = models.CharField(_('Guardian 1\'s Profession'),max_length=64,default='NA',blank=True)
	guardian1_employment = models.CharField(_('Guardian 1\'s Employment'),max_length=1,choices=EMPLOYMENT,default=1)


	guardian2_name = models.CharField(_('Guardian 2\'s Name'),max_length=64,blank=True,null=True)
	guardian2_relationship = models.CharField(_('Guardian 2\'s relationship to child'),max_length=64,blank=True,null=True,choices=RELATIONSHIPS,default='MOTHER')
	guardian2_phone = models.CharField(_('Guardian 2\'s Phone'),max_length=128,blank=True,null=True)
	guardian2_profession = models.CharField(_('Guardian 2\'s Profession'),max_length=64,default='NA',blank=True,null=True)
	guardian2_employment= models.CharField(_('Guardian 2\'s Employment'),max_length=1,choices=EMPLOYMENT,default=1,blank=True,null=True)

	minors = models.IntegerField(_('Number of children living in household (including student)'),default=0)
	minors_in_public_school = models.IntegerField(_('Number of children enrolled in public school last year'),default=0)
	minors_in_other_school = models.IntegerField(_('Number of children enrolled in private school last year'),default=0)
	minors_working = models.IntegerField(_('Number of minors working'),default=0)
	minors_profession = models.CharField(_('What are they doing for work?'),max_length=256, default='NA')
	minors_encouraged = models.CharField(_('Did you encourage them to take this job?'),max_length=2,choices=YN,default='NA')
	minors_training = models.CharField(_('Did they receive any vocational training?'),max_length=2,choices=YN,default='NA')
	minors_training_type = models.CharField(_('What kind of vocational training did they receive?'),max_length=256,default='NA',blank=True)

	notes = models.TextField('Notes',default='NA',blank=True)

	def __unicode__(self):
		return unicode(self.date)+' - '+unicode(self.student_id)

class StudentEvaluation(models.Model):
	student_id = models.ForeignKey(IntakeSurvey,verbose_name=_('Student ID'))
	date = models.DateField(_('Observation Date'))
	academic_score = models.IntegerField(_('Academic Growth Score'),blank=True,null=True,default=None)
	#academic_notes = models.CharField('Academic Growth Notes',blank=True,null=True)
	study_score = models.IntegerField(_('Study/Learning Skills Score'),blank=True,null=True,default=None)
	#study_notes = models.CharField('Academic Growth Notes',blank=True,null=True)
	personal_score = models.IntegerField(_('Life Skills/Personal Development Score'),blank=True,null=True,default=None)
	#personal_notes = models.CharField('Life Skills/Personal Development Notes',blank=True,null=True)
	hygiene_score = models.IntegerField(_('Hygiene Knowledge Score'),blank=True,null=True,default=None)
	#hygiene_notes = models.CharField('Hygeine Knowledge Notes',blank=True,null=True)
	faith_score = models.IntegerField(_('Christian Growth Score'),blank=True,null=True,default=None)
	#faith_notes = models.CharField('Christian Growth Notes',blank=True,null=True)
	#replacing individual notes fields with overall comments
	comments = models.TextField(_('Overall Comments'),blank=True)

	def __unicode__(self):
		return unicode(self.date)+' - '+unicode(self.student_id)
	class Meta:
		unique_together = (('student_id', 'date'),)


class SpiritualActivitiesSurvey(models.Model):
	student_id = models.ForeignKey(IntakeSurvey,verbose_name=_('Student ID'))
	date = models.DateField(_('Survey Date'),default=datetime.date.today)
	family_attend_church = models.CharField(_('Does your family currently attend church?'),max_length=2,choices=YN,default='NA')
	personal_attend_church = models.CharField(_('Do you currently attend church?'),max_length=2,choices=YN,default='NA')
	frequency_of_attending = models.CharField(_('Frequency of Attending'),choices=FREQUENCY,default='NA',max_length=16)
	church_name = models.CharField(_('Church Name'),max_length=128,blank=True,null=True)
	personal_prayer = models.CharField(_('Have you prayed on your own within the last week?'),max_length=2,choices=YN,default='NA')
	personal_baptism = models.CharField(_('Have you been baptized?'),max_length=2,choices=YN,default='NA')
	personal_bible_reading = models.CharField(_('Have you spent time reading the Bible in the last week?'),max_length=2,choices=YN,default='NA')
	personal_prayer_aloud = models.CharField(_('Have you prayed aloud in the last week?'),max_length=2,choices=YN,default='NA')
	def __unicode__(self):
		return unicode(self.date)+' - '+unicode(self.student_id)


class ExitSurvey(models.Model):
	student_id = models.ForeignKey(IntakeSurvey,verbose_name=_('Student ID'))
	survey_date = models.DateField(_('Exit Survey Performed'),default=datetime.date.today)
	exit_date = models.DateField(_('Exit Date'))
	early_exit = models.CharField(_('Early Exit (before achieveing age appropriate level)'),max_length=2,choices=YN,default='NA')
	last_grade = models.IntegerField(_('Public School Grade at exit'),choices=GRADES,default=1)
	early_exit_reason = models.CharField(_('Reason for Leaving Early'),choices=EXIT_REASONS,max_length=32)
	early_exit_comment = models.TextField(_('Comment'),blank=True)
	secondary_enrollment = models.CharField(_('Plan to enroll in secondary school?'),max_length=2,choices=YN,default='NA')
	def __unicode__(self):
		return unicode(self.exit_date)+' - '+unicode(self.student_id)

class PostExitSurvey(models.Model):
	student_id = models.ForeignKey(IntakeSurvey,verbose_name=_('Student ID'))
	post_exit_survey_date = models.DateField(_('Date of Survey'),default=datetime.date.today)
	exit_date = models.DateField(_('Exit Date'))
	early_exit = models.CharField(_('Early (before achieving grade level) Exit'),max_length=2,choices=YN,default='NA')

	guardian1_relationship = models.CharField(_('Guardian 1\'s relationship to child'),max_length=64,choices=RELATIONSHIPS,default='FATHER')
	guardian1_profession = models.CharField(_('Guardian 1\'s Profession'),max_length=64,default='NA')
	guardian1_employment = models.CharField(_('Guardian 1\'s Employment'),max_length=1,choices=EMPLOYMENT,default=1)

	guardian2_relationship = models.CharField(_('Guardian 2\'s relationship to child'),max_length=64,blank=True,null=True,choices=RELATIONSHIPS,default='MOTHER')
	guardian2_profession = models.CharField(_('Guardian 2\'s Profession'),max_length=64,default='NA',blank=True,null=True)
	guardian2_employment= models.CharField(_('Guardian 2\'s Employment'),max_length=1,choices=EMPLOYMENT,default=1,blank=True,null=True)

	minors = models.IntegerField(_('How many children in the household?'),default=0)
	enrolled = models.CharField(_('Currently in school? [Primary Child]'),max_length=2,choices=YN,default='NA')
	grade_current = models.IntegerField(_('Current Grade in formal school (if in school)'),choices=GRADES,default=1)
	grade_previous = models.IntegerField(_('Last Grade attended (if not in school)'),choices=GRADES,default=1)
	reasons = models.TextField(_('Reasons for not attending'),blank=True)
	def __unicode__(self):
		return unicode(self.exit_date)+' - '+unicode(self.student_id)

class AttendanceDayOffering(models.Model):
	classroom_id = models.ForeignKey(Classroom,verbose_name=_('Classroom ID'))
	date = models.DateField(_('Date'))
	offered = models.CharField(_('Offered'),max_length=2,choices=YN,default='Y')
	def __unicode__(self):
		return unicode(self.classroom_id)+' - '+unicode(self.date)
	class Meta:
		unique_together = (('classroom_id','date'))


class Attendance(models.Model):
	student_id = models.ForeignKey(IntakeSurvey,verbose_name=_('Student ID'))
	classroom = models.ForeignKey(Classroom, blank=True,null=True,verbose_name=_('Classroom'))
	date = models.DateField(_('Attendance Day'),default=datetime.date.today)
	attendance = models.CharField(_('Attendance'),max_length=2,choices=ATTENDANCE_CODES,default='P',null=True)
	notes = models.CharField(_('Notes'),max_length=256,blank=True)
	def __unicode__(self):
		return unicode(self.date) + ': '+ self.attendance + ' - ' + unicode(self.student_id)
	class Meta:
		unique_together = (('student_id', 'date'),)

class Discipline(models.Model):
	student_id = models.ForeignKey(IntakeSurvey,verbose_name=_('Student ID'))
	classroom_id = models.ForeignKey(Classroom,verbose_name=_('Classroom ID'))
	incident_date = models.DateField(_('Incident Date'),default=datetime.date.today)
	incident_code = models.IntegerField(_('Incident code'),choices=DISCIPLINE_CODES,default=1)
	incident_description = models.CharField(_('Incident description'),max_length=256,default='')

	def __unicode__(self):
			return unicode(self.incident_date)+ ':'+unicode(self.student_id)

class Academic(models.Model):
	student_id = models.ForeignKey(IntakeSurvey,verbose_name=_('Student ID'))
	test_date = models.DateField(_('Test Date'),default=datetime.date.today)
	test_level = models.IntegerField(_('Level'),choices=GRADES,default=0)
	test_grade_math = models.IntegerField(_('Math'),null=True,blank=True)
	test_grade_khmer = models.IntegerField(_('Khmer'),null=True,blank=True)
	promote = models.BooleanField(_('Promote'),default=False)

	def __unicode__(self):
		return unicode(self.test_date)+ ':'+unicode(self.student_id)
	class Meta:
		unique_together = (('student_id','test_date','test_level','promote'))

class Health(models.Model):
	student_id = models.ForeignKey(IntakeSurvey,verbose_name=_('Student ID'))
	appointment_date = models.DateField(_("Appointment date"),default=datetime.date.today)
	appointment_type = models.CharField(_("Appointment type"),choices=APPOINTMENT_TYPES,default='Check-up',max_length=16)
	height = models.DecimalField(_("Height"),max_digits=5,decimal_places=2,null=True,blank=True) 	#Medical
	weight = models.DecimalField(_("Weight"),max_digits=5,decimal_places=2,null=True,blank=True) 	#Medical
	extractions = models.IntegerField(_("Extractions"),default=0,null=True,blank=True) 	#dental
	sealent = models.IntegerField(_("Sealent"),default=0,null=True,blank=True) 		#dental
	filling = models.IntegerField(_("Filling"),default=0,null=True,blank=True)		#dental
	endo = models.IntegerField(_("Endo"),default=0,null=True,blank=True)			#dental
	scaling = models.IntegerField(_("Scaling"),default=0,null=True,blank=True)		#dental
	pulped = models.IntegerField(_("Pulped"),default=0,null=True,blank=True)			#dental
	xray = models.IntegerField(_("Xray"),default=0,null=True,blank=True)			#dental
	notes = models.TextField(_("Notes"),blank=True)									#all

	def __unicode__(self):
		return unicode(self.appointment_date) + ': '+self.appointment_type+ ' - '+unicode(self.student_id)

	class Meta:
		unique_together = (('student_id','appointment_date','appointment_type'))

class ClassroomEnrollment(models.Model):
	student_id = models.ForeignKey(IntakeSurvey,verbose_name=_('Student ID'))
	classroom_id = models.ForeignKey(Classroom,verbose_name=_('Classroom ID'))
	enrollment_date = models.DateField('Enrollment Date',default=datetime.date.today)
	drop_date = models.DateField(_('Drop Date'),null=True,blank=True)

	def __unicode__(self):
		return unicode(self.student_id)+unicode(self.classroom_id)
	class Meta:
		unique_together = (('student_id','classroom_id'))

class ClassroomTeacher(models.Model):
	classroom_id = models.ForeignKey(Classroom,verbose_name=_('Classroom ID'))
	teacher_id = models.ForeignKey(Teacher,verbose_name=_('Teacher ID'))
	def __unicode__(self):
		return unicode(self.teacher_id)+unicode(self.classroom_id)

class NotificationLog(models.Model):
	date = models.DateTimeField(_('Date'),auto_now=True)
	user = models.ForeignKey(User, blank=True,verbose_name=_('User'))
	user_generated = models.BooleanField(_('User Generated'),default=True)
	text = models.TextField(_('Text'))
	font_awesome_icon = models.TextField('Font Awesome Icon',max_length=16,default="fa-bolt") #a font-awesome icon name

	def __unicode__(self):
		return unicode(self.date) + ' - '+ unicode(self.user) + ' ' + unicode(self.text)

	class Meta:
		get_latest_by = 'date'

class AttendanceLog(models.Model):
	classroom = models.ForeignKey(Classroom,verbose_name=_('Classroom ID'))
	date = models.DateField(_("Date"))
	absent = models.IntegerField(_("Absent"),default=0)
	present = models.IntegerField(_("Present"),default=0)

	def __unicode__(self):
		return unicode(self.classroom) + ': '+ unicode(self.date)
	class Meta:
			unique_together = (('classroom','date'))

class PublicSchoolHistory(models.Model):
	student_id = models.ForeignKey(IntakeSurvey,verbose_name=_('Student ID'))
	status = models.CharField(_('Enrolled in public school'),choices=YESNO,max_length=16)
	enroll_date = models.DateField(_('From Date'))
	drop_date = models.DateField(_('To Date'),null=True,blank=True)
	grade = models.IntegerField(_('Grade'),choices=PUBLIC_SCHOOL_GRADES,null=True,blank=True)
	school_name = models.CharField(_('School Name'),max_length=128,blank=True)
	reasons = models.TextField(_('Reasons for not attending'),blank=True)
	def __unicode__(self):
		return unicode(self.student_id) + ' - '+ unicode(self.grade)
	class Meta:
			unique_together = (('student_id','grade','enroll_date'))
