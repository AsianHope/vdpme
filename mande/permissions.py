#set minimum permissions for access of each view (maybe more required for write access!)
perms_required={
    'student_list':{
        'mande.view_intakesurvey',
        'mande.view_intakeinternal',
        'mande.view_exitsurvey'
    },
    'student_detail':{
        'mande.view_intakesurvey',
        'mande.view_exitsurvey',
        'mande.view_postexitsurvey',
        'mande.view_academic',
        'mande.view_studentevaluation',
        'mande.view_discipline',
        'mande.view_health',
        'mande.view_classroomenrollment',
        'mande.view_attendance'
    },
    'attendance':{
        'mande.add_attendance',
        'mande.view_classroom',
        'mande.view_classroomenrollment',
        'mande.view_attendance',
        'mande.view_attendancedayoffering',
        'mande.view_attendancelog'
    },
    'attendance_calendar':{
        'mande.view_classroom',
        'mande.add_attendancedayoffering',
        'mande.change_attendancedayoffering'
    },
    'attendance_days':{
        'mande.view_classroom',
        'mande.add_attendancedayoffering',
        'mande.change_attendancedayoffering',
        'mande.delete_attendancedayoffering'
    },
    'take_attendance':{
        'mande.add_attendance',
        'mande.view_classroom',
        'mande.view_classroomenrollment',
        'mande.view_attendance',
        'mande.view_attendancedayoffering',
        'mande.view_attendancelog'
    },
    'take_class_attendance':{
        'mande.add_attendance',
        'mande.view_classroom',
        'mande.view_classroomenrollment',
        'mande.view_attendance',
        'mande.view_attendancedayoffering',
        'mande.view_attendancelog'
    },
    'daily_attendance_report':{
        'mande.view_classroom',
        'mande.view_attendancedayoffering',
        'mande.view_attendance'
    },
    'daily_absence_report':{
        'mande.view_classroom',
        'mande.view_attendancedayoffering',
        'mande.view_attendance'
    },
    'student_attendance_detail':{
        'mande.view_attendance'
    },

    'student_absence_report':{
        'mande.view_attendance'
    },
    'data_audit':{
        'mande.view_exitsurvey',
        'mande.view_intakesurvey',
        'mande.view_intakeinternal',
        'mande.view_intakeupdate',
        'mande.view_academic',
        'mande.view_intakeupdate',
        'mande.view_attendance',
        'mande.view_classroomenrollment'
    },
    'class_list':{
        'mande.view_classroom',
        'mande.view_classroomteacher'
    },
    'exit_surveys_list':{
        'mande.view_exitsurvey',
        'mande.view_postexitsurvey'
    },
    'student_lag_report':{
        'mande.view_exitsurvey',
        'mande.view_intakesurvey',
        'mande.view_intakeinternal',
        'mande.view_intakeupdate'
    },
    'student_evaluation_report':{
        'mande.view_studentevaluation',
        'mande.view_classroom'
    },
    'student_medical_report':{
        'mande.view_exitsurvey',
        'mande.view_intakesurvey',
        'mande.view_intakeinternal',
        'mande.view_intakeupdate',
        'mande.view_health'
    },
    'student_dental_report':{
        'mande.view_exitsurvey',
        'mande.view_intakesurvey',
        'mande.view_intakeinternal',
        'mande.view_intakeupdate',
        'mande.view_health'
    },
    'student_dental_summary_report':{
        'mande.view_exitsurvey',
        'mande.view_intakesurvey',
        'mande.view_intakeinternal',
        'mande.view_intakeupdate',
        'mande.view_health'
    },
    'mande_summary_report':{
        'mande.view_school',
        'mande.view_exitsurvey',
        'mande.view_intakesurvey',
        'mande.view_intakeupdate',
        'mande.view_classroomenrollment',
        'mande.view_classroom'
    },
    'student_promoted_report':{
        'mande.view_academic',
        'mande.view_intakesurvey',
        'mande.view_school'
    },
    'students_promoted_times_report':{
        'mande.view_school',
        'mande.view_intakesurvey',
        'mande.view_exitsurvey',
        'mande.view_academic'
    },
    'students_not_enrolled_in_public_school_report':{
        'mande.view_intakesurvey',
        'mande.view_exitsurvey'
    },
    'students_intergrated_in_public_school':{
        'mande.view_intakesurvey',
        'mande.view_intakeupdate'
    },
    'students_lag_summary':{
        'mande.view_intakesurvey',
        'mande.view_intakeinternal',
        'mande.view_exitsurvey',
        'mande.view_school'
    },
    'anomolous_data':{},
    'intake_survey':{
        'mande.add_intakesurvey',
        'mande.add_intakeinternal'
    },
    'intake_update':{
        'mande.add_intakeupdate'
    },
    'intake_internal':{
        'mande.add_intakeinternal'
    },
    'exit_survey':{
        'mande.add_exitsurvey'
    },
    'post_exit_survey':{
        'mande.add_postexitsurvey'
    },
    'post_exit_survey_list':{
        'mande.view_postexitsurvey'
    },
    'spiritualactivities_survey':{
        'mande.add_spiritualactivitiessurvey'
    },
    'health_form':{
        'mande.add_health'
    },
    'discipline_form':{
        'mande.add_discipline'
    },
    'teacher_form':{
        'mande.add_teacher',
        'mande.change_teacher'
    },
    'classroom_form':{
        'mande.add_classroom',
        'mande.change_classroom'
    },
    'classroomteacher_form':{
        'mande.add_classroomteacher',
        'mande.change_classroomteacher'
    },
    'classroomenrollment_form':{
        'mande.view_classroom',
        'mande.view_school',
        'mande.add_classroomenrollment',
        'mande.change_classroomenrollment'
    },
    'classroomenrollment_individual':{
        'mande.view_classroom',
        'mande.view_school',
        'mande.add_classroomenrollment',
        'mande.change_classroomenrollment'
    },
    'academic_select':{
        'mande.add_academic'
    },
    'academic_form':{
        'mande.add_academic'
    },
    'academic_form_single':{
        'mande.add_academic'
    },
    'studentevaluation_select':{
        'mande.add_studentevaluation'
    },
    'studentevaluation_form':{
        'mande.add_studentevaluation'
    },
    'studentevaluation_form_single':{
        'mande.add_studentevaluation'
    },
    'dashboard':{
        'mande.view_intakesurvey'
    },
    'notification_log':{
        'mande.view_notificationlog'
    }
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

    return group_perms

#helper function for above that makes sure the items in the list are unique
def __addperms(perms,addto):
    permissions = set(perms)
    target = set(addto)
    return list(target.union(permissions))
