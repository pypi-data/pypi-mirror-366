import re
import pytest
from webtest import TestApp as Client

from finitelycomputable.morepath_mount import application


def test_index():
    c = Client(application)
    response = c.get('/')
    assert 200 == response.status_code
    assert re.search('finitelycomputable.morepath_mount', response.text)

def test_env_info():
    c = Client(application)
    response = c.get('/env_info/')
    assert 200 == response.status_code
    assert re.search('finitelycomputable.morepath_mount', response.text)
