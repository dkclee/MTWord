
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from flask_login import UserMixin

from project.search import add_to_index, remove_from_index, query_index

db = SQLAlchemy()

bcrypt = Bcrypt()


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


class User(UserMixin, db.Model):
    """ Record of all the users of the app """

    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    first_name = db.Column(db.String(50),
                           nullable=False)
    last_name = db.Column(db.String(50),
                          nullable=False)
    email = db.Column(db.Text,
                      nullable=False)
    username = db.Column(db.String(30),
                         nullable=False,
                         unique=True)
    password = db.Column(db.Text,
                         nullable=False)
    bio = db.Column(db.Text)

    is_admin = db.Column(db.Boolean,
                         default=False,
                         nullable=False)
    password_reset_token = db.Column(db.Text)

    # Relationship with Sets and favorites
    sets = db.relationship('Set',
                           backref='user',
                           cascade="all, delete",)
    favorite_sets = db.relationship('Set',
                                    secondary='favorites',
                                    cascade="all, delete",)

    def __repr__(self):
        return f"<User {self.full_name}>"

    def update_password(self, pwd):
        """ Update the user's password """
        self.password = bcrypt.generate_password_hash(pwd).decode('utf8')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def register(cls, username, pwd, email, f_name, l_name):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd).decode('utf8')

        # return instance of user w/username and hashed pwd along with
        # email, first_name and last_name
        return cls(username=username,
                   password=hashed,
                   email=email,
                   first_name=f_name,
                   last_name=l_name)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False


class Set(SearchableMixin, db.Model):
    """Set containing various bible verses."""

    __tablename__ = "sets"
    __searchable__ = ['name', 'description']

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.String(50),
                     nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=db.func.now())

    verses = db.relationship('Verse',
                             secondary='sets_verses',
                             backref='sets',
                             cascade="all, delete")

    def __repr__(self):
        return f"<Set {self.name} by {self.user.first_name} \
            {self.user.last_name}>"


class Favorite(db.Model):
    """ User's favorited sets """

    __tablename__ = "favorites"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    set_id = db.Column(db.Integer,
                       db.ForeignKey('sets.id'))
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'))


class SetVerse(db.Model):
    """Mapping of a verse to a set."""

    __tablename__ = "sets_verses"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    set_id = db.Column(db.Integer,
                       db.ForeignKey('sets.id'))
    verse_id = db.Column(db.Integer,
                         db.ForeignKey('verses.id'))


class Verse(db.Model):
    """Verses."""

    __tablename__ = "verses"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    reference = db.Column(db.String(50),
                          nullable=False)
    verse = db.Column(db.Text,
                      nullable=False)

    def __repr__(self):
        return f"<Verse {self.reference} {self.verse[:10]}>"

    @property
    def hashed(self):
        return hash(self.reference)


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)
