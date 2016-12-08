from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page

from mande import views
#to add a new item to the side menu, map the URL in urlpatterns, assign permissions
# in perms_required (permissions.py) and add its name and display name to the activity map below
urlpatterns = patterns('',
    # ex: /mande/
    url(r'^$', cache_page(300)(views.dashboard), name='index'),
    # ex: /mande/students/
    url(r'^students/$', cache_page(120)(views.student_list), name='student_list'),
    # ex: /mande/students/4
    url(r'^students/(?P<student_id>\d+)/$', views.student_detail, name='student_detail'),

    url(r'^attendance/$', views.attendance, name='attendance'),
    url(r'^attendance/calendar$', views.attendance_calendar, name='attendance_calendar'),
    url(r'^attendance/calendar/(?P<classroom_id>\d+)/(?P<attendance_date>\d{4}-\d{1,2}-\d{1,2})/$', views.attendance_days, name='attendance_days'),

    url(r'^attendance/take/$', views.daily_attendance_report, name='take_attendance'),
    url(r'^attendance/take/(?P<classroom_id>\d+)/(?P<attendance_date>\d{4}-\d{1,2}-\d{1,2})/$', views.take_class_attendance, name='take_class_attendance'),

    url(r'^attendance/report/$', views.daily_attendance_report, name='daily_attendance_report'),
    url(r'^attendance/report/(?P<attendance_date>\d{4}-\d{1,2}-\d{1,2})/$', views.daily_attendance_report, name='daily_attendance_report'),

    url(r'^attendance/report/absences/$', views.daily_absence_report, name='daily_absence_report'),
    url(r'^attendance/report/absences/(?P<attendance_date>\d{4}-\d{1,2}-\d{1,2})/$', views.daily_absence_report, name='daily_absence_report'),

    url(r'^attendance/report/student_absences/$', views.student_absence_report, name='student_absence_report'),

    url(r'^attendance/report/attendance_summary/$', views.attendance_summary_report, name='attendance_summary_report'),
    url(r'^attendance/report/attendance_summary/(?P<id>\d+)/(?P<select_type>[\w-]+)/$', views.attendance_summary_report, name='attendance_summary_report'),

    url(r'^attendance/report/unapproved_absence_with_no_comment/$', views.unapproved_absence_with_no_comment, name='unapproved_absence_with_no_comment'),
    url(r'^attendance/report/unapproved_absence_with_no_comment/(?P<school_year>\d+)/$', views.unapproved_absence_with_no_comment, name='unapproved_absence_with_no_comment'),

    url(r'^reports/data_audit/$', cache_page(60)(views.data_audit), name='data_audit'),
    url(r'^reports/class_list/$', cache_page(60)(views.class_list), name='class_list'),
    url(r'^reports/exit_surveys_list/$', views.exit_surveys_list, name='exit_surveys_list'),
    url(r'^reports/lag/$', cache_page(60)(views.student_lag_report), name='student_lag_report'),
    url(r'^reports/student_evaluation/$', views.student_evaluation_report, name='student_evaluation_report'),
    url(r'^reports/student_evaluation/(?P<classroom_id>\d+)/$', views.student_evaluation_report, name='student_evaluation_report'),
    url(r'^reports/student_achievement_test/$', views.student_achievement_test_report, name='student_achievement_test_report'),
    url(r'^reports/student_achievement/(?P<classroom_id>\d+)/$', views.student_achievement_test_report, name='student_achievement_test_report'),
    url(r'^reports/student_medical/$', views.student_medical_report, name='student_medical_report'),
    url(r'^reports/student_dental/$', views.student_dental_report, name='student_dental_report'),
    url(r'^reports/student_dental_summary/$', views.student_dental_summary_report, name='student_dental_summary_report'),
    url(r'^reports/student_dental_summary/(?P<site_id>\d+)/$', views.student_dental_summary_report, name='student_dental_summary_report'),
    url(r'^reports/student_attendance_detail/(?P<student_id>\d+)/$', views.student_attendance_detail, name='student_attendance_detail'),
    url(r'^reports/student_attendance_detail/$', views.student_attendance_detail, name='student_attendance_detail'),

    url(r'^reports/mande_summary_report/(?P<start_view_date>\d{4}-\d{1,2}-\d{1,2})/(?P<view_date>\d{4}-\d{1,2}-\d{1,2})$',cache_page(1800)(views.mande_summary_report), name='mande_summary_report'),
    url(r'^reports/mande_summary_report/$',cache_page(1800)(views.mande_summary_report), name='mande_summary_report'),

    url(r'^reports/student_promoted_report/$', views.student_promoted_report, name='student_promoted_report'),
    url(r'^reports/students_promoted_times_report/$', views.students_promoted_times_report, name='students_promoted_times_report'),
    url(r'^reports/students_promoted_times_report/(?P<filter_seach>[\w-]+)/$', views.students_promoted_times_report, name='students_promoted_times_report'),


    url(r'^reports/public_school_report/$', views.public_school_report, name='public_school_report'),
    url(r'^reports/students_intergrated_in_public_school/$', views.students_intergrated_in_public_school, name='students_intergrated_in_public_school'),

    url(r'^reports/students_lag_summary/$', views.students_lag_summary, name='students_lag_summary'),
    url(r'^reports/anomalous_data/$', views.anomalous_data, name='anomalous_data'),
    url(r'^reports/advanced_report/$', views.advanced_report, name='advanced_report'),



    url(r'^surveys/intake/$', views.intake_survey, name='intake_survey'),
    url(r'^surveys/intake/(?P<student_id>\d+)/$', views.intake_survey, name='intake_survey'),
    url(r'^surveys/intake/update/(?P<student_id>\d+)/$', views.intake_update, name='intake_update'),
    url(r'^surveys/intake/update/$', views.intake_update, name='intake_update'),
    url(r'^surveys/intake/internal/$', views.intake_internal, name='intake_internal'),
    url(r'^surveys/intake/internal/(?P<student_id>\d+)/$', views.intake_internal, name='intake_internal'),


    url(r'^surveys/exit/(?P<student_id>\d+)/$', views.exit_survey, name='exit_survey'),
    url(r'^surveys/exit/$', views.exit_survey, name='exit_survey'),

    url(r'^surveys/post_exit/(?P<student_id>\d+)/$', views.post_exit_survey, name='post_exit_survey'),
    url(r'^surveys/post_exit/$', views.post_exit_survey_list, name='post_exit_survey'),

    url(r'^surveys/spiritualactivities/(?P<student_id>\d+)/$', views.spiritualactivities_survey, name='spiritualactivities_survey'),
    url(r'^surveys/spiritualactivities/$', views.spiritualactivities_survey, name='spiritualactivities_survey'),

    url(r'^surveys/health/(?P<student_id>\d+)/(?P<appointment_date>\d{4}-\d{1,2}-\d{1,2})/(?P<appointment_type>\w+)/$', views.health_form, name='health_form'),
    url(r'^surveys/health/(?P<student_id>\d+)/$', views.health_form, name='health_form'),
    url(r'^surveys/health/$', views.health_form, name='health_form'),

    url(r'^school-management/discipline/(?P<student_id>\d+)/$', views.discipline_form, name='discipline_form'),
    url(r'^school-management/discipline/$', views.discipline_form, name='discipline_form'),

    url(r'^school-management/teachers/$', views.teacher_form, name='teacher_form'),
    url(r'^school-management/teachers/(?P<teacher_id>\d+)/$', views.teacher_form, name='teacher_form'),

    url(r'^school-management/classrooms/$', views.classroom_form, name='classroom_form'),
    url(r'^school-management/classrooms/(?P<classroom_id>\d+)/$', views.classroom_form, name='classroom_form'),

    url(r'^school-management/classrooms/assignment/$', views.classroomteacher_form, name='classroomteacher_form'),
    url(r'^school-management/classrooms/assignment/(?P<teacher_id>\d+)/$', views.classroomteacher_form, name='classroomteacher_form'),

    url(r'^school-management/enrollment/(?P<classroom_id>\d+)/$', views.classroomenrollment_form, name='classroomenrollment_form'),
    url(r'^school-management/enrollment/(?P<classroom_id>\d+)/(?P<student_id>\d+)/$', views.classroomenrollment_individual, name='classroomenrollment_individual'),
    url(r'^school-management/enrollment/$', views.classroomenrollment_form, name='classroomenrollment_form'),


    url(r'^school-management/academics/$', views.academic_select, name='academic_select'),
    url(r'^school-management/academics/(?P<student_id>\d+)/$', views.academic_form_single, name='academic_form_single'),
    url(r'^school-management/academics/(?P<student_id>\d+)/(?P<test_id>\d+)/$', views.academic_form_single, name='academic_form_single'),
    # url(r'^school-management/academics/(?P<student_id>\d+)/(?P<test_date>\d{4}-\d{1,2}-\d{1,2})/(?P<test_level>-?\d+)/$', views.academic_form_single, name='academic_form_single'),
    url(r'^school-management/academics/bulk/(?P<school_id>\d+)/(?P<test_date>\d{4}-\d{1,2}-\d{1,2})/$', views.academic_form, name='academic_form'),
    url(r'^school-management/academics/bulk/(?P<school_id>\d+)/(?P<test_date>\d{4}-\d{1,2}-\d{1,2})/(?P<classroom_id>\d+)/$', views.academic_form, name='academic_form'),

    url(r'^school-management/student-evaluation/$', views.studentevaluation_select, name='studentevaluation_select'),
    url(r'^school-management/student-evaluation/(?P<student_id>\d+)/$', views.studentevaluation_form_single, name='studentevaluation_form_single'),
    url(r'^school-management/student-evaluation/bulk/(?P<school_id>\d+)/(?P<get_date>\d{4}-\d{1,2}-\d{1,2})/$', views.studentevaluation_form, name='studentevaluation_form'),
    url(r'^school-management/student-evaluation/bulk/(?P<school_id>\d+)/(?P<get_date>\d{4}-\d{1,2}-\d{1,2})/(?P<classroom_id>\d+)/$', views.studentevaluation_form, name='studentevaluation_form'),

    url(r'^school-management/student_publicschool/(?P<student_id>\d+)/$', views.publicschool_form, name='publicschool_form'),
    url(r'^school-management/student_publicschool/(?P<student_id>\d+)/(?P<id>\d+)$', views.publicschool_form, name='publicschool_form'),


    url(r'^success/$', views.survey_success, name='success'),
    url(r'^log/$', views.notification_log, name='notification_log')




)

#map out where activities should show up in the menus
activity_map = [
    {
        'display':'Reports',
        'icon':'fa-bar-chart-o',
        'items':[
            {'name':'daily_attendance_report','display':'Classroom Attendance'},
            {'name':'daily_absence_report','display':'Daily Attendance'},

            {'name':'unapproved_absence_with_no_comment','display':'Unapproved Absence With NO Comment'},

            {'name':'attendance_summary_report','display':'Attendance Summary'},
            {'name':'data_audit','display':'Data Audit'},
            {'name':'class_list','display':'Class List'},
            {'name':'exit_surveys_list','display':'Exit Surveys List'},
            {'name':'student_lag_report','display':'Student Lag Report'},
            {'name':'student_evaluation_report','display':'Student Evaluation Report'},
            {'name':'student_achievement_test_report','display':'Student Achievement Test'},
            {'name':'student_medical_report','display':'Student Medical Report'},
            {'name':'student_dental_report','display':'Student Dental Report'},
            {'name':'student_dental_summary_report','display':'Student Dental Summary Report'},
            {'name':'student_promoted_report','display':'Student Promoted Report'},
            {'name':'students_promoted_times_report','display':'Students Promoted Times Report'},
            {'name':'public_school_report','display':'Public School Report'},
            {'name':'students_intergrated_in_public_school','display':'Students Intergrated In Public School Report'},
            {'name':'mande_summary_report','display':'M&E Summary Report'},
            {'name':'students_lag_summary','display':'Students Lag Summary Report'},
            {'name':'anomalous_data','display':'Anomalous Data'},
            {'name':'advanced_report','display':'Advanced Report'}

        ],
    },
    {
        'display':'Attendance',
        'icon':'fa-table',
        'items':[
            {'name':'take_attendance','display':'Take Attendance'},
            {'name':'attendance_calendar','display':'Modify Attendance Calendars'}
        ]
    },
    {
        'display':'Surveys',
        'icon':'fa-edit',
        'items':[
            {'name':'intake_survey','display':'Intake Survey'},
            {'name':'exit_survey','display':'Exit Survey'},
            {'name':'post_exit_survey','display':'Post-Exit Survey'},
            {'name':'spiritualactivities_survey','display':'Spiritual Activities'},
            {'name':'health_form','display':'Health Form'}

        ]
    },
    {
        'display':'School Management',
        'icon':'fa-sitemap',
        'items':[
            {'name':'student_list','display':'Student Information'},
            {'name':'classroomenrollment_form','display':'Enrolment'},
            {'name':'discipline_form','display':'Discipline'},
            {'name':'teacher_form','display':'Manage Teachers'},
            {'name':'classroom_form','display':'Manage Classrooms'},
            {'name':'classroomteacher_form','display':'Manage Classroom Assignments'},
            {'name':'academic_select','display':'Input Achievement Tests'},
            {'name':'studentevaluation_select','display':'Input Student Evaluations '}
        ]
    }
]
