"""
Full-text search service using Whoosh
"""
import os
from typing import List, Optional
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID, KEYWORD, DATETIME
from whoosh.qparser import MultifieldParser, QueryParser
from whoosh.query import And, Or, Term
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.document import QMSDocument


class SearchService:
    """
    Full-text search service for documents
    """

    # Whoosh schema for document indexing
    SCHEMA = Schema(
        doc_id=ID(stored=True, unique=True),
        doc_number=ID(stored=True),
        title=TEXT(stored=True),
        description=TEXT(stored=True),
        content=TEXT,
        owner=KEYWORD(stored=True),
        type=KEYWORD(stored=True),
        status=KEYWORD(stored=True),
        created_at=DATETIME(stored=True)
    )

    def __init__(self, index_dir: str = "./storage/search_index"):
        """
        Initialize search service

        Args:
            index_dir: Directory to store search index
        """
        self.index_dir = index_dir

        # Create index directory if it doesn't exist
        if not os.path.exists(index_dir):
            os.makedirs(index_dir)

        # Create or open index
        if not exists_in(index_dir):
            self.index = create_in(index_dir, self.SCHEMA)
        else:
            self.index = open_dir(index_dir)

    def index_document(self, document: QMSDocument):
        """
        Add or update document in search index

        Args:
            document: Document to index
        """
        writer = self.index.writer()

        writer.update_document(
            doc_id=str(document.id),
            doc_number=document.doc_number,
            title=document.title,
            description=document.description or "",
            content=document.content_text or "",
            owner=document.owner,
            type=document.type.value,
            status=document.status.value,
            created_at=document.created_at
        )

        writer.commit()

    def remove_document(self, document_id: int):
        """
        Remove document from search index

        Args:
            document_id: Document ID to remove
        """
        writer = self.index.writer()
        writer.delete_by_term('doc_id', str(document_id))
        writer.commit()

    def search(
        self,
        query_string: str,
        fields: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[dict]:
        """
        Search documents by query string

        Args:
            query_string: Search query
            fields: Fields to search in (default: title, description, content)
            limit: Maximum results to return

        Returns:
            List of search results with document IDs and scores
        """
        if fields is None:
            fields = ["title", "description", "content"]

        with self.index.searcher() as searcher:
            parser = MultifieldParser(fields, schema=self.SCHEMA)
            query = parser.parse(query_string)

            results = searcher.search(query, limit=limit)

            return [
                {
                    "doc_id": int(hit["doc_id"]),
                    "doc_number": hit["doc_number"],
                    "title": hit["title"],
                    "score": hit.score
                }
                for hit in results
            ]

    def search_by_field(
        self,
        field: str,
        value: str,
        limit: int = 100
    ) -> List[dict]:
        """
        Search documents by specific field

        Args:
            field: Field name
            value: Field value to search
            limit: Maximum results

        Returns:
            List of matching documents
        """
        with self.index.searcher() as searcher:
            parser = QueryParser(field, schema=self.SCHEMA)
            query = parser.parse(value)

            results = searcher.search(query, limit=limit)

            return [
                {
                    "doc_id": int(hit["doc_id"]),
                    "doc_number": hit["doc_number"],
                    "title": hit["title"]
                }
                for hit in results
            ]

    def rebuild_index(self, db: Session):
        """
        Rebuild entire search index from database

        Args:
            db: Database session
        """
        # Clear existing index
        writer = self.index.writer()
        writer.commit()  # Commit to clear

        # Re-index all documents
        documents = db.query(QMSDocument).all()

        writer = self.index.writer()
        for doc in documents:
            writer.add_document(
                doc_id=str(doc.id),
                doc_number=doc.doc_number,
                title=doc.title,
                description=doc.description or "",
                content=doc.content_text or "",
                owner=doc.owner,
                type=doc.type.value,
                status=doc.status.value,
                created_at=doc.created_at
            )

        writer.commit()
