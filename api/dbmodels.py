from sqlalchemy.orm import declarative_base,relationship
from sqlalchemy import Column,Boolean,ForeignKey,String,Integer,DateTime
from datetime import datetime,timezone

Base = declarative_base()

def utc_now():
    return datetime.now(timezone.utc)


class Organisation(Base):
    __tablename__="organizations"

    org_id=Column(Integer,primary_key=True)
    org_name=Column(String,unique=True,nullable=False)
    email=Column(String,unique=True,nullable=False)
    is_active=Column(Boolean,nullable=False,default=True)
    created_at=Column(DateTime(timezone=True),default=utc_now)
    users=relationship("User",back_populates="organization")

class User(Base):
    __tablename__="users"
    user_id=Column(Integer,primary_key=True,unique=True)
    name=Column(String,nullable=False,unique=True)
    org_id=Column(Integer,ForeignKey("organizations.org_id"))
    password_hash=Column(String,nullable=False,unique=True)
    role=Column(String,default="USER")
    is_active=Column(Boolean,default=True)
    org_admin=Column(Boolean,default=False)
    created_at=Column(DateTime(timezone=True),default=utc_now)
    organization=relationship(Organisation,back_populates="users")

class AuditLog(Base):
    __tablename__="audit_logs"
    id=Column(Integer,primary_key=True)
    user_id=Column(Integer)
    action=Column(String)
    endpoint = Column(String)
    timestamp = Column(DateTime(timezone=True),default=utc_now)



