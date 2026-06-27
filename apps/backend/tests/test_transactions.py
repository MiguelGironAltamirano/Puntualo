"""tests/test_transactions.py - Tests to validate database transaction atomicity, rollbacks, and parallel ACID compliance."""
import pytest
import asyncio
import uuid
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_atomic_rollback_on_failure(test_db: AsyncSession):
    """Test that database mutations are rolled back atomically when an operation fails."""
    # Start a transaction block
    async with test_db.begin_nested():
        # Insert a valid user
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email="rolledback@example.com",
            hashed_password="password",
            full_name="Rolled Back",
            username="rolledback_user",
        )
        test_db.add(user)
        await test_db.flush()

        # Insert an invalid user to force an IntegrityError (null email)
        invalid_user = User(
            id=uuid.uuid4(),
            email=None,  # Should fail not-null constraint
            hashed_password="password",
            full_name="Invalid",
            username="invalid_user",
        )
        test_db.add(invalid_user)
        
        with pytest.raises(IntegrityError):
            await test_db.flush()
        
        # Explicitly roll back the nested transaction
        await test_db.rollback()

    # Query the database to ensure the first (valid) user was NOT committed/saved
    stmt = select(User).where(User.id == user_id)
    result = (await test_db.execute(stmt)).scalar_one_or_none()
    assert result is None


@pytest.mark.asyncio
async def test_concurrent_transactions_acid(test_db: AsyncSession):
    """Test that concurrent transactions run safely and maintain ACID properties."""
    user_ids = [uuid.uuid4() for _ in range(10)]
    
    async def create_user_task(user_id: uuid.UUID, index: int):
        # We must use separate session instances for concurrent tasks
        async with AsyncSession(bind=test_db.bind, expire_on_commit=False) as session:
            user = User(
                id=user_id,
                email=f"concurrent_{index}@example.com",
                hashed_password="password",
                full_name=f"Concurrent User {index}",
                username=f"concurrent_{index}",
            )
            session.add(user)
            await session.commit()

    # Run tasks concurrently using asyncio.gather
    tasks = [create_user_task(uid, i) for i, uid in enumerate(user_ids)]
    await asyncio.gather(*tasks)

    # Verify that all 10 users were successfully inserted and committed
    stmt = select(User).where(User.email.like("concurrent_%"))
    users = (await test_db.execute(stmt)).scalars().all()
    assert len(users) == 10
