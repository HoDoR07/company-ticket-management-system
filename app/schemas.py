from pydantic import BaseModel,EmailStr,Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserCreate(BaseModel):
    name: str = Field(max_length=100)
    email: EmailStr
    password: str = Field(max_length=20,min_length=8)
    phone: Optional[str] = Field(None,max_length=10,min_length=10)

class UserResponse(BaseModel):
    id: int
    name: str
    email:EmailStr
    phone: Optional[str]
    role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token : str
    token_type : str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class TicketCreate(BaseModel):
    title: str
    description: str
    priority: str= "medium"

class TicketResponse(BaseModel):
    id : int
    title : str
    description : str
    priority : str
    status : str
    assigned_to : Optional[int]
    created_by : int
    created_at : datetime


class TicketStatusUpdate(BaseModel):
    status: str


class TicketAssign(BaseModel):
    technician_id: int



class TicketUpdate(BaseModel):
    title: str
    description: str



class PriorityUpdate(BaseModel):
    priority: str



class RoleUpdate(BaseModel):
    role: str




