from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, models, database, oath2, redis
import json

router = APIRouter()

redis_client = redis.redis_client





@router.post("/tickets", response_model=schemas.TicketResponse, status_code=status.HTTP_201_CREATED)
def create_tickets(ticket: schemas.TicketCreate, current_user=Depends(oath2.get_current_user), db: Session = Depends(database.get_db)):

    if ticket.priority not in ["modrate", "medium", "high"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please choose [modrate, medium, high]"
        )

    new_ticket = models.Ticket(
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority,
        created_by=current_user.id
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    key = f"tickets:user:{current_user.id}"
    redis_client.delete(key)

    return new_ticket





@router.get("/tickets")
def get_tickets(current_user=Depends(oath2.get_current_user), db=Depends(database.get_db)):

    cached_tickets = redis_client.get(f"tickets:user:{current_user.id}")

    if cached_tickets:
        return json.loads(cached_tickets)

    tickets = db.query(models.Ticket).filter(
        models.Ticket.created_by == current_user.id).all()

    if not tickets:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Tickets Not Found")
    tickets_data = []

    for ticket in tickets:
        tickets_data.append({
            "id": ticket.id,
            "title": ticket.title,
            "description": ticket.description,
            "priority": ticket.priority,
            "status": ticket.status,
            "assigned_to": ticket.assigned_to,
            "created_by": ticket.created_by,
            "created_at": ticket.created_at.isoformat()
        })

    key = f"tickets:user:{current_user.id}"
    value = json.dumps(tickets_data)

    redis_client.set(key, value, ex=120)
    
    return tickets_data



@router.put("/tickets/update/{ticket_id}")
def update_ticket(ticket_id: int, ticket_update: schemas.TicketUpdate, db: Session = Depends(database.get_db), current_user=Depends(oath2.get_current_user)):

    ticket = db.query(models.Ticket).filter(
        models.Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Ticket Not Found With id: {ticket_id}")

    if (ticket.created_by != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if ticket.status == "closed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Ticket already closed")

    ticket.title = ticket_update.title
    ticket.description = ticket_update.description

    db.commit()
    db.refresh(ticket)

    key = f"tickets:user:{current_user.id}"
    redis_client.delete(key)
    
    return ticket


@router.delete("/ticket/delete/{ticket_id}")
def delete_ticket(ticket_id: int, current_user=Depends(oath2.get_current_user), db: Session = Depends(database.get_db)):

    ticket = db.query(models.Ticket).filter(
        models.Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Ticket not found with id: {ticket_id}")

    if (ticket.created_by != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Forbidden")

    if ticket.status == "closed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Ticket already closed")    

    db.delete(ticket)
    db.commit()

    key = f"tickets:user:{current_user.id}"
    redis_client.delete(key)

    return ("Ticket Deleted Successfully")