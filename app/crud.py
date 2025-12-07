from sqlalchemy.orm import Session
from . import models, schemas, security
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status


def _to_dict(pydantic_obj, **kwargs) -> dict:
    """
    Support both Pydantic v1 (.dict) and v2 (.model_dump).
    """
    if hasattr(pydantic_obj, "model_dump"):
        return pydantic_obj.model_dump(**kwargs)
    return pydantic_obj.dict(**kwargs)


# ---------- USER CRUD ----------

def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    hashed_pw = security.hash_password(user_in.password)
    db_user = models.User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hashed_pw,
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        # Unique constraint failed (username or email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists.",
        )
    return db_user


def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username == username).first()


# ---------- CALCULATION CRUD ----------

def create_calculation(db: Session, calc_in: schemas.CalculationCreate) -> models.Calculation:
    data = _to_dict(calc_in)
    db_calc = models.Calculation(**data)
    db.add(db_calc)
    db.commit()
    db.refresh(db_calc)
    return db_calc


def get_all_calculations(db: Session) -> list[models.Calculation]:
    return db.query(models.Calculation).all()


def get_calculation_by_id(db: Session, calc_id: int) -> models.Calculation | None:
    return db.query(models.Calculation).filter(models.Calculation.id == calc_id).first()


def update_calculation(
    db: Session,
    calc_id: int,
    calc_in: schemas.CalculationUpdate,
) -> models.Calculation | None:
    calc = get_calculation_by_id(db, calc_id)
    if not calc:
        return None

    # Only update provided fields (exclude_unset)
    update_data = _to_dict(calc_in, exclude_unset=True)
    for field, value in update_data.items():
        setattr(calc, field, value)

    db.commit()
    db.refresh(calc)
    return calc


def delete_calculation(db: Session, calc_id: int) -> bool:
    calc = get_calculation_by_id(db, calc_id)
    if not calc:
        return False

    db.delete(calc)
    db.commit()
    return True

