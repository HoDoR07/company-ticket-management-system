from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_


from app import schemas, models, database, oath2, redis


router = APIRouter()

redis_client = redis.redis_client



@router.get("/admin/tickets")
def admin_tickets(ticket_status:str | None = None, ticket_priority:str |None = None, current_user=Depends(oath2.admin_only), db: Session = Depends(database.get_db)):

    if ticket_status and ticket_status not in ["open", "in progress", "resolved", "closed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please choose [open, in progress, resolved, closed]"
        )

    if ticket_priority and ticket_priority not in ["modrate", "medium", "high"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Please choose [modrate, medium, high]")

    
    query = db.query(models.Ticket)

    if ticket_status:
        query = query.filter(models.Ticket.status == ticket_status)

    if ticket_priority:
        query = query.filter(models.Ticket.priority == ticket_priority)

    tickets = query.all()
    return tickets



@router.get("/admin/alluser",response_model=list[schemas.UserResponse])
def admin_alluser(current_user=Depends(oath2.admin_only), db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    return users




@router.put("/admin/users/{user_id}",response_model=schemas.UserResponse)
def update_role(user_id: int,
                upd_role: schemas.RoleUpdate,
                current_user=Depends(oath2.admin_only),
                db: Session = Depends(database.get_db)):
    
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No User with id: {user_id}")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Admin cannot modify their own role")
    
    if upd_role.role not in ["admin", "technician", "employee"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Wrong Input Please Enter the role admin, technician, employee ")

    user.role = upd_role.role
    db.commit()
    db.refresh(user)
    return user



@router.put("/admin/ticket/{ticket_id}/priority")
def update_ticket_priority(ticket_id: int,priority_update: schemas.PriorityUpdate,current_user=Depends(oath2.admin_only),db: Session = Depends(database.get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No ticket found with id: {ticket_id}")

    if priority_update.priority not in ["modrate", "medium", "high"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invali Input please sellect [modrate, medium, high]") 

    ticket.priority = priority_update.priority

    db.commit()
    db.refresh(ticket)
    key = f"tickets:user:{ticket.created_by}"
    redis_client.delete(key)
    return ticket



@router.patch("/admin/ticket/{ticket_id}/status")
def update_ticket_status(ticket_id: int, status_update: schemas.TicketStatusUpdate, current_user = Depends(oath2.admin_only), db: Session = Depends(database.get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No tickets found with id: {ticket_id}")

    if status_update.status not in ["open", "in progress", "resolved", "closed"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invali Input please sellect [open, in progress, resolved, closed] ")

    ticket.status = status_update.status

    db.commit()
    db.refresh(ticket)

    key = f"tickets:user:{ticket.created_by}"
    redis_client.delete(key)
    return ticket



@router.delete("/admin/user/{user_id}/delete")
def user_delete(user_id: int, current_user = Depends(oath2.admin_only), db:Session= Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User Dose not exist with id: {user_id}")
    
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Admin cannot delete their own account")
    
    tickets_and_assigned_ticket = db.query(models.Ticket).filter(or_(models.Ticket.created_by == user_id,models.Ticket.assigned_to == user_id)).all()

    if tickets_and_assigned_ticket:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"user with id: {user_id} have Tickets Unable to delete")


    db.delete(user)
    db.commit()

    return {"message": f"User with id: {user_id} deleted Successfully"}




@router.post("/ticket/{ticket_id}/assign")
def assign_ticket(ticket_id: int, assigned: schemas.TicketAssign, db: Session = Depends(database.get_db), current_user=Depends(oath2.admin_only)):

    ticket = db.query(models.Ticket).filter(
        models.Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No tickets Found with id: {ticket_id}")

    if ticket.status == "closed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Ticket with id: {ticket_id} is already closed")

    technician = db.query(models.User).filter(
        models.User.id == assigned.technician_id).first()

    if not technician:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No user found with id: {assigned.technician_id}")

    if not (technician.role == "technician"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Unauthorized Access")

    ticket.assigned_to = technician.id

    db.commit()
    db.refresh(ticket)

    key = f"tickets:user:{ticket.created_by}"
    redis_client.delete(key)

    return ticket





@router.delete("/admin/delete/{ticket_id}/ticket")
def admin_delete_ticket(ticket_id: int, current_user = Depends(oath2.admin_only),db:Session= Depends(database.get_db)):

    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Ticket not found with id: {ticket_id}")


    db.delete(ticket)
    db.commit()        

    return {"message": f"Ticket with id: {ticket_id} deleted Successfully"}




@router.get("/admin/dashboard")
def admin_dashboard(current_user = Depends(oath2.admin_only), db: Session = Depends(database.get_db)):
    total_users = db.query(models.User).count()

    total_tickets = db.query(models.Ticket).count()

    open_tickets = db.query(models.Ticket).filter(models.Ticket.status == "open").count()
    in_progress_tickets = db.query(models.Ticket).filter(models.Ticket.status == "in progress").count()
    resolved_tickets = db.query(models.Ticket).filter(models.Ticket.status == "resolved").count()
    closed_tickets = db.query(models.Ticket).filter(models.Ticket.status == "closed").count()

    return {
        "total_users": total_users,
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "in_progress_tickets": in_progress_tickets,
        "resolved_tickets": resolved_tickets,
        "closed_tickets": closed_tickets
    }

