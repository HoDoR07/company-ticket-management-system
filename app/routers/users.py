from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, models, database, utils, oath2


router = APIRouter()


@router.post("/users/new", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already used")

    new_user = models.User(
        name=user.name,
        email=user.email,
        password=utils.hash_password(user.password),
        phone=user.phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "phone": new_user.phone,
        "role": new_user.role
    }


@router.post("/login", response_model=schemas.LoginResponse)
def User_Login(user: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user_email = db.query(models.User).filter(
        models.User.email == user.email).first()
    if not user_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Credentials")

    if not utils.verify_password(user.password, user_email.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Credentials")

    token = oath2.create_access_token({
        "user_id": user_email.id,
        "role": user_email.role
    })
    return {
        "access_token": token,
        "token_type": "bearer"
    }


# @app.get("/users", response_model=list[schemas.UserResponse])
# def get_users(db: Session = Depends(database.get_db)):
#     users = db.query(models.User).all()
#     result = []

#     for user in users:
#         result.append({
#             "id": user.id,
#             "name": user.name,
#             "email": user.email,
#             "phone": user.phone
#         })
#     return result


@router.get("/users/me", response_model=schemas.UserResponse)
def user_me(current_user=Depends(oath2.get_current_user)):

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "role": current_user.role
        
    }


@router.get("/users/{id}", response_model=schemas.UserResponse)
def get_user(id: int,current_user = Depends(oath2.get_current_user), db: Session = Depends(database.get_db)):

    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} dose not exist")

    if user.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Forbidden")
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role
    }






@router.put("/users/{id}", response_model=schemas.UserResponse)
def update_user(id: int, user: schemas.UserUpdate,current_user = Depends(oath2.get_current_user), db: Session = Depends(database.get_db)):

    user_get = db.query(models.User).filter(models.User.id == id).first()
    
    if not user_get:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} Not Found")
    if user_get.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Forbidden")
    if user.email is not None:
        exesting_email = db.query(models.User).filter(models.User.email == user.email, models.User.id != current_user.id).first()

        if exesting_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Email already exist") 

    
    if user.name is not None:
        user_get.name = user.name
    if user.email is not None:
        user_get.email = user.email
    if user.phone is not None:
        user_get.phone = user.phone

    db.commit()
    db.refresh(user_get)
    return {
        "id": user_get.id,
        "name": user_get.name,
        "email": user_get.email,
        "phone": user_get.phone,
        "role": user_get.role
    }


# @app.delete("/users/{id}")
# def delete_user(id: int,current_user= Depends(oath2.get_current_user), db: Session = Depends(database.get_db)):
#     user = db.query(models.User).filter(models.User.id == id).first()

#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"User with id: {id} Not Found")
#     if user.id != current_user.id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
#                             detail="Forbidden")    
#     db.delete(user)
#     db.commit()

#     return {
#         "message": f"user deleted Successfully | user id: {id}"
#     }
