from project.models import db, User, Set, Verse

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

db.drop_all()
db.create_all()


hashed = bcrypt.generate_password_hash("testing").decode('utf8')

user = User(username="test",
            password=hashed,
            email="davidlee980804@gmail.com",
            first_name="David",
            last_name="Lee",
            is_admin=True)

db.session.add(user)
db.session.commit()


verse1 = Verse(
    reference="John 3:16",
    verse='“For God so loved the world, that he gave his only Son, \
        that whoever believes in him should not perish but have eternal life.'
)

verse2 = Verse(
    reference="Romans 5:8",
    verse="but God shows his love for us in that while we were still sinners, \
        Christ died for us."
)

db.session.add(verse1, verse2)
db.session.commit()


new_set = Set(
    name="Test Set",
    description="Testing purposes",
    user_id=user.id
)

db.session.add(new_set)
db.session.commit()

new_set.verses.append(verse1)
new_set.verses.append(verse2)
db.session.commit()

Set.reindex()
