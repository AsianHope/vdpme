from django.contrib import admin

# Register your models here.
from mande.models import School
from mande.models import Classroom
from mande.models import Teacher

from mande.models import IntakeSurvey
from mande.models import IntakeInternal
from mande.models import IntakeUpdate
from mande.models import ExitSurvey
from mande.models import PostExitSurvey



from mande.models import StudentEvaluation
from mande.models import SpiritualActivitiesSurvey

from mande.models import AttendanceDayOffering
from mande.models import Attendance

from mande.models import Discipline
from mande.models import Academic
from mande.models import Health

from mande.models import ClassroomEnrollment
from mande.models import ClassroomTeacher

class SchoolAdmin(admin.ModelAdmin):
        list_display = ('school_name','school_location')

class ClassroomAdmin(admin.ModelAdmin):
        list_display = ('school_id','classroom_id', 'cohort','classroom_number','classroom_location')
        list_filter = ('school_id','cohort')

class TeacherAdmin(admin.ModelAdmin):
        list_display = ('teacher_id','name')

class IntakeSurveyAdmin(admin.ModelAdmin):
    fieldsets = [
        ('',
        {'fields': ['date','site']}),
        ('Student Biographical Information',
        {'fields': ['name','dob','grade_appropriate','gender','address','enrolled','grade_current','grade_last','reasons']}),
        ('Information about the Father',
        {'fields': ['father_name','father_phone','father_profession','father_employment']}),
        ('Information about the Mother',
        {'fields': ['mother_name','mother_phone','mother_profession','mother_employment']}),
        ('Household Information',
        {'fields': ['minors','minors_in_school','minors_working','minors_profession','minors_encouraged','minors_training','minors_training_type']}),
        ('Notes',
        {'fields': ['notes']}),

    ]
    list_display = ('date','student_id','name','grade_appropriate')
    list_filter = ('date','grade_appropriate')
    search_fields = ['name','student_id']

class IntakeInternalAdmin(admin.ModelAdmin):
    list_display = ('student_id','enrollment_date','starting_grade')
    list_filter = ('starting_grade','enrollment_date')
    raw_id_fields = ('student_id',)
    search_fields = ['student_id__student_id']

class IntakeUpdateAdmin(admin.ModelAdmin):
    list_display = ('student_id','date')
    list_filter = ('date',)
    raw_id_fields = ('student_id',)
    search_fields = ['student_id__student_id']

class ExitSurveyAdmin(admin.ModelAdmin):
    list_display = ('student_id','exit_date','last_grade','early_exit_reason')
    list_filter = ('exit_date','last_grade','early_exit_reason')
    raw_id_fields = ('student_id',)

class PostExitSurveyAdmin(admin.ModelAdmin):
    list_display = ('student_id','exit_date','enrolled')
    list_filter = ('exit_date','enrolled')
    raw_id_fields = ('student_id',)
    search_fields = ['student_id__student_id']

class StudentEvaluationAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'date', 'academic_score', 'study_score', 'personal_score', 'hygiene_score', 'faith_score')
    list_filter = ('date',)
    raw_id_fields = ('student_id',)
    search_fields = ['student_id__student_id']

class SpiritualActivitiesSurveyAdmin(admin.ModelAdmin):
    list_display = ('student_id','date')
    list_filter = ('date',)
    raw_id_fields = ('student_id',)
    search_fields = ['student_id__student_id']

class AttendanceDayOfferingAdmin(admin.ModelAdmin):
    list_display = ('classroom_id', 'date', 'offered')
    list_filter = ('classroom_id', 'date', 'offered')

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('date','student_id','attendance')
    list_filter = ('date','attendance')
    raw_id_fields = ('student_id',)
    search_fields = ['student_id__student_id']

class DisciplineAdmin(admin.ModelAdmin):
    list_display = ('incident_date','student_id','classroom_id','incident_code')
    list_filter = ('incident_date','incident_code')
    raw_id_fields = ('student_id',)
    search_fields = ['student_id__student_id']

class AcademicAdmin(admin.ModelAdmin):
    list_display = ('test_date','student_id','test_level','promote')
    list_filter = ('test_level','promote')
    raw_id_fields = ('student_id',)
    search_fields = ['student_id__student_id']

class HealthAdmin(admin.ModelAdmin):
    list_display = ('appointment_date','appointment_type','student_id')
    list_filter = ('appointment_date','appointment_type')
    raw_id_fields = ('student_id',)
    search_fields = ['student_id__student_id']

class ClassroomEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('classroom_id','student_id','enrollment_date','drop_date')
    list_filter = ('classroom_id','enrollment_date','drop_date')
    raw_id_fields = ('student_id',)
    search_fields = ['student_id__student_id']

class ClassroomTeacherAdmin(admin.ModelAdmin):
    list_display = ('classroom_id','teacher_id')
    list_filter = ('classroom_id','teacher_id')

admin.site.register(School,SchoolAdmin)
admin.site.register(Classroom,ClassroomAdmin)
admin.site.register(Teacher,TeacherAdmin)

admin.site.register(IntakeSurvey,IntakeSurveyAdmin)
admin.site.register(IntakeInternal,IntakeInternalAdmin)
admin.site.register(IntakeUpdate,IntakeUpdateAdmin)
admin.site.register(ExitSurvey,ExitSurveyAdmin)
admin.site.register(PostExitSurvey,PostExitSurveyAdmin)

admin.site.register(StudentEvaluation,StudentEvaluationAdmin)
admin.site.register(SpiritualActivitiesSurvey,SpiritualActivitiesSurveyAdmin)

admin.site.register(AttendanceDayOffering,AttendanceDayOfferingAdmin)
admin.site.register(Attendance,AttendanceAdmin)

admin.site.register(Discipline,DisciplineAdmin)
admin.site.register(Academic,AcademicAdmin)
admin.site.register(Health,HealthAdmin)

admin.site.register(ClassroomEnrollment,ClassroomEnrollmentAdmin)
admin.site.register(ClassroomTeacher,ClassroomTeacherAdmin)
