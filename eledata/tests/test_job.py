from django.test import TestCase
from django.test import Client
from eledata.models.job import Job
from eledata.models.event import Event
from eledata.models.users import User, Group


class JobTestCase(TestCase):
    def doCleanups(self):
        Group.drop_collection()
        User.drop_collection()
        Event.drop_collection()
        Job.drop_collection()

    def setUp(self):
        Group.drop_collection()
        User.drop_collection()
        Event.drop_collection()
        Job.drop_collection()

        assert len(Group.objects) == 0
        assert len(User.objects) == 0
        assert len(Event.objects) == 0
        assert len(Job.objects) == 0

        self.admin = User.create_admin(username="admin", password="pass", group_name="dummy_group")
        self.admin_group = Group.objects.get(name="dummy_group")
        self.admin_client = Client()
        self.admin_client.post("/users/login/", {"username": "admin", "password": "pass"})

    def test_job(self):
        job = Job(
            job_engine="job_engine",
            job_status="job_status",
            job_error_message="job_error_message",
            group=self.admin_group,  # see if any group created in the test file
            parameter=[],
        )
        job.save()

        # your get api here
        response = self.admin_client.get("/event/select_job_list/")

        # test your response
        print(response)
