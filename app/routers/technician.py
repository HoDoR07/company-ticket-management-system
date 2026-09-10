from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, models, database, oath2

router = APIRouter()



@router.get("/technician/tickets")
def Technician_Tickets(current_user=Depends(oath2.technician_only), db=Depends(database.get_db)):
    tickets = db.query(models.Ticket).filter(
        models.Ticket.assigned_to == current_user.id).all()
    if not tickets:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Tickets Not Found")

    return tickets




@router.patch("/technician/tickets/{ticket_id}")
def status_update(status_update: schemas.TicketStatusUpdate, ticket_id: int, current_user=Depends(oath2.technician_only),
                  db: Session = Depends(database.get_db)):
    ticket = db.query(models.Ticket).filter(
        models.Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Ticket Not Found with id: {ticket_id}")

    if ticket.status == "closed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Ticket already closed")

    if status_update.status not in [ "in progress", "resolved" ]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="please choose [in progress, resolved]")

    if not (ticket.assigned_to == current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Unauthorized Access")
    ticket.status = status_update.status
    db.commit()
    db.refresh(ticket)

    return ticket
