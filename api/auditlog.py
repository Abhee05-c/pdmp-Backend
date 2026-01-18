from sqlalchemy.orm import Session
from api.dbmodels import AuditLog

def auditLogs(db:Session,user_id:int,action:str,endpoint:str):
    log=AuditLog(
        user_id=user_id,
        action=action,
        endpoint=endpoint   
    )

    db.add(log)
    db.commit()
