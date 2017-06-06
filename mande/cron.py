#!/usr/bin/env python
from mande.models import CurrentStudentInfo
from mande.utils import getEnrolledStudents
from mande.utils import ExitSurvey
from mande.utils import IntakeSurvey
from mande.utils import studentAtAgeAppropriateGradeLevel
from datetime import date,datetime

def my_scheduled_job():
  print datetime.now()
  try:
      cur_student = CurrentStudentInfo.objects.all()
      cur_student.delete()
      exit_surveys = ExitSurvey.objects.all().filter(
                      exit_date__lte=date.today().isoformat()
                      ).values_list('student_id',flat=True)
      active_surveys = IntakeSurvey.objects.filter(date__lte=date.today().isoformat()).order_by('student_id'
                               ).exclude(student_id__in=exit_surveys)
      for survey in active_surveys:
           recent_survey = survey.getRecentFields()
           student = CurrentStudentInfo(
               student_id=recent_survey['student_id'],
               name = recent_survey['name'],
               site = recent_survey['site'],
               date = recent_survey['date'],
               dob = recent_survey['dob'],
               gender = recent_survey['gender'],
               age_appropriate_grade = survey.age_appropriate_grade(),
               in_public_school = True if survey.get_pschool().status=='Y' else False,
               at_grade_level = studentAtAgeAppropriateGradeLevel(recent_survey['student_id']),
               vdp_grade = survey.current_vdp_grade()
           )
           student.save()
      print 'Success: Deleted: '+str(cur_student.count()) + '. Added: ' + str(CurrentStudentInfo.objects.all().count())
  except Exception as e:
     print 'Error:' + str(e)



