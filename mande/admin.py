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

from mande.models import AttendanceDaysOffered
from mande.models import Attendance

from mande.models import Discipline
from mande.models import Academic
from mande.models import Health

from mande.models import ClassroomEnrollment
from mande.models import ClassroomTeacher

class IntakeSurveyAdmin(admin.ModelAdmin):
    fieldsets = [
        ('',
        {'fields': ['date']}),
        ('Student Biographical Information',
        {'fields': ['name','dob','grade_appropriate','graduation','gender','address','enrolled','grade_current','grade_last','reasons']}),
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
    list_filter = ('date','student_id','name')
    search_fields = ['name']

admin.site.register(School)
admin.site.register(Classroom)
admin.site.register(Teacher)

admin.site.register(IntakeSurvey,IntakeSurveyAdmin)
admin.site.register(IntakeInternal)
admin.site.register(IntakeUpdate)
admin.site.register(ExitSurvey)
admin.site.register(PostExitSurvey)

admin.site.register(StudentEvaluation)
admin.site.register(SpiritualActivitiesSurvey)

admin.site.register(AttendanceDaysOffered)
admin.site.register(Attendance)

admin.site.register(Discipline)
admin.site.register(Academic)
admin.site.register(Health)

admin.site.register(ClassroomEnrollment)
admin.site.register(ClassroomTeacher)
