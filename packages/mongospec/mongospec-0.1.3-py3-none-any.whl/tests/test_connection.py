# tests/test_connection.py
import pytest
from bson import ObjectId
import mongojet
import mongospec
from mongospec import MongoDocument

pytestmark = pytest.mark.asyncio

class DummyDoc(MongoDocument):
    """Simple dummy document model for testing init binding."""
    __collection_name__ = "dummy"
    value: int

async def test_init_binds_collection_and_creates_indexes(mongo_db):
    """mongospec.init should bind collection for MongoDocument subclasses and create indexes."""
    # Define a model with an index to verify index creation
    from mongojet import IndexModel
    class IndexedDoc(MongoDocument):
        __collection_name__ = "indexed"
        __indexes__ = [IndexModel(keys=[("field", 1)], options={"unique": True})]
        field: str

    # Initially, collections not bound
    with pytest.raises(RuntimeError):
        _ = IndexedDoc.get_collection()  # should raise if not initialized:contentReference[oaicite:2]{index=2}

    # Initialize with the DummyDoc and IndexedDoc types
    await mongospec.init(mongo_db, document_types=[DummyDoc, IndexedDoc])
    # After init, the __collection__ for each should be set
    coll_dummy = DummyDoc.get_collection()
    coll_indexed = IndexedDoc.get_collection()
    assert coll_dummy.name == "dummy"
    assert coll_indexed.name == "indexed"
    # Indexes should have been created on the IndexedDoc collection:contentReference[oaicite:3]{index=3}
    indexes = await coll_indexed.list_indexes()
    # There should be a unique index on "field"
    unique_indexes = [idx for idx in indexes if list(idx["key"].items()) == [("field", 1)]]
    assert unique_indexes and unique_indexes[0].get("unique") is True

async def test_init_invalid_document_type_raises(mongo_db):
    """mongospec.init should reject non-MongoDocument types with TypeError:contentReference[oaicite:4]{index=4}."""
    # Pass an invalid type (e.g. int) in document_types
    with pytest.raises(TypeError):
        await mongospec.init(mongo_db, document_types=[int, DummyDoc])

async def test_close_is_idempotent_and_safe(mongo_db):
    """mongospec.close can be called multiple times safely:contentReference[oaicite:5]{index=5}."""
    # Closing without init should not raise
    await mongospec.close()
    # Initialize and close twice
    await mongospec.init(mongo_db, document_types=[DummyDoc])
    await mongospec.close()
    # Second close after already closed connection
    await mongospec.close()
    # If we try to use DummyDoc after closing, it should raise since collection is not initialized
    with pytest.raises(RuntimeError):
        await DummyDoc.find_one({})
