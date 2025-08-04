"""
Google Cloud Firestore database wrapper.

This module provides a simplified interface for interacting with Google Cloud Firestore,
implementing common database operations such as CRUD operations, batch writes, and
filtered queries. It abstracts Firestore-specific implementation details and provides
a more intuitive API.

Example:
    >>> db = FirestoreWrapper()
    >>> user_data = db.get_document("users", "user123")
    >>> db.create_document("users", {"name": "John", "age": 30})
"""

import logging
from pydantic import BaseModel, ValidationError
from typing import Dict, List, Any, Optional, TypeVar
from google.cloud import firestore

from ..utils import constants as kk
import commons.logger as _

# Define a type variable for handling Pydantic models
MODEL_TYPE = TypeVar("MODEL_TYPE", bound=BaseModel)

logger = logging.getLogger("Firestore Wrapper")


class FirestoreWrapper:
    """A wrapper class for Google Cloud Firestore operations.

    This class provides a simplified interface for common Firestore operations
    including CRUD operations, batch writes, and queries.

    Args:
        database: The name of the Firestore database to connect to.
    """

    def __init__(
        self,
        project: str = kk.PROJECT_ID,
        database: str = kk.FIRESTORE_DATABASE_INTERNAL,
    ):
        """Initialize the Firestore client with the specified database."""
        self.db = firestore.Client(project=project, database=database)

    def get_collection(self, collection_name: str):
        """Get a reference to a Firestore collection.

        Args:
            collection_name: Name of the collection.

        Returns:
            CollectionReference: A reference to the specified collection.
        """
        return self.db.collection(collection_name)

    def get_document(
        self, collection_name: str, document_id: str, include_document_id: bool = False
    ) -> dict:
        """Retrieves a single document from a Firestore collection.

        Args:
            collection_name: Name of the collection containing the document
            document_id: Unique identifier of the document to retrieve
            include_document_id: When True, adds the document ID to the returned data
                with key 'document_id'

        Returns:
            dict: Document data as a dictionary, or None if the document doesn't exist

        Example:
            >>> doc = db.get_document("users", "user123", include_document_id=True)
            >>> if doc:
            ...     print(f"Found user: {doc['name']}")
        """
        doc = self.db.collection(collection_name).document(document_id).get()
        if not doc.exists:
            return None
        data = doc.to_dict()
        if include_document_id and data and "document_id" not in data:
            data["document_id"] = doc.id
        return data

    def get_document_pydantic(
        self,
        collection_name: str,
        document_id: str,
        pydantic_model: type[MODEL_TYPE],
        include_document_id: bool = False,
    ) -> MODEL_TYPE:
        """Retrieve a document from Firestore and convert it to a Pydantic model.

        Args:
            collection_name: Name of the collection containing the document.
            document_id: ID of the document to retrieve.
            pydantic_model: Pydantic model to convert the document data to.
            include_document_id: If True, includes document ID in model data with key '_document_id'.

        Returns:
            Any: Pydantic model instance with the document data.
        """
        doc_data = self.get_document(collection_name, document_id, include_document_id)
        return pydantic_model(**doc_data) if doc_data else None

    def create_document(
        self,
        collection_name: str,
        document_data: Dict[str, Any],
        document_id: Optional[str] = None,
    ) -> str:
        """Create a new document in Firestore.

        Args:
            collection_name: Name of the collection to create document in.
            document_data: Dictionary containing the document data.
            document_id: Optional custom document ID. If not provided, Firestore will auto-generate one.

        Returns:
            str: ID of the created document.
        """
        collection_ref = self.db.collection(collection_name)
        if document_id:
            doc_ref = collection_ref.document(document_id)
            doc_ref.set(document_data)
            return document_id
        else:
            doc_ref = collection_ref.add(document_data)[1]
            return doc_ref.id

    def update_document(
        self, collection_name: str, document_id: str, document_data: Dict[str, Any]
    ) -> None:
        """Update an existing document in Firestore.

        Args:
            collection_name: Name of the collection containing the document.
            document_id: ID of the document to update.
            document_data: Dictionary containing the fields to update.

        Raises:
            google.cloud.exceptions.NotFound: If the document doesn't exist.
        """
        doc_ref = self.db.collection(collection_name).document(document_id)
        doc_ref.update(document_data)

    def delete_document(self, collection_name: str, document_id: str) -> None:
        """Delete a document from Firestore.

        Args:
            collection_name: Name of the collection containing the document.
            document_id: ID of the document to delete.
        """
        doc_ref = self.db.collection(collection_name).document(document_id)
        doc_ref.delete()

    def batch_write(self, operations: List[Dict[str, Any]]) -> None:
        """Perform multiple write operations in a single batch.

        Args:
            operations: List of dictionaries, each containing:
                - 'collection': Name of the collection
                - 'document_id': ID of the document
                - 'data': Document data
                - 'operation': Type of operation ('set', 'update', or 'delete')

        Example:
            operations = [
                {'collection': 'users', 'document_id': 'user1',
                 'data': {'name': 'John'}, 'operation': 'set'},
                {'collection': 'users', 'document_id': 'user2',
                 'data': {'name': 'Jane'}, 'operation': 'set'}
            ]
        """
        batch = self.db.batch()
        batch_size: int = 500

        for i, op in enumerate(operations):
            collection = op.get("collection")
            doc_id = op.get("document_id")
            data = op.get("data")
            operation = op.get("operation", "set")

            if not doc_id:
                doc_ref = self.db.collection(collection).document()
            else:
                doc_ref = self.db.collection(collection).document(doc_id)
            if operation == "set":
                batch.set(doc_ref, data)
            elif operation == "update":
                batch.update(doc_ref, data)
            elif operation == "delete":
                batch.delete(doc_ref)

            # Commit the batch every batch_size operations
            if i % batch_size == 0:
                batch.commit()
                batch = self.db.batch()

        batch.commit()

    def query_documents(
        self,
        collection_name: str,
        filters: List[Dict[str, Any]] = None,
        include_document_id: bool = False,
    ) -> List[Dict[str, Any]]:
        """Queries documents in a collection using optional filters.

        Args:
            collection_name: Name of the collection to query
            filters: List of filter dictionaries, where each dictionary contains:
                - field: Name of the field to filter on
                - operation: Comparison operator (e.g., '==', '>', '<')
                - value: Value to compare against
            include_document_id: When True, adds document IDs to the returned data

        Returns:
            List[Dict[str, Any]]: List of documents matching the query criteria

        Example:
            >>> filters = [
            ...     {"field": "age", "operation": ">=", "value": 18},
            ...     {"field": "city", "operation": "==", "value": "New York"}
            ... ]
            >>> adult_users = db.query_documents("users", filters)
        """
        query = self.db.collection(collection_name)

        if not query.limit(1).get():
            logger.info("Collection %s does not exist", collection_name)
            return []

        if filters:
            for filter_dict in filters:
                field = filter_dict.get("field")
                op = filter_dict.get("operation")
                value = filter_dict.get("value")
                query = query.where(filter=firestore.FieldFilter(field, op, value))

        docs = query.stream()
        if include_document_id:
            return [dict(document_id=doc.id, **doc.to_dict()) for doc in docs]
        return [doc.to_dict() for doc in docs]

    def query_documents_pydantic(
        self,
        collection_name: str,
        pydantic_model: type[MODEL_TYPE],
        filters: List[Dict[str, Any]] | None = None,
        include_document_id: bool = False,
    ) -> list[MODEL_TYPE]:
        """Queries documents in a Firestore collection collection using optional filters

        pydantic_model: type[MODEL_TYPE],

        Args:
            collection_name: Name of the collection to query
            filters: List of filter dictionaries, where each dictionary contains:
                - field: Name of the field to filter on
                - operation: Comparison operator (e.g., '==', '>', '<')
                - value: Value to compare against
            include_document_id: When True, adds document IDs to the returned data
            pydantic_model: Pydantic model to convert the document data to.

        Returns:
            List[MODEL_TYPE]: A list of objects of type `MODEL_TYPE` (the specified Pydantic model).
            Each document in the Firestore collection that matches the query criteria is converted
            into an instance of the Pydantic model. If `include_document_id` is True, the document ID
            is included in the data passed to the Pydantic model.

        Example:
            >>> filters = [
            ...     {"field": "age", "operation": ">=", "value": 18},
            ...     {"field": "city", "operation": "==", "value": "New York"}
            ... ]
            >>> adult_users = db.query_documents_pydantic(
            ...     "users",
            ...     filters=filters,
            ...     pydantic_model=User,
            ...     include_document_id=True
            ... )
        """

        docs = self.query_documents(
            collection_name=collection_name,
            filters=filters,
            include_document_id=include_document_id,
        )

        parsed_docs: list[MODEL_TYPE] = []

        for doc in docs:
            try:
                parsed_doc: type[MODEL_TYPE] = pydantic_model.model_validate(doc)
                parsed_docs.append(parsed_doc)

            except ValidationError as e:
                logger.warning(
                    "Error validating document %s, due to validation error: %s",
                    doc.get("document_id", "unknown"),
                    e.json(),
                )
                continue

        return parsed_docs

    def generate_resource_path(
        self, collection_names: list[str], document_ids: list[str]
    ) -> str:
        """
        Function used to create a document path from a list of nested collections' names and document IDs.
        The path is created with the following format: collection_name/document_id/sub_collection_name/sub_collection_document_id/...
        The number of document IDs must be equal to or one element less than the number of collection names.

        Example:
            >>> collection_names = ["projects", "raw_objects"]
            >>> document_ids = ["project_id", "raw_object_id"]
            >>> path = db.generate_resource_path(collection_names, document_ids)
            >>> print(path)
            "projects/project_id/raw_objects/raw_object_id"
        """
        if len(document_ids) < len(collection_names) - 1:
            raise ValueError(
                "The number of document IDs must be equal to or one element less than the number of collection names to create the paths like: collection_name/document_id/sub_collection_name/sub_collection_document_id"
            )

        path = ""
        for collection_name, document_id in zip(collection_names, document_ids):
            path += f"{collection_name}/{document_id}/"

        leftover_collection_names = collection_names[len(document_ids) :]

        for collection_name in leftover_collection_names:
            path += f"{collection_name}/"

        path = path.rstrip("/")

        return path

    def generate_document_id(
        self,
        resource_path: str,
    ) -> str:
        """
        Function used to generate a document ID given its resource path up to the last nested collection.
        The ID is created with the following format: collection_name/document_id/sub_collection_name/__generated_id__

        Example:
            >>> resource_path = "projects/project_id/raw_objects/raw_object_id"
            >>> id = db.generate_document_id(resource_path)
            >>> print(id)
            "collection_name/document_id/sub_collection_name/__generated_id__"
        """

        document_id = self.db.collection(resource_path).document().id

        return document_id
