"""
Document Linking Service
Handles bidirectional linking and traceability between documents
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from backend.models.document import Document, DocumentLink, DocumentAuditLog


class LinkingService:
    """Service for managing document relationships and traceability"""

    def __init__(self, db: Session):
        self.db = db

    def create_link(
        self,
        source_document_id: int,
        target_document_id: int,
        link_type: str,
        description: Optional[str] = None,
        is_bidirectional: bool = False,
        strength: str = "normal",
        user_id: Optional[int] = None
    ) -> dict:
        """
        Create a link between two documents

        Args:
            source_document_id: Source document ID
            target_document_id: Target document ID
            link_type: Type of link (parent-child, reference, related, supersedes, implements)
            description: Optional description
            is_bidirectional: Whether the link is bidirectional
            strength: Link strength (strong, normal, weak)
            user_id: User creating the link

        Returns:
            Created link information
        """
        # Validate documents exist
        source = self._get_document(source_document_id)
        target = self._get_document(target_document_id)

        # Prevent self-linking
        if source_document_id == target_document_id:
            raise ValueError("Cannot link a document to itself")

        # Check if link already exists
        existing = self.db.query(DocumentLink).filter(
            DocumentLink.source_document_id == source_document_id,
            DocumentLink.target_document_id == target_document_id,
            DocumentLink.link_type == link_type
        ).first()

        if existing:
            raise ValueError("Link already exists between these documents")

        # Create link
        link = DocumentLink(
            source_document_id=source_document_id,
            target_document_id=target_document_id,
            link_type=link_type,
            description=description,
            is_bidirectional=is_bidirectional,
            strength=strength
        )

        self.db.add(link)

        # Create reverse link if bidirectional
        if is_bidirectional:
            reverse_link = DocumentLink(
                source_document_id=target_document_id,
                target_document_id=source_document_id,
                link_type=self._get_reverse_link_type(link_type),
                description=description,
                is_bidirectional=True,
                strength=strength
            )
            self.db.add(reverse_link)

        # Create audit log
        if user_id:
            self._create_audit_log(
                document_id=source_document_id,
                user_id=user_id,
                action="link_created",
                notes=f"Linked to {target.document_number} ({link_type})"
            )

        self.db.commit()

        return {
            'status': 'success',
            'message': 'Link created successfully',
            'link_id': link.id,
            'source': source.document_number,
            'target': target.document_number,
            'link_type': link_type,
            'is_bidirectional': is_bidirectional
        }

    def remove_link(
        self,
        link_id: int,
        user_id: Optional[int] = None
    ) -> dict:
        """Remove a document link"""
        link = self.db.query(DocumentLink).filter(DocumentLink.id == link_id).first()

        if not link:
            raise ValueError(f"Link not found: {link_id}")

        # If bidirectional, remove reverse link too
        if link.is_bidirectional:
            reverse_link = self.db.query(DocumentLink).filter(
                DocumentLink.source_document_id == link.target_document_id,
                DocumentLink.target_document_id == link.source_document_id,
                DocumentLink.link_type == self._get_reverse_link_type(link.link_type)
            ).first()
            if reverse_link:
                self.db.delete(reverse_link)

        # Create audit log
        if user_id:
            self._create_audit_log(
                document_id=link.source_document_id,
                user_id=user_id,
                action="link_removed",
                notes=f"Removed link to document ID {link.target_document_id} ({link.link_type})"
            )

        self.db.delete(link)
        self.db.commit()

        return {
            'status': 'success',
            'message': 'Link removed successfully'
        }

    def get_document_links(
        self,
        document_id: int,
        direction: str = "all"  # "outgoing", "incoming", "all"
    ) -> Dict[str, List[dict]]:
        """
        Get all links for a document

        Args:
            document_id: Document ID
            direction: Link direction ("outgoing", "incoming", "all")

        Returns:
            Dictionary with categorized links
        """
        result = {
            'outgoing': [],
            'incoming': [],
            'summary': {
                'total_outgoing': 0,
                'total_incoming': 0,
                'by_type': {}
            }
        }

        if direction in ["outgoing", "all"]:
            outgoing = self.db.query(DocumentLink).filter(
                DocumentLink.source_document_id == document_id
            ).all()

            for link in outgoing:
                target_doc = self._get_document(link.target_document_id)
                result['outgoing'].append({
                    'link_id': link.id,
                    'target_id': link.target_document_id,
                    'target_number': target_doc.document_number,
                    'target_title': target_doc.title,
                    'target_level': target_doc.level.value,
                    'link_type': link.link_type,
                    'description': link.description,
                    'strength': link.strength,
                    'is_bidirectional': link.is_bidirectional
                })

            result['summary']['total_outgoing'] = len(outgoing)

        if direction in ["incoming", "all"]:
            incoming = self.db.query(DocumentLink).filter(
                DocumentLink.target_document_id == document_id
            ).all()

            for link in incoming:
                source_doc = self._get_document(link.source_document_id)
                result['incoming'].append({
                    'link_id': link.id,
                    'source_id': link.source_document_id,
                    'source_number': source_doc.document_number,
                    'source_title': source_doc.title,
                    'source_level': source_doc.level.value,
                    'link_type': link.link_type,
                    'description': link.description,
                    'strength': link.strength,
                    'is_bidirectional': link.is_bidirectional
                })

            result['summary']['total_incoming'] = len(incoming)

        # Count by type
        all_links = result['outgoing'] + result['incoming']
        for link in all_links:
            link_type = link['link_type']
            result['summary']['by_type'][link_type] = result['summary']['by_type'].get(link_type, 0) + 1

        return result

    def get_hierarchy(self, document_id: int, max_depth: int = 5) -> dict:
        """
        Get document hierarchy (parent and children)

        Args:
            document_id: Root document ID
            max_depth: Maximum depth to traverse

        Returns:
            Hierarchical structure
        """
        document = self._get_document(document_id)

        hierarchy = {
            'id': document.id,
            'document_number': document.document_number,
            'title': document.title,
            'level': document.level.value,
            'children': [],
            'parent': None
        }

        # Get parent if exists
        if document.parent_document_id:
            parent = self._get_document(document.parent_document_id)
            hierarchy['parent'] = {
                'id': parent.id,
                'document_number': parent.document_number,
                'title': parent.title,
                'level': parent.level.value
            }

        # Get children recursively
        hierarchy['children'] = self._get_children_recursive(document_id, max_depth, 0)

        return hierarchy

    def _get_children_recursive(
        self,
        parent_id: int,
        max_depth: int,
        current_depth: int
    ) -> List[dict]:
        """Recursively get children documents"""
        if current_depth >= max_depth:
            return []

        children = self.db.query(Document).filter(
            Document.parent_document_id == parent_id,
            Document.is_deleted == False
        ).all()

        result = []
        for child in children:
            child_data = {
                'id': child.id,
                'document_number': child.document_number,
                'title': child.title,
                'level': child.level.value,
                'status': child.status.value,
                'children': self._get_children_recursive(child.id, max_depth, current_depth + 1)
            }
            result.append(child_data)

        return result

    def get_traceability_matrix(
        self,
        document_id: int,
        depth: int = 2
    ) -> dict:
        """
        Generate traceability matrix showing all relationships

        Args:
            document_id: Root document ID
            depth: How many levels deep to trace

        Returns:
            Traceability matrix
        """
        visited = set()
        matrix = {
            'root': None,
            'upstream': [],  # Documents that this depends on
            'downstream': [],  # Documents that depend on this
            'related': []  # Related documents
        }

        # Get root document
        root = self._get_document(document_id)
        matrix['root'] = {
            'id': root.id,
            'document_number': root.document_number,
            'title': root.title,
            'level': root.level.value
        }

        # Trace upstream (dependencies)
        self._trace_upstream(document_id, depth, 0, visited, matrix['upstream'])

        # Reset visited for downstream
        visited = set()

        # Trace downstream (dependents)
        self._trace_downstream(document_id, depth, 0, visited, matrix['downstream'])

        # Get related documents
        related_links = self.db.query(DocumentLink).filter(
            ((DocumentLink.source_document_id == document_id) |
             (DocumentLink.target_document_id == document_id)) &
            (DocumentLink.link_type == 'related')
        ).all()

        for link in related_links:
            other_id = link.target_document_id if link.source_document_id == document_id else link.source_document_id
            if other_id not in visited:
                other_doc = self._get_document(other_id)
                matrix['related'].append({
                    'id': other_doc.id,
                    'document_number': other_doc.document_number,
                    'title': other_doc.title,
                    'level': other_doc.level.value
                })

        return matrix

    def _trace_upstream(
        self,
        document_id: int,
        max_depth: int,
        current_depth: int,
        visited: set,
        result: list
    ):
        """Trace upstream dependencies"""
        if current_depth >= max_depth or document_id in visited:
            return

        visited.add(document_id)

        # Get documents this one references/implements
        links = self.db.query(DocumentLink).filter(
            DocumentLink.source_document_id == document_id,
            DocumentLink.link_type.in_(['reference', 'implements', 'parent-child'])
        ).all()

        for link in links:
            target = self._get_document(link.target_document_id)
            result.append({
                'id': target.id,
                'document_number': target.document_number,
                'title': target.title,
                'level': target.level.value,
                'link_type': link.link_type,
                'depth': current_depth + 1
            })
            self._trace_upstream(link.target_document_id, max_depth, current_depth + 1, visited, result)

    def _trace_downstream(
        self,
        document_id: int,
        max_depth: int,
        current_depth: int,
        visited: set,
        result: list
    ):
        """Trace downstream dependents"""
        if current_depth >= max_depth or document_id in visited:
            return

        visited.add(document_id)

        # Get documents that reference/implement this one
        links = self.db.query(DocumentLink).filter(
            DocumentLink.target_document_id == document_id,
            DocumentLink.link_type.in_(['reference', 'implements', 'parent-child'])
        ).all()

        for link in links:
            source = self._get_document(link.source_document_id)
            result.append({
                'id': source.id,
                'document_number': source.document_number,
                'title': source.title,
                'level': source.level.value,
                'link_type': link.link_type,
                'depth': current_depth + 1
            })
            self._trace_downstream(link.source_document_id, max_depth, current_depth + 1, visited, result)

    def bulk_link_documents(
        self,
        source_document_id: int,
        target_document_ids: List[int],
        link_type: str,
        user_id: Optional[int] = None
    ) -> dict:
        """Bulk create links from one document to multiple documents"""
        created = 0
        errors = []

        for target_id in target_document_ids:
            try:
                self.create_link(
                    source_document_id=source_document_id,
                    target_document_id=target_id,
                    link_type=link_type,
                    user_id=user_id
                )
                created += 1
            except Exception as e:
                errors.append({
                    'target_id': target_id,
                    'error': str(e)
                })

        return {
            'status': 'success' if created > 0 else 'error',
            'created': created,
            'errors': errors,
            'total': len(target_document_ids)
        }

    def find_related_documents(
        self,
        document_id: int,
        by_level: Optional[str] = None,
        by_category: Optional[str] = None,
        by_standard: Optional[str] = None
    ) -> List[dict]:
        """
        Find potentially related documents based on metadata

        Args:
            document_id: Document ID
            by_level: Filter by document level
            by_category: Filter by category
            by_standard: Filter by standard

        Returns:
            List of potentially related documents
        """
        document = self._get_document(document_id)

        # Build query
        query = self.db.query(Document).filter(
            Document.id != document_id,
            Document.is_deleted == False
        )

        if by_level:
            query = query.filter(Document.level == by_level)
        elif document.level:
            # Same level by default
            query = query.filter(Document.level == document.level)

        if by_category:
            query = query.filter(Document.category == by_category)
        elif document.category:
            # Same category
            query = query.filter(Document.category == document.category)

        if by_standard:
            query = query.filter(Document.standard == by_standard)
        elif document.standard:
            # Same standard
            query = query.filter(Document.standard == document.standard)

        related = query.limit(20).all()

        return [{
            'id': doc.id,
            'document_number': doc.document_number,
            'title': doc.title,
            'level': doc.level.value,
            'category': doc.category,
            'standard': doc.standard.value if doc.standard else None,
            'similarity_score': self._calculate_similarity(document, doc)
        } for doc in related]

    def _calculate_similarity(self, doc1: Document, doc2: Document) -> float:
        """Calculate similarity score between two documents"""
        score = 0.0

        # Same level: +0.3
        if doc1.level == doc2.level:
            score += 0.3

        # Same category: +0.3
        if doc1.category and doc2.category and doc1.category == doc2.category:
            score += 0.3

        # Same standard: +0.2
        if doc1.standard and doc2.standard and doc1.standard == doc2.standard:
            score += 0.2

        # Similar tags: +0.2
        if doc1.tags and doc2.tags:
            tags1 = set(doc1.tags)
            tags2 = set(doc2.tags)
            if tags1 & tags2:  # Intersection
                score += 0.2

        return round(score, 2)

    def _get_reverse_link_type(self, link_type: str) -> str:
        """Get reverse link type for bidirectional links"""
        reverse_map = {
            'parent-child': 'child-parent',
            'child-parent': 'parent-child',
            'supersedes': 'superseded-by',
            'superseded-by': 'supersedes',
            'implements': 'implemented-by',
            'implemented-by': 'implements',
            'reference': 'referenced-by',
            'referenced-by': 'reference',
            'related': 'related'
        }
        return reverse_map.get(link_type, 'related')

    def _get_document(self, document_id: int) -> Document:
        """Get document or raise error"""
        document = self.db.query(Document).filter(
            Document.id == document_id,
            Document.is_deleted == False
        ).first()

        if not document:
            raise ValueError(f"Document not found: {document_id}")

        return document

    def _create_audit_log(
        self,
        document_id: int,
        user_id: int,
        action: str,
        notes: Optional[str] = None
    ):
        """Create audit log entry"""
        audit = DocumentAuditLog(
            document_id=document_id,
            user_id=user_id,
            action=action,
            notes=notes
        )
        self.db.add(audit)
