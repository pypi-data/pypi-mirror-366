# tests/conftest.py
import pytest_asyncio
import pytest
from bson import ObjectId
import mongojet
import mongospec

# Mark all tests using this fixture as async tests
pytestmark = pytest.mark.asyncio

@pytest_asyncio.fixture
async def mongo_db():
    """Provide a clean MongoDB database for each test and ensure cleanup."""
    # Connect to MongoDB (adjust URI via MONGODB_URI env var if needed)
    client = await mongojet.create_client("mongodb://localhost:27017")
    db = client.get_database("mongospec_tests")
    # Clean database at start of test
    await db.drop()
    try:
        db = client.get_database("mongospec_tests")
        yield db  # run the test using this database
    finally:
        # Drop database and close connections after test
        await db.drop()
        await mongospec.close()   # closes via _DatabaseConnection (safe to call even if not connected)
