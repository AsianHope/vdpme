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


admin.site.register(School)
admin.site.register(Classroom)
admin.site.register(Teacher)

admin.site.register(IntakeSurvey)
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
