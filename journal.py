# -*- coding: utf-8 -*-
import psycopg2
import os
import logging
import datetime
import markdown
import jinja2
import json
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid.view import view_config
# from pyramid.events import NewRequest, subscriber
from waitress import serve
from contextlib import closing
from pyramid.httpexceptions import HTTPFound, HTTPInternalServerError, HTTPForbidden
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from cryptacular.bcrypt import BCRYPTPasswordManager
from pyramid.security import remember, forget
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from waitress import serve
from zope.sqlalchemy import ZopeTransactionExtension


here = os.path.dirname(os.path.abspath(__file__))

DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id serial PRIMARY KEY,
    title VARCHAR (127) NOT NULL,
    text TEXT NOT NULL,
    created TIMESTAMP NOT NULL
)
"""

INSERT_ENTRY = """
INSERT INTO entries (title, text, created) VALUES (%s, %s, %s)
"""

UPDATE_ENTRY = """
UPDATE entries SET (title, text) = (%s, %s) WHERE id=%s
"""

DB_ENTRIES_LIST = """
SELECT id, title, text, created FROM entries ORDER BY created DESC
"""

SELECT_SINGLE_ENTRY = """
SELECT * FROM entries WHERE id=%s;
"""
SELECT_SINGLE_NEWEST_ENTRY = """
SELECT * FROM entries ORDER BY created DESC LIMIT 1 
"""

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Entry(Base):
    __tablename__ = 'entries'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.Unicode(127), nullable=False)
    text = sa.Column(sa.UnicodeText, nullable=False)
    created = sa.Column(
        sa.DateTime, nullable=False, default=datetime.datetime.utcnow
    )

    def __repr__(self):
        return u"{}: {}".format(self.__class__.__name__, self.title)

    @classmethod
    def all(cls):
        return DBSession.query(cls).order_by(cls.created.desc()).all()

    @classmethod
    def by_id(cls, id):
        return DBSession.query(cls).filter(cls.id==id).one()

    @classmethod
    def from_request(cls, request):
        title = request.params.get('title', None)
        text = request.params.get('text', None)
        created = datetime.datetime.utcnow()
        new_entry = cls(title=title, text=text, created=created)
        DBSession.add(new_entry)

    @classmethod
    def get_newest(cls):
        return DBSession.query(cls).order_by(cls.created.desc()).first()

logging.basicConfig()
log = logging.getLogger(__file__)

def to_json(entry):
        return dict(id = entry.id,
                    title = entry.title,
                    text = entry.text,
                    created = entry.created)

def mdown(text):
    return markdown.markdown(text, extensions=['codehilite', 'fenced_code'])


# def connect_db(settings):
#     """Return a connection to the configured database"""
#     return psycopg2.connect(settings['db'])


# def init_db():
#     """Create database dables defined by DB_SCHEMA

#     Warning: This function will not update existing table definitions
#     """
#     settings = {}
#     settings['db'] = os.environ.get(
#         'DATABASE_URL', 'dbname=learning_journal user=edward'
#     )
#     with closing(connect_db(settings)) as db:
#         db.cursor().execute(DB_SCHEMA)
#         db.commit()


# @subscriber(NewRequest)
# def open_connection(event):
#     request = event.request
#     settings = request.registry.settings
#     request.db = connect_db(settings)
#     request.add_finished_callback(close_connection)


# def close_connection(request):
#     """close the database connection for this request

#     If there has been an error in the processing of the request, abort any
#     open transactions.
#     """
#     db = getattr(request, 'db', None)
#     if db is not None:
#         if request.exception is not None:
#             db.rollback()
#         else:
#             db.commit()
#         request.db.close()


def update_entry(request, id):
    """update an entry already in the database"""
    title = request.params.get('title', None)
    text = request.params.get('text', None)
    request.db.cursor().execute(UPDATE_ENTRY, [title, text, id])


# def write_entry(request):
#     """ add a new entry to the database"""
#     title = request.params.get('title', None)
#     text = request.params.get('text', None)
#     created = datetime.datetime.utcnow()
#     request.db.cursor().execute(INSERT_ENTRY, [title, text, created])


@view_config(route_name='add', renderer='json')
def add_entry(request):
    if request.authenticated_userid:
        if request.method == 'POST':
            try:
                Entry.from_request(request)
            # This error type needs to be updated since it will now be an SQLA error
            # type.
            except psycopg2.Error:
                # this will catch any errors generated by the database
                return HTTPInternalServerError
            return get_newest_entry(request)
    else:
        return HTTPForbidden()

# HOME PAGE
@view_config(route_name='home', renderer='templates/list.jinja2')
def read_entries(request):
    """return a list of all entries as dicts"""
    entries = Entry.all()
    for entry in entries:
        entry.text = mdown(entry.text)
    return {'entries': entries}


# EDIT ENTRY PAGE
@view_config(route_name='edit', renderer='json')
def edit(request):
    """view for edit single entry"""
    entry = ""
    id = request.params.get('id', None)
    if request.authenticated_userid:
        if request.method == 'POST':
            try:
                update_entry(request, id)
                entry = get_single_entry(request, True, True, id)
            except psycopg2.Error:
                # this will catch any errors generated by the database
                return HTTPInternalServerError
        else: # GET REQUEST
            entry = get_single_entry(request, False, True, id)
    entry['created'] = entry['created'].strftime('%b %d, %Y')
    return entry


# DETAIL PAGE
@view_config(route_name='detail', renderer='templates/detail.jinja2')
def detail_view(request):
    """view for entry (permalink for an entry)."""
    id = request.matchdict.get('id', -1)
    return get_single_entry(request, True, False, id)

def get_newest_entry(request):
    entry = Entry.get_newest()
    # cursor = request.db.cursor()
    # cursor.execute(SELECT_SINGLE_NEWEST_ENTRY)
    # keys = ('id', 'title', 'text', 'created')
    # entry = dict(zip(keys, cursor.fetchone()))
    entry.text = mdown(entry.text)
    entry.created = entry.created.strftime('%b %d, %Y')
    return to_json(entry)

def get_single_entry(request, mark_down, json, id):
    """get single entry - returns markdown if mark_down set to True"""
    # id = request.matchdict.get('id', -1)
    # cursor = request.db.cursor()
    # cursor.execute(SELECT_SINGLE_ENTRY, (id,))
    # keys = ('id', 'title', 'text', 'created')
    # entry = dict(zip(keys, cursor.fetchone()))
    entry = Entry.by_id(id)
    if mark_down:
        entry.text = mdown(entry.text)
    if json:
        return entry
    return {'entry': entry}


def do_login(request):
    username = request.params.get('username', None)
    password = request.params.get('password', None)
    if not (username and password):
        raise ValueError('both username and password are required')

    settings = request.registry.settings
    manager = BCRYPTPasswordManager()
    if username == settings.get('auth.username', ''):
        hashed = settings.get('auth.password', '')
        return manager.check(hashed, password)


@view_config(route_name='login', renderer="templates/login.jinja2")
def login(request):
    """authenticate a user by username/password"""
    username = request.params.get('username', '')
    error = ''
    if request.method == 'POST':
        error = "Login Failed"
        authenticated = False
        try:
            authenticated = do_login(request)
        except ValueError as e:
            error = str(e)

        if authenticated:
            headers = remember(request, username)
            return HTTPFound(request.route_url('home'), headers=headers)

    return {'error': error, 'username': username}


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)


def main():
    """Create a configured wsgi app"""
    # configuraton settings
    settings = {}
    settings['reload_all'] = os.environ.get('DEBUG', True)
    settings['debug_all'] = os.environ.get('DEBUG', True)
    # settings['db'] = os.environ.get(
    #     'DATABASE_URL', 'dbname=learning_journal user=edward'
    # )
    settings['sqlalchemy.url'] = os.environ.get(
        ### FIX THE DB URL FORMAT, MUST BE rfc1738 URL
        'DATABASE_URL', 'postgresql://edward:@/learning_journal'
    )
    engine = sa.engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    settings['auth.username'] = os.environ.get('AUTH_USERNAME', 'admin')
    manager = BCRYPTPasswordManager()
    settings['auth.password'] = os.environ.get(
        'AUTH_PASSWORD', manager.encode('secret')
    )
    # secret value for session signing:
    secret = os.environ.get('JOURNAL_SESSION_SECRET', 'itsaseekrit')
    session_factory = SignedCookieSessionFactory(secret)
    # secret value for auth signing
    auth_secret = os.environ.get('JOURNAL_AUTH_SECRET', 'anotherseekrit')
    # configuration setup
    config = Configurator(
        settings=settings,
        session_factory=session_factory,
        authentication_policy=AuthTktAuthenticationPolicy(
            secret=auth_secret,
            hashalg='sha512'
        ),
        authorization_policy=ACLAuthorizationPolicy(),
    )
    config.include('pyramid_tm')
    config.include('pyramid_jinja2')
    config.add_static_view('static', os.path.join(here, 'static'))
    config.add_route('home', '/')
    config.add_route('add', '/add')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('detail', '/detail/{id:\d+}')
    config.add_route('edit', '/edit')
    config.scan()

    jinja2.filters.FILTERS['markdown'] = mdown

    # serve app
    app = config.make_wsgi_app()
    return app


if __name__ == '__main__':
    app = main()
    port = os.environ.get('PORT', 5000)
    serve(app, host='0.0.0.0', port=port)
