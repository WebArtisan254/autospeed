import pytest
from autospeed import create_app
from autospeed.models import db, User, Entry
from autospeed.domain.entries import (
    create_entry_for_user,
    update_entry_for_user,
    delete_entry_for_user,
    ValidationError,
    NotFoundError,
    ForbiddenError,
)


@pytest.fixture
def app():
    app = create_app(test_config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "DATABASE_URL": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret",
        "WTF_CSRF_ENABLED": False,
        "SERVER_NAME": "localhost",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def user(app):
    with app.app_context():
        u = User(username="testuser", email="test@test.com")
        u.set_password("password123")
        db.session.add(u)
        db.session.commit()
        return u.id


@pytest.fixture
def other_user(app):
    with app.app_context():
        u = User(username="otheruser", email="other@test.com")
        u.set_password("password123")
        db.session.add(u)
        db.session.commit()
        return u.id


# ---- CREATE TESTS ----

class TestCreateEntry:
    def test_create_entry_success(self, app, user):
        with app.app_context():
            entry = create_entry_for_user(
                user_id=user,
                data={"title": "Test Entry", "content": "Some content"},
            )
            assert entry.id is not None
            assert entry.title == "Test Entry"
            assert entry.content == "Some content"
            assert entry.status == "draft"
            assert entry.user_id == user

    def test_create_entry_published(self, app, user):
        with app.app_context():
            entry = create_entry_for_user(
                user_id=user,
                data={"title": "Published Entry", "content": "Content", "status": "published"},
            )
            assert entry.status == "published"

    def test_create_entry_empty_title_raises(self, app, user):
        with app.app_context():
            with pytest.raises(ValidationError) as exc:
                create_entry_for_user(
                    user_id=user,
                    data={"title": "", "content": "Some content"},
                )
            assert exc.value.field == "title"

    def test_create_entry_invalid_status_raises(self, app, user):
        with app.app_context():
            with pytest.raises(ValidationError) as exc:
                create_entry_for_user(
                    user_id=user,
                    data={"title": "Test", "content": "Content", "status": "archived"},
                )
            assert exc.value.field == "status"

    def test_create_entry_no_content(self, app, user):
        with app.app_context():
            entry = create_entry_for_user(
                user_id=user,
                data={"title": "No Content Entry"},
            )
            assert entry.content == ""


# ---- UPDATE TESTS ----

class TestUpdateEntry:
    def test_update_entry_title(self, app, user):
        with app.app_context():
            entry = create_entry_for_user(
                user_id=user,
                data={"title": "Original Title", "content": "Content"},
            )
            updated = update_entry_for_user(
                user_id=user,
                entry_id=entry.id,
                data={"title": "Updated Title"},
            )
            assert updated.title == "Updated Title"

    def test_update_entry_content(self, app, user):
        with app.app_context():
            entry = create_entry_for_user(
                user_id=user,
                data={"title": "Title", "content": "Old content"},
            )
            updated = update_entry_for_user(
                user_id=user,
                entry_id=entry.id,
                data={"title": "Title", "content": "New content"},
            )
            assert updated.content == "New content"

    def test_update_entry_status(self, app, user):
        with app.app_context():
            entry = create_entry_for_user(
                user_id=user,
                data={"title": "Title", "content": "Content"},
            )
            updated = update_entry_for_user(
                user_id=user,
                entry_id=entry.id,
                data={"title": "Title", "status": "published"},
            )
            assert updated.status == "published"

    def test_update_entry_empty_title_raises(self, app, user):
        with app.app_context():
            entry = create_entry_for_user(
                user_id=user,
                data={"title": "Title", "content": "Content"},
            )
            with pytest.raises(ValidationError) as exc:
                update_entry_for_user(
                    user_id=user,
                    entry_id=entry.id,
                    data={"title": ""},
                )
            assert exc.value.field == "title"

    def test_update_entry_title_too_long_raises(self, app, user):
        with app.app_context():
            entry = create_entry_for_user(
                user_id=user,
                data={"title": "Title", "content": "Content"},
            )
            with pytest.raises(ValidationError) as exc:
                update_entry_for_user(
                    user_id=user,
                    entry_id=entry.id,
                    data={"title": "A" * 121},
                )
            assert exc.value.field == "title"

    def test_update_entry_not_found_raises(self, app, user):
        with app.app_context():
            with pytest.raises(NotFoundError):
                update_entry_for_user(
                    user_id=user,
                    entry_id=9999,
                    data={"title": "Title"},
                )

    def test_update_entry_wrong_user_raises(self, app, user, other_user):
        with app.app_context():
            entry = create_entry_for_user(
                user_id=user,
                data={"title": "Title", "content": "Content"},
            )
            with pytest.raises(ForbiddenError):
                update_entry_for_user(
                    user_id=other_user,
                    entry_id=entry.id,
                    data={"title": "Hacked"},
                )


# ---- DELETE TESTS ----

class TestDeleteEntry:
    def test_delete_entry_success(self, app, user):
        with app.app_context():
            entry = create_entry_for_user(
                user_id=user,
                data={"title": "To Delete", "content": "Content"},
            )
            entry_id = entry.id
            delete_entry_for_user(user_id=user, entry_id=entry_id)
            assert db.session.get(Entry, entry_id) is None

    def test_delete_entry_not_found_raises(self, app, user):
        with app.app_context():
            with pytest.raises(NotFoundError):
                delete_entry_for_user(user_id=user, entry_id=9999)

    def test_delete_entry_wrong_user_raises(self, app, user, other_user):
        with app.app_context():
            entry = create_entry_for_user(
                user_id=user,
                data={"title": "My Entry", "content": "Content"},
            )
            with pytest.raises(ForbiddenError):
                delete_entry_for_user(user_id=other_user, entry_id=entry.id)
