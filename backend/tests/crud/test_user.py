"""Unit tests for user CRUD operations."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import (
    get_user_by_email,
    get_user_by_id,
    create_user,
    update_last_login,
    update_user,
    deactivate_user,
    get_all_users,
    get_users_count,
)
from app.models.user import User, UserRole


@pytest.fixture
def mock_session():
    """Create a mock AsyncSession."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_user():
    """Create a sample User."""
    user = MagicMock(spec=User)
    user.id = 1
    user.email = "admin@example.com"
    user.hashed_password = "hashed_password_123"
    user.full_name = "Admin User"
    user.role = UserRole.ADMIN
    user.is_active = True
    user.last_login_at = None
    user.created_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    return user


@pytest.fixture
def sample_users():
    """Create a list of sample users."""
    users = []

    # User 1 - Admin
    user1 = MagicMock(spec=User)
    user1.id = 1
    user1.email = "admin@example.com"
    user1.full_name = "Admin User"
    user1.role = UserRole.ADMIN
    user1.is_active = True
    users.append(user1)

    # User 2 - Publisher
    user2 = MagicMock(spec=User)
    user2.id = 2
    user2.email = "publisher@example.com"
    user2.full_name = "Publisher User"
    user2.role = UserRole.PUBLISHER
    user2.is_active = True
    users.append(user2)

    # User 3 - Inactive Publisher
    user3 = MagicMock(spec=User)
    user3.id = 3
    user3.email = "inactive@example.com"
    user3.full_name = "Inactive User"
    user3.role = UserRole.PUBLISHER
    user3.is_active = False
    users.append(user3)

    return users


@pytest.fixture
def user_data():
    """Sample user creation data."""
    return {
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "New User",
        "role": UserRole.PUBLISHER,
        "is_active": True,
    }


class TestGetUserByEmail:
    """Test get_user_by_email function."""

    @pytest.mark.asyncio
    async def test_get_user_by_email_found(self, mock_session, sample_user):
        """Test getting user by email when found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        user = await get_user_by_email(mock_session, "admin@example.com")

        assert user is not None
        assert user.email == "admin@example.com"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, mock_session):
        """Test getting user by email when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        user = await get_user_by_email(mock_session, "nonexistent@example.com")

        assert user is None


class TestGetUserById:
    """Test get_user_by_id function."""

    @pytest.mark.asyncio
    async def test_get_user_by_id_found(self, mock_session, sample_user):
        """Test getting user by ID when found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        user = await get_user_by_id(mock_session, 1)

        assert user is not None
        assert user.id == 1
        assert user.email == "admin@example.com"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, mock_session):
        """Test getting user by ID when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        user = await get_user_by_id(mock_session, 999)

        assert user is None


class TestCreateUser:
    """Test create_user function."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_session, user_data):
        """Test creating a user successfully."""
        created_user = MagicMock(spec=User)
        created_user.email = user_data["email"]
        created_user.full_name = user_data["full_name"]
        created_user.role = user_data["role"]
        created_user.is_active = True

        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch("app.crud.user.get_password_hash", return_value="hashed_pwd"):
            with patch("app.crud.user.User", return_value=created_user):
                user = await create_user(mock_session, user_data)

                assert user.email == "newuser@example.com"
                assert user.full_name == "New User"
                assert user.is_active is True
                mock_session.add.assert_called_once()
                mock_session.commit.assert_called_once()
                mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_with_defaults(self, mock_session):
        """Test creating user with default role and is_active."""
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User",
        }

        created_user = MagicMock(spec=User)
        created_user.email = user_data["email"]
        created_user.role = UserRole.PUBLISHER
        created_user.is_active = True

        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch("app.crud.user.get_password_hash", return_value="hashed"):
            with patch("app.crud.user.User", return_value=created_user):
                user = await create_user(mock_session, user_data)

                assert user.role == UserRole.PUBLISHER
                assert user.is_active is True


class TestUpdateLastLogin:
    """Test update_last_login function."""

    @pytest.mark.asyncio
    async def test_update_last_login_success(self, mock_session, sample_user):
        """Test updating last login timestamp."""
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch("app.crud.user.get_user_by_id", return_value=sample_user):
            user = await update_last_login(mock_session, 1)

            assert user.last_login_at is not None
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_last_login_not_found(self, mock_session):
        """Test updating last login for non-existent user."""
        with patch("app.crud.user.get_user_by_id", return_value=None):
            user = await update_last_login(mock_session, 999)

            assert user is None
            mock_session.commit.assert_not_called()


class TestUpdateUser:
    """Test update_user function."""

    @pytest.mark.asyncio
    async def test_update_user_basic_fields(self, mock_session, sample_user):
        """Test updating basic user fields."""
        update_data = {"full_name": "Updated Name", "is_active": False}

        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch("app.crud.user.get_user_by_id", return_value=sample_user):
            user = await update_user(mock_session, 1, update_data)

            assert user.full_name == "Updated Name"
            assert user.is_active is False
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_password(self, mock_session, sample_user):
        """Test updating user password (should hash it)."""
        update_data = {"password": "NewPassword123!"}

        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch("app.crud.user.get_user_by_id", return_value=sample_user):
            with patch("app.crud.user.get_password_hash", return_value="new_hash") as mock_hash:
                user = await update_user(mock_session, 1, update_data)

                mock_hash.assert_called_once_with("NewPassword123!")
                assert user.hashed_password == "new_hash"

    @pytest.mark.asyncio
    async def test_update_user_ignores_protected_fields(self, mock_session, sample_user):
        """Test that protected fields (id, hashed_password) are ignored."""
        update_data = {"id": 999, "hashed_password": "should_not_update"}

        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch("app.crud.user.get_user_by_id", return_value=sample_user):
            user = await update_user(mock_session, 1, update_data)

            # ID should remain unchanged
            assert user.id == 1
            # hashed_password should remain unchanged
            assert user.hashed_password == "hashed_password_123"

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, mock_session):
        """Test updating non-existent user."""
        update_data = {"full_name": "New Name"}

        with patch("app.crud.user.get_user_by_id", return_value=None):
            user = await update_user(mock_session, 999, update_data)

            assert user is None
            mock_session.commit.assert_not_called()


class TestDeactivateUser:
    """Test deactivate_user function."""

    @pytest.mark.asyncio
    async def test_deactivate_user_success(self, mock_session, sample_user):
        """Test deactivating a user."""
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch("app.crud.user.get_user_by_id", return_value=sample_user):
            user = await deactivate_user(mock_session, 1)

            assert user.is_active is False
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_deactivate_user_not_found(self, mock_session):
        """Test deactivating non-existent user."""
        with patch("app.crud.user.get_user_by_id", return_value=None):
            user = await deactivate_user(mock_session, 999)

            assert user is None
            mock_session.commit.assert_not_called()


class TestGetAllUsers:
    """Test get_all_users function."""

    @pytest.mark.asyncio
    async def test_get_all_users_no_filters(self, mock_session, sample_users):
        """Test getting all users without filters."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_users
        mock_session.execute.return_value = mock_result

        users = await get_all_users(mock_session)

        assert len(users) == 3
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_users_with_role_filter(self, mock_session, sample_users):
        """Test filtering users by role."""
        publishers = [u for u in sample_users if u.role == UserRole.PUBLISHER]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = publishers
        mock_session.execute.return_value = mock_result

        users = await get_all_users(mock_session, filters={"role": UserRole.PUBLISHER})

        assert len(users) == 2
        assert all(u.role == UserRole.PUBLISHER for u in users)

    @pytest.mark.asyncio
    async def test_get_all_users_with_is_active_filter(self, mock_session, sample_users):
        """Test filtering users by active status."""
        active_users = [u for u in sample_users if u.is_active]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = active_users
        mock_session.execute.return_value = mock_result

        users = await get_all_users(mock_session, filters={"is_active": True})

        assert len(users) == 2
        assert all(u.is_active for u in users)

    @pytest.mark.asyncio
    async def test_get_all_users_with_pagination(self, mock_session, sample_users):
        """Test pagination parameters."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_users[1]]
        mock_session.execute.return_value = mock_result

        users = await get_all_users(mock_session, skip=1, limit=1)

        assert len(users) == 1
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_users_combined_filters(self, mock_session, sample_users):
        """Test combining role and is_active filters."""
        filtered = [
            u for u in sample_users
            if u.role == UserRole.PUBLISHER and u.is_active
        ]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = filtered
        mock_session.execute.return_value = mock_result

        users = await get_all_users(
            mock_session,
            filters={"role": UserRole.PUBLISHER, "is_active": True}
        )

        assert len(users) == 1
        assert users[0].role == UserRole.PUBLISHER
        assert users[0].is_active is True

    @pytest.mark.asyncio
    async def test_get_all_users_empty_result(self, mock_session):
        """Test when no users match filters."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        users = await get_all_users(mock_session, filters={"role": UserRole.ADMIN})

        assert users == []


class TestGetUsersCount:
    """Test get_users_count function."""

    @pytest.mark.asyncio
    async def test_get_users_count_no_filters(self, mock_session):
        """Test counting all users."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 10
        mock_session.execute.return_value = mock_result

        count = await get_users_count(mock_session)

        assert count == 10
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_users_count_with_role_filter(self, mock_session):
        """Test counting users by role."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 5
        mock_session.execute.return_value = mock_result

        count = await get_users_count(mock_session, filters={"role": UserRole.PUBLISHER})

        assert count == 5

    @pytest.mark.asyncio
    async def test_get_users_count_with_is_active_filter(self, mock_session):
        """Test counting active users."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 8
        mock_session.execute.return_value = mock_result

        count = await get_users_count(mock_session, filters={"is_active": True})

        assert count == 8

    @pytest.mark.asyncio
    async def test_get_users_count_zero(self, mock_session):
        """Test when count is zero."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_session.execute.return_value = mock_result

        count = await get_users_count(mock_session)

        assert count == 0


class TestUserIntegration:
    """Integration tests for user CRUD operations."""

    @pytest.mark.asyncio
    async def test_full_user_lifecycle(self, mock_session, user_data, sample_user):
        """Test complete user lifecycle: create → get → update → deactivate."""
        # 1. Create user
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch("app.crud.user.get_password_hash", return_value="hashed"):
            with patch("app.crud.user.User", return_value=sample_user):
                created_user = await create_user(mock_session, user_data)
                assert created_user.email == "admin@example.com"

        # 2. Get user by ID
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        user = await get_user_by_id(mock_session, 1)
        assert user is not None

        # 3. Update user
        with patch("app.crud.user.get_user_by_id", return_value=sample_user):
            updated = await update_user(mock_session, 1, {"full_name": "Updated"})
            assert updated.full_name == "Updated"

        # 4. Deactivate user
        with patch("app.crud.user.get_user_by_id", return_value=sample_user):
            deactivated = await deactivate_user(mock_session, 1)
            assert deactivated.is_active is False

    @pytest.mark.asyncio
    async def test_filter_consistency(self, mock_session, sample_users):
        """Test that filters work consistently across get and count."""
        filters = {"role": UserRole.PUBLISHER, "is_active": True}

        # Mock for get_all_users
        filtered_users = [
            u for u in sample_users
            if u.role == UserRole.PUBLISHER and u.is_active
        ]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = filtered_users
        mock_session.execute.return_value = mock_result

        users = await get_all_users(mock_session, filters=filters)
        assert len(users) == 1

        # Mock for get_users_count
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1
        mock_session.execute.return_value = mock_count_result

        count = await get_users_count(mock_session, filters=filters)
        assert count == len(users)
