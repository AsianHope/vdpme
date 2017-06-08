from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User, Group, Permission
from django.core.urlresolvers import reverse
from mande.models import *
from mande.permissions import generate_group_perms
from mande.permissions import perms_required

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
    'student_evaluation_report':{'classroom_id':1},
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
    'academic_form':{'school_id':1,'test_date':'2015-01-01','classroom_id':1}
}

class PermissionsTestCase(TestCase):
    fixtures = ['schools.json','intakesurveys.json','exitsurveys.json',
                'classrooms.json','classroomenrollment.json','academic.json',
                'teachers.json']
    #generate users and groups
    def setUp(self):
        self.client = Client()
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
        self.client.login(username='teacher',password='test')
        site_coordinators_can_access = [
            'daily_absence_report',
            'class_list',
            'student_lag_report',
            'student_evaluation_report',
            'student_promoted_report',
            'students_promoted_times_report',
            'take_attendance',
            'attendance',
            'take_class_attendance',
            'attendance_calendar',
            'daily_attendance_report',
            'student_list',
            'student_detail',
            'intake_update',
            'classroomenrollment_form',
            'discipline_form',
            'academic_select',
            'studentevaluation_select'
        ]

        for url,args in permissions_test_data.iteritems():
            resp = self.client.get(reverse(url,kwargs=args))
            if url not in site_coordinators_can_access:
                if resp.status_code != 403:
                    print 'sc accessing '+url+str(resp.status_code)+'[expected: 403 ]'
                self.assertEqual(resp.status_code,403)
            else:
                if resp.status_code !=200:
                    print 'sc accessing '+url+str(resp.status_code)+'[expected: 200 ]'
                self.assertEqual(resp.status_code,200)

    def test_teacher_permissions(self):
        self.client.login(username='teacher',password='test')
        teachers_can_access = [
            'daily_absence_report',
            'class_list',
            'student_lag_report',
            'student_evaluation_report',
            'student_promoted_report',
            'students_promoted_times_report',
            'take_attendance',
            'take_class_attendance',
            'attendance_calendar',
            'daily_attendance_report',
            'attendance',
            'student_list',
            'student_detail',
            'intake_update',
            'classroomenrollment_form',
            'discipline_form',
            'academic_select',
            'studentevaluation_select'
        ]

        for url,args in permissions_test_data.iteritems():
            resp = self.client.get(reverse(url,kwargs=args))
            if url not in teachers_can_access:
                if resp.status_code != 403:
                    print 't accessing '+url+str(resp.status_code)+'[expected: 403 ]'
                self.assertEqual(resp.status_code,403)
            else:
                if resp.status_code !=200:
                    print 't accessing '+url+str(resp.status_code)+'[expected: 200 ]'

                self.assertEqual(resp.status_code,200)

    def test_community_worker_permissions(self):
        self.client.login(username='community_worker',password='test')
        community_worker_can_access = [
            'daily_attendance_report',
            'class_list',
            'exit_surveys_list',
            'student_medical_report',
            'student_dental_report',
            'students_intergrated_in_public_school',
            'attendance',
            'take_attendance',
            'take_class_attendance',
            'daily_attendance_report',
            'intake_survey',
            'exit_survey',
            'post_exit_survey',
            'spiritualactivities_survey',
            'health_form',
            'student_list',
            'classroomenrollment_form',
            'discipline_form',
            'student_detail',
            'student_dental_summary_report'
        ]

        for url,args in permissions_test_data.iteritems():
            resp = self.client.get(reverse(url,kwargs=args))
            if url not in community_worker_can_access:
                if resp.status_code != 403:
                    print 'cw accessing '+url+str(resp.status_code)+'[expected: 403 ]'
                self.assertEqual(resp.status_code,403)
            else:
                if resp.status_code !=200:
                    print 'cw accessing '+url+str(resp.status_code)+'[expected: 200 ]'
                self.assertEqual(resp.status_code,200)
    #just a sanity check
    def test_health_worker_permissions(self):
        self.client.login(username='health_worker',password='test')
        community_worker_can_access = [
            'health_form'
        ]

        for url,args in permissions_test_data.iteritems():
            resp = self.client.get(reverse(url,kwargs=args))
            if url not in community_worker_can_access:
                self.assertEqual(resp.status_code,403)
            else:
                self.assertEqual(resp.status_code,200)
