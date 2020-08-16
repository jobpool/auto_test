from test_base import TestBase
import pytest

class Testmail163Class(TestBase):

    def case_mail163_login(self):
        self.init('cases/mail163/case_mail163_login.json',headless=False,nap=5,closewindows=True,wait=0)
        self.run()

    def case_mail163_sendmail(self):
        self.init('cases/mail163/case_mail163_sendmail.json',headless=False,nap=5,closewindows=True,wait=0)
        self.run()

test_example = Testmail163Class()

def test_case_mail163_login():
    test_example.case_mail163_login()

def test_case_mail163_sendmail():
    test_example.case_mail163_sendmail()

