"""
Document endpoints for managing generated PDFs.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.document import Document
from app.schemas.document import Document as DocumentSchema
from app.services.pdf_service import pdf_service
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("/", response_model=List[DocumentSchema])
def list_documents(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all documents with optional filtering.

    Args:
        patient_id: Filter by patient ID
        document_type: Filter by document type
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of documents
    """
    query = db.query(Document)

    if patient_id:
        query = query.filter(Document.patient_id == patient_id)

    if document_type:
        query = query.filter(Document.document_type == document_type)

    documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()

    return documents


@router.get("/{document_id}", response_model=DocumentSchema)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get document metadata by ID.

    Args:
        document_id: Document ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Document metadata

    Raises:
        HTTPException: If document not found
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )

    return document


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Download a document PDF file.

    Args:
        document_id: Document ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        PDF file as response

    Raises:
        HTTPException: If document not found or file doesn't exist
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )

    # Load PDF from storage
    pdf_bytes = pdf_service.get_document_bytes(document)

    if pdf_bytes is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found in storage"
        )

    # Verify integrity
    if not pdf_service.verify_document_integrity(document):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document integrity verification failed"
        )

    # Audit log
    audit_service.log_document_download(
        db,
        current_user,
        document.id,
        document.patient_id
    )

    # Return PDF
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={document.filename}"
        }
    )


@router.get("/{document_id}/preview")
def preview_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Preview a document PDF inline in browser.

    Args:
        document_id: Document ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        PDF file for inline display

    Raises:
        HTTPException: If document not found
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )

    # Load PDF from storage
    pdf_bytes = pdf_service.get_document_bytes(document)

    if pdf_bytes is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found in storage"
        )

    # Verify integrity
    if not pdf_service.verify_document_integrity(document):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document integrity verification failed"
        )

    # Return PDF for inline display
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename={document.filename}"
        }
    )


@router.post("/{document_id}/reprint")
def reprint_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Log a document reprint action and return the PDF.

    Args:
        document_id: Document ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        PDF file for printing

    Raises:
        HTTPException: If document not found
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )

    # Load PDF from storage
    pdf_bytes = pdf_service.get_document_bytes(document)

    if pdf_bytes is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found in storage"
        )

    # Verify integrity
    if not pdf_service.verify_document_integrity(document):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document integrity verification failed"
        )

    # Audit log for reprint
    audit_service.log_document_print(
        db,
        current_user,
        document.id,
        document.patient_id
    )

    # Return PDF
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename={document.filename}"
        }
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a document record.
    Note: This does not delete the physical file, only the database record.

    Args:
        document_id: Document ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If document not found
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )

    # Audit log
    audit_service.log(
        db,
        current_user,
        entity="document",
        action="delete",
        entity_id=document.id,
        description=f"Deleted document {document.filename}",
        metadata={"filename": document.filename, "patient_id": document.patient_id}
    )

    db.delete(document)
    db.commit()

    return None
