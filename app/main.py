from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas, crud, security
from .database import engine, Base, get_db

# Create tables (for simple setups; in real world you'd use Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI()


# ---------- User Endpoints ----------

@app.post("/users/", response_model=schemas.UserRead, status_code=201)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Old endpoint kept for backward compatibility with Module 11 tests"""
    user = crud.create_user(db, user_in)
    return user


@app.post("/users/register", response_model=schemas.UserRead, status_code=201)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user (Module 12 spec)"""
    user = crud.create_user(db, user_in)
    return user


@app.post("/users/login", response_model=schemas.UserRead)
def login_user(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return user info"""
    user = crud.get_user_by_username(db, user_in.username)
    if not user or not security.verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return user


@app.get("/users/{user_id}", response_model=schemas.UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ---------- Calculation BREAD Endpoints ----------

@app.post("/calculations/", response_model=schemas.CalculationRead, status_code=201)
def create_calculation(calc_in: schemas.CalculationCreate, db: Session = Depends(get_db)):
    """Create (B) a new calculation"""
    calculation = crud.create_calculation(db, calc_in)
    return calculation


@app.get("/calculations/", response_model=list[schemas.CalculationRead])
def read_all_calculations(db: Session = Depends(get_db)):
    """Read (R) all calculations"""
    calculations = crud.get_all_calculations(db)
    return calculations


@app.get("/calculations/{calc_id}", response_model=schemas.CalculationRead)
def read_calculation(calc_id: int, db: Session = Depends(get_db)):
    """Read (R) a specific calculation by ID"""
    calculation = crud.get_calculation_by_id(db, calc_id)
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calculation


@app.put("/calculations/{calc_id}", response_model=schemas.CalculationRead)
def update_calculation(
    calc_id: int,
    calc_in: schemas.CalculationUpdate,
    db: Session = Depends(get_db),
):
    """Update (E) an existing calculation"""
    calculation = crud.update_calculation(db, calc_id, calc_in)
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calculation


@app.delete("/calculations/{calc_id}", status_code=204)
def delete_calculation(calc_id: int, db: Session = Depends(get_db)):
    """Delete (A) a calculation"""
    success = crud.delete_calculation(db, calc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return None

