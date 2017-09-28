from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User, Group, Permission
from django.core.urlresolvers import reverse
from mande.models import *
from mande.permissions import generate_group_perms
from mande.permissions import perms_required
from django.utils.translation import activate, get_language
permissions_test_data = {
    'index':{},
    'student_list':{},
    'student_detail':{'student_id':1},
    'attendance':{},
    'attendance_calendar':{},
    'attendance_days':{'classroom_id':1,'attendance_date':'2015-01-01'},
    'take_attendance':{},
    'take_class_attendance':{'classroom_id':1,'attendance_date':'2015-01-01'},
    'daily_attendance_report':{},
    'daily_attendance_report':{'attendance_date':'2015-01-01'},
    'daily_absence_report':{},
    'daily_absence_report':{'attendance_date':'2015-01-01'},
    'student_absence_report':{},
    'data_audit':{},
    'class_list':{},
    'exit_surveys_list':{},
    'student_lag_report':{},
    'student_evaluation_report':{},
    'student_evaluation_report':{'grade_id':1},
    'student_medical_report':{},
    'student_dental_summary_report':{},
    'student_dental_summary_report':{'site_id':1},
    'mande_summary_report':{},
    'mande_summary_report':{},
    'student_promoted_report':{},
    'students_promoted_times_report':{},
    'students_promoted_times_report':{'filter_seach':'la'},
    # 'students_intergrated_in_public_school':{},
    'students_lag_summary':{},
    'anomalous_data':{},
    'intake_survey':{},
    'intake_survey':{'student_id':1},
    'intake_update':{},
    'intake_update':{'student_id':1},
    'intake_internal':{},
    'intake_internal':{'student_id':1},
    'exit_survey':{},
    'exit_survey':{'student_id':1},
    'post_exit_survey':{},
    'post_exit_survey':{'student_id':1},
    'spiritualactivities_survey':{},
    'spiritualactivities_survey':{'student_id':1},
    'health_form':{},
    'health_form':{'student_id':1},
    'health_form':{'student_id':1,'appointment_date':'2015-01-01','appointment_type':'DENTAL'},
    'discipline_form':{},
    'discipline_form':{'student_id':1},
    'teacher_form':{},
    'teacher_form':{'teacher_id':1,'status':'active'},
    'classroom_form':{},
    'classroom_form':{'classroom_id':1},
    'classroomteacher_form':{},
    'classroomteacher_form':{'teacher_id':1},
    'classroomenrollment_form':{'classroom_id':1},
    'classroomenrollment_individual':{'classroom_id':1,'student_id':1},
    'classroomenrollment_form':{},
    'academic_select':{},
    'academic_form_single':{'student_id':1},
    'academic_form_single':{'student_id':1,'test_id':1},
    'academic_form':{'school_id':1,'test_date':'2015-01-01'},
    'academic_form':{'school_id':1,'test_date':'2015-01-01','classroom_id':1},

    'studentevaluation_select':{},
    'studentevaluation_form_single':{'student_id':1},
    'notification_log':{},
    'studentevaluation_select':{},
    'student_achievement_test_report':{},
    'delete_spiritualactivities_survey':{'id':1},
    'public_school_report':{},
    'index':{},
    'studentevaluation_form':{'school_id':2,'get_date':'2017-06-08','classroom_id':1},
    'student_attendance_detail':{'student_id':1},
    'attendance_summary_report':{},
    'advanced_report':{},
    'unapproved_absence_with_no_comment':{},
    'publicschool_form':{'student_id':1},
    'delete_public_school':{'id':1},
    'save_photo':{},
    'academic_making_period':{},
    'generate':{},
}

class PermissionsTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json','exitsurveys.json',
                'classrooms.json','classroomenrollment.json','academic.json',
                'teachers.json','spiritualactivities.json']

    #generate users and groups
    def setUp(self):
        self.client = Client()
        activate('en')
        group_perms = generate_group_perms()
        for group,perms in group_perms.iteritems():
            newgroup = Group.objects.create(name=group)
            newuser = User.objects.create_user(username=group,password='test')
            for perm in perms:
                #remove the mande. before the permission
                objects = Permission.objects.filter(codename=perm[6:])
                try:
                    newgroup.permissions.add(Permission.objects.get(codename=perm[6:]))
                except:
                    print 'oh crap! Tried to add: '+perm[6:]
            newuser.groups.add(newgroup)

    def test_admin_permissions(self):
        self.client.login(username='admin',password='test')
        #admins can access everything!
        for url,args in permissions_test_data.iteritems():
            resp = self.client.get(reverse(url,kwargs=args))
            self.assertNotEqual(resp.status_code,403)

    def test_site_coordinator_permissions(self):
        self.client.login(username='site_coordinator',password='test')
        #admins can access everything!
        for url,args in permissions_test_data.iteritems():
            resp = self.client.get(reverse(url,kwargs=args))
            self.assertNotEqual(resp.status_code,403)
    def test_teacher_permissions(self):
        self.client.login(username='teacher',password='test')
        teachers_can_access = [
            'publicschool_form',
            'unapproved_absence_with_no_comment',
            'student_attendance_detail',
            'attendance_summary_report',
            'daily_absence_report',
            'class_list',
            'student_lag_report',
            'student_evaluation_report',
            'student_achievement_test_report',
            'student_promoted_report',
            'students_promoted_times_report',
            'take_attendance',
            'attendance_calendar',
            'student_list',
            'student_detail',
            'intake_update',
            'classroomenrollment_form',
            'discipline_form',
            'academic_select',
            'studentevaluation_select',
            'studentevaluation_form',
            'studentevaluation_form_single',
            'take_class_attendance',
            'attendance',
            'advanced_report',
            'delete_public_school',
            'save_photo',
            'daily_attendance_report'
        ]
        for url,args in permissions_test_data.iteritems():
            resp = self.client.get(reverse(url,kwargs=args))
            if url not in teachers_can_access:
                if resp.status_code != 403:
                    print 't accessing '+url+' '+str(resp.status_code)+' [expected: 403 ]'
                self.assertEqual(resp.status_code,403)
            else:
                if resp.status_code !=200:
                    print 't accessing '+url+' '+str(resp.status_code)+' [expected: 200 ]'
                self.assertIn(resp.status_code,[200,302])

    def test_community_worker_permissions(self):
        self.client.login(username='community_worker',password='test')
        community_worker_can_access = [
            'publicschool_form',
            'unapproved_absence_with_no_comment',
            'student_attendance_detail',
            'attendance_summary_report',
            'daily_attendance_report',
            'class_list',
            'exit_surveys_list',
            'student_medical_report',
            'student_dental_report',
            'student_dental_summary_report',
            'public_school_report',
            'students_intergrated_in_public_school',
            'take_attendance',
            'take_class_attendance',
            'attendance',
            'intake_survey',
            'exit_survey',
            'post_exit_survey',
            'spiritualactivities_survey',
            'delete_spiritualactivities_survey',
            'health_form',
            'student_list',
            'classroomenrollment_form',
            'discipline_form',
            'student_detail',
            'advanced_report',
            'delete_public_school',
            'save_photo',
        ]

        for url,args in permissions_test_data.iteritems():
            resp = self.client.get(reverse(url,kwargs=args))
            if url not in community_worker_can_access:
                if resp.status_code != 403:
                    print 'cw accessing '+url+' '+str(resp.status_code)+' [expected: 403 ]'
                self.assertEqual(resp.status_code,403)
            else:
                if resp.status_code !=200:
                    print 'cw accessing '+url+' '+str(resp.status_code)+' [expected: 200 ]'
                self.assertIn(resp.status_code,[200,302])
    #just a sanity check
    def test_health_worker_permissions(self):
        self.client.login(username='health_worker',password='test')
        health_worker_can_access = [
            'health_form'
        ]
        for url,args in permissions_test_data.iteritems():
            resp = self.client.get(reverse(url,kwargs=args))
            if url not in health_worker_can_access:
                if resp.status_code != 403:
                    print 'hw accessing '+url+' '+str(resp.status_code)+' [expected: 403 ]'
                self.assertEqual(resp.status_code,403)
            else:
                if resp.status_code !=200:
                    print 'hw accessing '+url+' '+str(resp.status_code)+' [expected: 200 ]'
                self.assertIn(resp.status_code,[200,302])
