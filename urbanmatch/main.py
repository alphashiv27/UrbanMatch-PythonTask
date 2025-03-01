import re
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from urbanmatch.database import SessionLocal, engine, Base
import urbanmatch.models as models, urbanmatch.schemas as schemas

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Validate email
    validation_response = check_email_internally(db, user.email)
    if not validation_response.is_valid:
        if validation_response.error == schemas.InvalidEmailEnum.INVALID_EMAIL:
            raise HTTPException(status_code=400, detail="Invalid email")
        elif validation_response.error == schemas.InvalidEmailEnum.DUPLICATE_EMAIL:
            raise HTTPException(status_code=400, 
                                detail="Email already belongs to other user")
    
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user: schemas.UserUpdate, user_id: int, db: Session = Depends(get_db)):
    # Validate email
    validation_response = check_email_internally(db, user.email)
    if not validation_response.is_valid:
        if validation_response.error == schemas.InvalidEmailEnum.INVALID_EMAIL:
            raise HTTPException(status_code=400, detail="Invalid email")
        elif validation_response.user_id != user_id:
            raise HTTPException(status_code=400, 
                                detail="Email already belongs to other user")

    
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.dict().items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return db_user

@app.post("/match/{user_id}", response_model=list[schemas.User])
def match_user(user_id: int, interest: schemas.InterestFilter, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    matched_users = db.query(models.User).filter(models.User.id != user_id).all()
    matched_users = [matched_user for matched_user in matched_users if matched_user.city in interest.city 
                     and matched_user.gender in interest.gender 
                     and interest.age_range_start <= matched_user.age <= interest.age_range_end 
                     and any(interest in matched_user.interests for interest in user.interests)]
    return matched_users

@app.get("/validate_email/{email}", response_model=schemas.ValidateEmailResponse)
def validate_email(email: str, db: Session = Depends(get_db)):
    return check_email_internally(db, email)

def check_email_internally(db: Session, email: str):
    # Regex check
    if re.match(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$', email) is None:
        return schemas.InvalidEmailResponse()

    # Duplicate check
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is not None:
        return schemas.DuplicateEmailResponse(user_id=user.id)

    # Otherwise, it's valid and not taken
    return schemas.ValidateEmailResponse(is_valid=True)

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users/bulk", response_model=list[schemas.User])
def create_users_bulk(users: list[schemas.UserCreate], db: Session = Depends(get_db)):
    new_users = []

    for user_data in users:
        # Validate email
        validate_email_response = check_email_internally(db, user_data.email)
        if not validate_email_response.is_valid:
            if validate_email_response.error == schemas.InvalidEmailEnum.INVALID_EMAIL:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid email: {user_data.email}"
                )
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Duplicate email: {user_data.email}"
                )


        db_user = models.User(**user_data.dict())
        new_users.append(db_user)
    
    db.add_all(new_users)
    db.commit()
    
    for user in new_users:
        db.refresh(user)
        
    return new_users



