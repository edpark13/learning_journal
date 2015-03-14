import pytest
from pyramid import testing
import sqlalchemy as sa
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from sqlalchemy.ext.declarative import declarative_base
# from journal import Entry
from cryptacular.bcrypt import BCRYPTPasswordManager

# TEST_DSN = 'dbname=test user=edward'

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

@pytest.fixture(scope='function')
def app():
    from journal import main
    from webtest import TestApp
    import os
    os.environ['DATABASE_URL'] = 'postgresql://edward:@/test'
    app = main()
    return TestApp(app)

@pytest.fixture(scope='function')
def auth_req(request):
    manager = BCRYPTPasswordManager()
    settings = {
        'auth.username': 'admin',
        'auth.password': manager.encode('secret'),
    }
    testing.setUp(settings=settings)
    req = testing.DummyRequest()

    def cleanup():
        testing.tearDown()

    request.addfinalizer(cleanup)

    return req

def test_post_to_add_view(app):
    entry_data = {
        'title': 'Hello there',
        'text': 'This is a post',
    }
    response = app.post('/add', params=entry_data, status='3*')
    redirected = response.follow()
    actual = redirected.body
    for expected in entry_data.values():
        assert expected in actual

