import re
import pytest
from webtest import TestApp as Client

from finitelycomputable.morepath_mount import application


def test_helloworld_morepath():
    c = Client(application)
    response = c.get('/hello_world/')
    assert 200 == response.status_code
    assert re.search('says "hello, world"\n', response.text)
    assert re.search('Morepath', response.text)

def test_helloworld_in_env_info():
    c = Client(application)
    response = c.get('/env_info/')
    assert 200 == response.status_code
    assert re.search('finitelycomputable.helloworld_morepath', response.text)
    assert re.search('finitelycomputable.morepath_mount', response.text)

def test_helloworld_in_index():
    c = Client(application)
    response = c.get('/')
    assert 200 == response.status_code
    assert re.search('finitelycomputable-helloworld-morepath', response.text)
    assert re.search('finitelycomputable.morepath_mount', response.text)
