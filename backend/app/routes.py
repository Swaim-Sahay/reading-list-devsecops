from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db

router = APIRouter(prefix="/api/books", tags=["books"])


def _get_or_404(db: Session, book_id: int) -> models.Book:
    book = db.get(models.Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.get("", response_model=List[schemas.BookOut])
def list_books(db: Session = Depends(get_db)):
    return db.query(models.Book).order_by(models.Book.id).all()


@router.post("", response_model=schemas.BookOut, status_code=status.HTTP_201_CREATED)
def create_book(payload: schemas.BookCreate, db: Session = Depends(get_db)):
    book = models.Book(**payload.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.get("/{book_id}", response_model=schemas.BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, book_id)


@router.put("/{book_id}", response_model=schemas.BookOut)
def update_book(book_id: int, payload: schemas.BookUpdate, db: Session = Depends(get_db)):
    book = _get_or_404(db, book_id)
    for key, value in payload.model_dump().items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db.delete(_get_or_404(db, book_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
