from sqlalchemy import Column,Integer,String,Boolean,DateTime,func,ForeignKey
from sqlalchemy.orm import DeclarativeBase
from .database import engine


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id = Column(Integer,nullable=False,primary_key=True)
    name = Column(String,nullable=False)
    email = Column(String,nullable=False,unique=True)
    password = Column(String,nullable=False)
    role = Column(String,nullable=False,default="employee")
    phone = Column(String)
    created_at = Column(DateTime,default=func.now())



class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer,nullable=False,primary_key=True)
    title = Column(String,nullable=False)
    description = Column(String,nullable=False)
    priority = Column(String,default="medium")
    status = Column(String,nullable=False,default="open")
    created_by = Column(Integer,ForeignKey(User.id))
    assigned_to = Column(Integer,ForeignKey(User.id))
    created_at = Column(DateTime,default=func.now())




    
# Base.metadata.create_all(engine)

