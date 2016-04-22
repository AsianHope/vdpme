#set minimum permissions for access of each view (maybe more required for write access!)
perms_required = {
	'classroom_form': {'mande.view_classroom_form'},
	'academic_select': {'mande.view_academic_select'},
	'student_lag_report': {'mande.view_student_lag_report'},
	'health_form': {'mande.view_health_form'},
	'studentevaluation_form_single': {'mande.view_studentevaluation_form_single'},
	'intake_internal': {'mande.view_intake_internal'},
	'discipline_form': {'mande.view_discipline_form'},
	'classroomenrollment_form': {'mande.view_classroomenrollment_form'},
	'take_class_attendance': {'mande.view_take_class_attendance'},
	'attendance': {'mande.view_attendance'},
	'student_dental_report': {'mande.view_student_dental_report'},
	'intake_update': {'mande.view_intake_update'},
	'notification_log': {'mande.view_notification_log'},
	'student_detail': {'mande.view_student_detail'},
	'intake_survey': {'mande.view_intake_survey'},
	'take_attendance': {'mande.view_daily_attendance_report'},#take_attendance is just a link the the daily_attendance report
	'classroomteacher_form': {'mande.view_classroomteacher_form'},
	'class_list': {'mande.view_class_list'},
	'students_promoted_times_report': {'mande.view_students_promoted_times_report'},
	'post_exit_survey_list': {'mande.view_post_exit_survey_list'},
	'daily_absence_report': {'mande.view_daily_absence_report'},
	'mande_summary_report': {'mande.view_mande_summary_report'},
	'exit_survey': {'mande.view_exit_survey'},
	'student_absence_report': {'mande.view_student_absence_report'},
	'student_evaluation_report': {'mande.view_student_evaluation_report'},
	'academic_form_single': {'mande.view_academic_form_single'},
	'attendance_days': {'mande.view_attendance_days'},
	'classroomenrollment_individual': {'mande.view_classroomenrollment_individual'},
	'anomolous_data': {'mande.view_anomolous_data'},
	'students_lag_summary': {'mande.view_students_lag_summary'},
	'data_audit': {'mande.view_data_audit'},
	'studentevaluation_select': {'mande.view_studentevaluation_select'},
	'exit_surveys_list': {'mande.view_exit_surveys_list'},
	'daily_attendance_report': {'mande.view_daily_attendance_report'},
	'spiritualactivities_survey': {'mande.view_spiritualactivities_survey'},
	'student_medical_report': {'mande.view_student_medical_report'},
	'attendance_calendar': {'mande.view_attendance_calendar'},
	'teacher_form': {'mande.view_teacher_form'},
	'student_promoted_report': {'mande.view_student_promoted_report'},
	'students_intergrated_in_public_school': {'mande.view_students_intergrated_in_public_school'},
	'students_not_enrolled_in_public_school_report': {'mande.view_students_not_enrolled_in_public_school_report'},
	'post_exit_survey': {'mande.view_post_exit_survey'},
	'academic_form': {'mande.view_academic_form'},
	'dashboard': {'mande.view_dashboard'},
	'student_list': {'mande.view_student_list'},
	'studentevaluation_form': {'mande.view_studentevaluation_form'},
	'student_dental_summary_report': {'mande.view_student_dental_summary_report'},
	'student_attendance_detail':{'mande.view_student_attendance_detail'},
	'attendance_summary_report':{'mande.view_attendance_summary_report'}
}
#this is a function to help test that the permissions above are
#correctly implemented in the views
def generate_group_perms():
    #set up roles
    group_perms = {
        'admin':[],
        'site_coordinator':[],
        'community_worker':[],
        'teacher':[],
        'health_worker':[]
    }
    #admins/site coordinators have all permissions
    for function,permissions in perms_required.iteritems():
        for permission in permissions:
            group_perms['admin'].append(permission)
            group_perms['site_coordinator'].append(permission)

    #hws is a made up role - just a sanity check with a single permission.
    group_perms['health_worker'] = __addperms(perms_required['health_form'],group_perms['health_worker'])

    #community workers can:
    #view attendance detail
    group_perms['community_worker'] = __addperms(perms_required['student_attendance_detail'],group_perms['community_worker'])
	#view attendance summary
    group_perms['community_worker'] = __addperms(perms_required['attendance_summary_report'],group_perms['community_worker'])
    #view classroom Attendance
    group_perms['community_worker'] = __addperms(perms_required['daily_attendance_report'],group_perms['community_worker'])
    #view class list
    group_perms['community_worker'] = __addperms(perms_required['class_list'],group_perms['community_worker'])
    #view exit surveys list
    group_perms['community_worker'] = __addperms(perms_required['exit_surveys_list'],group_perms['community_worker'])
    #view student medical report
    group_perms['community_worker'] = __addperms(perms_required['student_medical_report'],group_perms['community_worker'])
    #view student dental report
    group_perms['community_worker'] = __addperms(perms_required['student_dental_report'],group_perms['community_worker'])
    #view student dental summary report
    group_perms['community_worker'] = __addperms(perms_required['student_dental_summary_report'],group_perms['community_worker'])
    #view students not enrolled in public school
    group_perms['community_worker'] = __addperms(perms_required['students_not_enrolled_in_public_school_report'],group_perms['community_worker'])
    #view students integrated in publich school report
    group_perms['community_worker'] = __addperms(perms_required['students_intergrated_in_public_school'],group_perms['community_worker'])
    #take Attendance
    group_perms['community_worker'] = __addperms(perms_required['take_attendance'],group_perms['community_worker'])
    group_perms['community_worker'] = __addperms(perms_required['take_class_attendance'],group_perms['community_worker'])
    group_perms['community_worker'] = __addperms(perms_required['attendance'],group_perms['community_worker'])
    #add intake Surveys
    group_perms['community_worker'] = __addperms(perms_required['intake_survey'],group_perms['community_worker'])
    #add exit Surveys
    group_perms['community_worker'] = __addperms(perms_required['exit_survey'],group_perms['community_worker'])
    #add post-exit Surveys
    group_perms['community_worker'] = __addperms(perms_required['post_exit_survey'],group_perms['community_worker'])
    #add spiritual activities
    group_perms['community_worker'] = __addperms(perms_required['spiritualactivities_survey'],group_perms['community_worker'])
    #add/edit health
    group_perms['community_worker'] = __addperms(perms_required['health_form'],group_perms['community_worker'])
    #view student Information
    group_perms['community_worker'] = __addperms(perms_required['student_list'],group_perms['community_worker'])
    #view Enrollment
    group_perms['community_worker'] = __addperms(perms_required['classroomenrollment_form'],group_perms['community_worker'])
    #view discipline
    group_perms['community_worker'] = __addperms(perms_required['discipline_form'],group_perms['community_worker'])
    #add/change student details
    group_perms['community_worker'] = __addperms(perms_required['student_detail'],group_perms['community_worker'])

    #teachers can:
    #view attendance detail
    group_perms['teacher'] = __addperms(perms_required['student_attendance_detail'],group_perms['teacher'])
	#view attendance summary
    group_perms['teacher'] = __addperms(perms_required['attendance_summary_report'],group_perms['teacher'])
    #view dailiy absences
    group_perms['teacher'] = __addperms(perms_required['daily_absence_report'],group_perms['teacher'])
    #view class list
    group_perms['teacher'] = __addperms(perms_required['class_list'],group_perms['teacher'])
    #view student lag reports
    group_perms['teacher'] = __addperms(perms_required['student_lag_report'],group_perms['teacher'])
    #view student evaluation reports
    group_perms['teacher'] = __addperms(perms_required['student_evaluation_report'],group_perms['teacher'])
    #view students promoted reports
    group_perms['teacher'] = __addperms(perms_required['student_promoted_report'],group_perms['teacher'])
    #view students promoted times report
    group_perms['teacher'] = __addperms(perms_required['students_promoted_times_report'],group_perms['teacher'])
    #take attendance
    group_perms['teacher'] = __addperms(perms_required['take_attendance'],group_perms['teacher'])
    #view attendance calendars
    group_perms['teacher'] = __addperms(perms_required['attendance_calendar'],group_perms['teacher'])
    #view student Information
    group_perms['teacher'] = __addperms(perms_required['student_list'],group_perms['teacher'])
    #view student detail
    group_perms['teacher'] = __addperms(perms_required['student_detail'],group_perms['teacher'])
    #add intakeupdate
    group_perms['teacher'] = __addperms(perms_required['intake_update'],group_perms['teacher'])
    #view Enrollment
    group_perms['teacher'] = __addperms(perms_required['classroomenrollment_form'],group_perms['teacher'])
    #add discipline
    group_perms['teacher'] = __addperms(perms_required['discipline_form'],group_perms['teacher'])
    #add achievement tests
    group_perms['teacher'] = __addperms(perms_required['academic_select'],group_perms['teacher'])
    #add student evaluations
    group_perms['teacher'] = __addperms(perms_required['studentevaluation_select'],group_perms['teacher'])
    group_perms['teacher'] = __addperms(perms_required['studentevaluation_form'],group_perms['teacher'])
    group_perms['teacher'] = __addperms(perms_required['studentevaluation_form_single'],group_perms['teacher'])
    #take attendance
    group_perms['teacher'] = __addperms(perms_required['take_class_attendance'],group_perms['teacher'])
    group_perms['teacher'] = __addperms(perms_required['attendance'],group_perms['teacher'])

    return group_perms

#helper function for above that makes sure the items in the list are unique
def __addperms(perms,addto):
    permissions = set(perms)
    target = set(addto)
    return list(target.union(permissions))
