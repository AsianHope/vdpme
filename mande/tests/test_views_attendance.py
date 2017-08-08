from django.test import TestCase
from django.test import Client

from mande.models import *
from mande.forms import *
from mande.views import AttendanceCalendar

from datetime import date,datetime

from django.db.models import Q
from django.core.urlresolvers import reverse
from django.utils.translation import activate
from django.utils.safestring import mark_safe


activate('en')
class AttendanceViewTestCase(TestCase):
    fixtures = ['users.json']
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_context(self):
        url = reverse('attendance')
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/attendance.html')
        content1 = '<a href = "'+reverse("attendance_calendar")+'">Modify Attendance Calendars</a>'
        content2 = '<a href = "'+reverse("take_attendance")+'">Take Attendance</a>'
        self.assertContains(resp,content1)
        self.assertContains(resp,content2)

class AttendanceCalendarViewTestCase(TestCase):
    fixtures = ['users.json','classrooms.json','schools.json']
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
    def test_context(self):
        url = reverse('attendance_calendar')
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/attendancecalendar.html')
        attendance_date = date.today().replace(day=1).isoformat()
        self.assertEqual(len(resp.context['classrooms']),4)
        self.assertEqual(resp.context['attendance_date'],attendance_date)

class TakeClassAttendanceViewTestCase(TestCase):
    fixtures = ['users.json','classrooms.json','schools.json',
                'classroomenrollment.json','intakesurveys.json',
                'attendances.json','attendancedayofferings.json',
                'attendancelogs.json','notificationlogs.json'
               ]
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
        # submit_enabled True
        AttendanceDayOffering.objects.create(
        classroom_id=Classroom.objects.get(pk=1),
        date=date.today().isoformat(),
        offered='Y'
        )

        # Attendance for one or more students has been taken
        Attendance.objects.create(
        classroom=Classroom.objects.get(pk=1),
        student_id= IntakeSurvey.objects.get(pk=1),
		notes="",
		attendance="UA",
		date='2017-01-01'
        )

    def test_context(self):
        classroom_id = 1
        today = date.today().isoformat()
        attendance_date = '2017-01-01'
        url = reverse('take_class_attendance',kwargs={'classroom_id':classroom_id,'attendance_date':attendance_date})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/takeclassattendanceformset.html')
        classroom = Classroom.objects.get(pk=1)
        students = ClassroomEnrollment.objects.filter(
                                                  Q(classroom_id=classroom_id)
                                                  & Q(student_id__date__lte=today)
                                                  & Q(Q(drop_date__gte=attendance_date) | Q(drop_date=None)))
        student_attendance = Attendance.objects.filter(student_id__in=students.values_list('student_id'),
                                                     date=attendance_date)
        self.assertEqual(resp.context['classroom'],classroom)
        self.assertEqual(list(resp.context['students']),list(students))
        self.assertEqual(resp.context['attendance_date'],attendance_date)
        self.assertIsInstance(resp.context['formset'],AttendanceFormSet)
        self.assertEqual(resp.context['warning'],'The selected date is not today!')
        self.assertEqual(resp.context['message'],'Attendance for one or more students has been taken')
        self.assertEqual(resp.context['submit_enabled'],False)
        self.assertEqual(resp.context['limit'],None)
        self.assertEqual(resp.context['next_url'],None)

    def test_post_invalid(self):
        # test field reqired
        classroom_id = 1
        attendance_date = '2017-01-01'
        url = reverse('take_class_attendance',kwargs={'classroom_id':classroom_id,'attendance_date':attendance_date})
        data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 10,
            'form-0-student_id':1,
        }
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/takeclassattendanceformset.html')
        self.assertFalse(resp.context['formset'].is_valid())
        self.assertEqual(resp.context['formset'].errors,[{'date': [u'This field is required.'], 'attendance': [u'This field is required.']}])
        # test attendance already exist
        data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 10,
            'form-0-student_id':1,
            'form-0-attendance':'P',
            'form-0-date':attendance_date,
            'form-0-classroom':classroom_id
        }
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/takeclassattendanceformset.html')
        self.assertFalse(resp.context['formset'].is_valid())
        self.assertEqual(resp.context['formset'].errors,[{'__all__': [u'Attendance with this Student ID and Attendance Day already exists.']}])

    def test_post_valid(self):
        classroom_id = 1
        attendance_date =  date.today().isoformat()
        url = reverse('take_class_attendance',kwargs={'classroom_id':classroom_id,'attendance_date':attendance_date})
        data = {
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 10,

            'form-0-student_id':1,
            'form-0-attendance':'P',
            'form-0-date':attendance_date,
            'form-0-classroom':classroom_id,

            'form-1-student_id':2,
            'form-1-attendance':'AA',
            'form-1-date':attendance_date,
            'form-1-classroom':classroom_id,
        }
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/takeclassattendanceformset.html')
        self.assertIsInstance(resp.context['formset'],AttendanceFormSet)
        self.assertTrue(resp.context['formset'].is_valid())
        self.assertEqual(resp.context['attendance_date'],attendance_date)
        self.assertEqual(len(resp.context['students']),1)
        self.assertTrue(Attendance.objects.filter(date=attendance_date,classroom_id=1).count(),2)

        attendancelog = AttendanceLog.objects.get(classroom=classroom_id,date=attendance_date)
        self.assertEqual(attendancelog.present,1)
        self.assertEqual(attendancelog.absent,1)

        message = ('Took attendance for '+unicode(Classroom.objects.get(pk=1))+' (A:'+unicode(attendancelog.absent)+',P:'+unicode(attendancelog.present)+')')
        self.assertEqual(resp.context['message'],message)
        self.assertTrue(
            NotificationLog.objects.filter(
                text=message, font_awesome_icon='fa-check-square',
                user=self.client.session['_auth_user_id']
            ).exists()
        )
        self.assertEqual(resp.context['submit_enabled'],True)
        self.assertEqual(resp.context['limit'],None)
        self.assertEqual(resp.context['next_url'],None)

class AttendanceCalendarClassTestCase(TestCase):
    fixtures = ['users.json','attendancedayofferings.json','classrooms.json','schools.json']
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')

    def test_classinitialiate(self):
        attendance_days = AttendanceDayOffering.objects.filter(classroom_id=1).filter(date__year='2016',date__month='03')
        calendar = AttendanceCalendar(attendance_days)

        self.assertEqual(calendar.firstweekday,6)
        self.assertEqual(calendar.attendance_offerings,calendar.breakout(attendance_days))

        calendartable = calendar.formatmonth(2016,03)
        self.assertIn('March 2016',calendartable)
        self.assertIn('<td class="tue filled">1 </td>',calendartable)
        self.assertIn('<td class="wed filled">2 </td>',calendartable)
        self.assertIn('<td class="thu filled">3 </td>',calendartable)
        self.assertIn('<td class="fri filled">4 </td>',calendartable)
        self.assertIn('<td class="sat filled">5 </td>',calendartable)
        self.assertIn('<td class="sun filled">6 </td>',calendartable)
        self.assertIn('<td class="mon filled">7 </td>',calendartable)
        self.assertIn('<td class="tue filled">8 </td>',calendartable)
        self.assertIn('<td class="wed filled">9 </td>',calendartable)
        self.assertIn('<td class="thu filled">10 </td>',calendartable)
        self.assertIn('<td class="fri filled">11 </td>',calendartable)
        self.assertIn('<td class="sat filled">12 </td>',calendartable)
        self.assertIn('<td class="sun filled">13 </td>',calendartable)
        self.assertIn('<td class="mon filled">14 </td>',calendartable)
        self.assertIn('<td class="tue filled">15 </td>',calendartable)
        self.assertIn('<td class="wed filled">16 </td>',calendartable)
        self.assertIn('<td class="thu filled">17 </td>',calendartable)
        self.assertIn('<td class="fri filled">18 </td>',calendartable)
        self.assertIn('<td class="sat filled">19 </td>',calendartable)
        self.assertIn('<td class="sun filled">20 </td>',calendartable)
        self.assertIn('<td class="mon filled">21 </td>',calendartable)
        self.assertIn('<td class="tue filled">22 </td>',calendartable)
        self.assertIn('<td class="wed filled">23 </td>',calendartable)
        self.assertIn('<td class="thu filled">24 </td>',calendartable)
        self.assertIn('<td class="fri filled">25 </td>',calendartable)
        self.assertIn('<td class="sat filled">26 </td>',calendartable)
        self.assertIn('<td class="sun filled">27 </td>',calendartable)
        self.assertIn('<td class="mon filled">28 </td>',calendartable)
        self.assertIn('<td class="tue filled">29 </td>',calendartable)
        self.assertIn('<td class="wed filled">30 </td>',calendartable)
        self.assertIn('<td class="thu filled">31 </td>',calendartable)

        self.assertEqual(calendar.formatday(0,1),'<td class="noday">&nbsp;</td>')
        self.assertEqual(calendar.formatday(1,1),'<td class="tue filled">1 </td>')

        days = []
        for attendance_offering in attendance_days:
            days.append(attendance_offering.date.day)
        self.assertEqual(
                    calendar.breakout(attendance_days),
                    days
                )

        self.assertEqual(calendar.day_cell('noday','&nbsp;'),'<td class="noday">&nbsp;</td>')
        self.assertEqual(calendar.day_cell('thu','1'),'<td class="thu">1</td>')

class AttendanceDaysViewTestCase(TestCase):
    fixtures = ['users.json','attendancedayofferings.json','classrooms.json','schools.json']
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin',password='test')
    def test_context_no_get(self):
        classroom_id = 1
        attendance_date = '2016-01-03'
        url = reverse('attendance_days',kwargs={'classroom_id':classroom_id,'attendance_date':attendance_date})
        resp = self.client.get(url,follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,'mande/attendancedays.html')
        self.assertEqual(resp.context['classroom'],Classroom.objects.get(pk=1))
        attendance_date =  datetime.strptime(attendance_date, '%Y-%m-%d')
        attendance_days = AttendanceDayOffering.objects.filter(
                                                          classroom_id=classroom_id
                                                      ).filter(
                                                          date__year=attendance_date.year,
                                                          date__month=attendance_date.month
                                                      )
        c = mark_safe(AttendanceCalendar(attendance_days).formatmonth(attendance_date.year,attendance_date.month))
        self.assertEqual(resp.context['Calendar'],c)

    def test_context_get_with_day(self):
         classroom_id = 1
         attendance_date = '2016-03-01'
         day = 1
         url = reverse('attendance_days',kwargs={'classroom_id':classroom_id,'attendance_date':attendance_date})
         resp = self.client.get(url,{'day':day},follow=True)
         self.assertEqual(resp.status_code, 200)
         self.assertTemplateUsed(resp,'mande/attendancedays.html')
         attendance_date =  datetime.strptime(attendance_date, '%Y-%m-%d')
         attendance_days = AttendanceDayOffering.objects.filter(
                                         classroom_id=classroom_id,
                                         date__year=attendance_date.year,
                                         date__month=attendance_date.month,
                                         date__day=day)
         self.assertRaises(KeyError, lambda:resp.context['classroom'])
         self.assertRaises(KeyError, lambda:resp.context['Calendar'])
         self.assertFalse(attendance_days.exists())

    def test_context_get_with_autoapply(self):
         classroom_id = 1
         attendance_date = '2016-03-01'
         day = 1
         url = reverse('attendance_days',kwargs={'classroom_id':classroom_id,'attendance_date':attendance_date})
         resp = self.client.get(url,{'day':day,'autoapply':True},follow=True)
         self.assertEqual(resp.status_code, 200)
         self.assertTemplateUsed(resp,'mande/attendancedays.html')
         classroom = Classroom.objects.get(pk=classroom_id)
         self.assertRaises(KeyError, lambda:resp.context['classroom'])
         self.assertRaises(KeyError, lambda:resp.context['Calendar'])
         classrooms = Classroom.objects.all(
                    ).filter(school_id=classroom.school_id
                    ).exclude(classroom_id=classroom.classroom_id)
         for c in classrooms:
             self.assertEqual(c.attendance_calendar,classroom)
         self.assertEqual(classroom.attendance_calendar,None)
