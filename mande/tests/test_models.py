from django.test import TestCase
from mande.models import School

class SchoolTestCase(TestCase):
    def setUp(self):
        School.objects.create(school_name="Test School", school_location="Somewhere")
        School.objects.create(school_name="Test School 2", school_location="Somewhere Else")

    def test_schools_exist(self):
        schools = School.objects.all();

        self.assertEqual(len(schools),2)
