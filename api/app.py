from fastapi import FastAPI,UploadFile,File,HTTPException,Depends
from fastapi.security import OAuth2PasswordRequestForm
from io import StringIO
import pandas as pd
from src.predict import _predictRUL
from api.payloadSchemas import live_data
from api.database import Session_local
from api.authSchemas import SignupRequest,LoginRequest,TokenResponse,CreateOrgUserRequest
from sqlalchemy.orm import Session
from api import dbmodels 
from api.dbmodels import User,AuditLog,Organisation
from api.authJWT import hash_password,verify_hash,create_access_token
from api.database import engine
from api.dependencies import current_user
from api.auditlog import auditLogs
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI(title="RUL Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    allow_methods=["*"]
)

dbmodels.Base.metadata.create_all(bind=engine)

def get_db():
    db=Session_local()
    try:
        yield db
    finally:
        db.close()
    

@app.get("/health")
def health():
    return {"status":"API is healthy"}


@app.post("/auth/signup",response_model=TokenResponse)
def signup(req:SignupRequest,db: Session=Depends(get_db)):

    org=dbmodels.Organisation(
        org_name=req.org_name,
        email=req.org_email)
    
    db.add(org)
    db.commit()
    db.refresh(org)

    user= dbmodels.User(
        org_id=org.org_id,
        name=req.username,
        password_hash=hash_password(req.password),
        org_admin=True,
        role="USER"
    )

    db.add(user)
    db.commit()

    token=create_access_token({
        "user_id":user.user_id,
        "org_id":org.org_id,
        "role":user.role,
        "user_name":user.name,
    })

    return {"access_token": token}

@app.post("/auth/login",response_model=TokenResponse)
def login(form_data:OAuth2PasswordRequestForm=Depends(),
          db: Session=Depends(get_db)):

    user=db.query(dbmodels.User).filter_by(name=form_data.username).first()

    if not user or not verify_hash(form_data.password,user.password_hash):
        raise HTTPException(status_code=401,detail="Invalid UserName or Password")
    
    token=create_access_token({
        "user_id":user.user_id,
        "org_id":user.org_id,
        "role":user.role,
        "is_org_admin":user.org_admin,
        "user_name":user.name
    })

    return {"access_token": token,"token_type":"bearer"}

@app.post("/org/users")
def create_org_user(
    req: CreateOrgUserRequest,
    user=Depends(current_user),
    db: Session = Depends(get_db)
):
    # ---- Must be org admin ----
    if not user.get("is_org_admin"):
        raise HTTPException(status_code=403, detail="Only org admin can add users")

    new_user = dbmodels.User(
        org_id=user["org_id"],
        name=req.username,
        password_hash=hash_password(req.password),
        role="USER",
        org_admin=False
    )

    db.add(new_user)
    db.commit()

    auditLogs(
        db=db,
        user_id=user["user_id"],
        action="CREATE_ORG_USER",
        endpoint="/org/users"
    )

    return {
        "message": "User created successfully",
        "username": req.username
    }

@app.get("/org/users")
def list_org_users(
    user=Depends(current_user),
    db: Session = Depends(get_db)
):
    if not user.get("is_org_admin"):
        raise HTTPException(status_code=403, detail="Only org admin can view users")

    users = (
        db.query(dbmodels.User)
        .filter(
            dbmodels.User.org_id == user["org_id"],
            dbmodels.User.is_active == True
        )
        .all()
    )

    return [
        {
            "user_id": u.user_id,
            "username": u.name,
            "role": u.role,
            "is_org_admin": u.org_admin,
            "is_active": u.is_active,
        }
        for u in users
    ]

@app.delete("/org/users/{user_id}")
def delete_org_user(
    user_id: int,
    user=Depends(current_user),
    db: Session = Depends(get_db)
):
    if not user.get("is_org_admin"):
        raise HTTPException(status_code=403, detail="Only org admin can delete users")

    if user_id == user["user_id"]:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")

    target_user = (
        db.query(dbmodels.User)
        .filter(
            dbmodels.User.user_id == user_id,
            dbmodels.User.org_id == user["org_id"]
        )
        .first()
    )

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if target_user.org_admin:
        raise HTTPException(status_code=403, detail="Cannot delete org admin")

    target_user.is_active = False
    db.commit()

    auditLogs(
        db=db,
        user_id=user["user_id"],
        action="DELETE_ORG_USER",
        endpoint=f"/org/users/{user_id}"
    )

    return {"status": "user deleted"}


@app.get("/admin/organizations")
def list_organizations(user=Depends(current_user),db: Session=Depends(get_db)):

    if user["role"]!="ADMIN":
        raise HTTPException(status_code=403,detail="Forbidden")
    
    list_orgsAll=db.query(dbmodels.Organisation).all()
    return list_orgsAll


@app.post("/admin/organizations/{org_id}/disable")
def organizations_disable(org_id:int, user=Depends(current_user),db:Session=Depends(get_db)):

    if user["role"]!="ADMIN":
        raise HTTPException(status_code=403,detail="Forbidden")
    
    org = db.query(dbmodels.Organisation).get(org_id)
    if not org:
        raise HTTPException(404, "Organisation not found")

    org.is_active = False
    db.commit()

    return {"status": "organization disabled"}


@app.post("/admin/organizations/{org_id}/enable")
def organizations_enable(org_id:int, user=Depends(current_user),db:Session=Depends(get_db)):

    if user["role"]!="ADMIN":
        raise HTTPException(status_code=403,detail="Forbidden")
    
    org = db.query(dbmodels.Organisation).get(org_id)
    if not org:
        raise HTTPException(404, "Organisation not found")

    org.is_active = True
    db.commit()

    return {"status": "organization enabled"}

@app.get("/admin/organizations/{org_id}/users")
def listUsers(org_id:int, user=Depends(current_user),db:Session=Depends(get_db)):

    if user["role"]!="ADMIN":
        raise HTTPException(status_code=403,detail="Forbidden")
    
    users = db.query(dbmodels.User).filter_by(org_id=org_id).all()
    return users


@app.post("/admin/users/{user_id}/disable")
def user_disable(user_id:int, user=Depends(current_user),db:Session=Depends(get_db)):

    if user["role"]!="ADMIN":
        raise HTTPException(status_code=403,detail="Forbidden")
    
    user_ = db.query(dbmodels.User).get(user_id)
    if not user_:
        raise HTTPException(404, "User not found")

    user_.is_active = False
    db.commit()

    return {"status": "user disabled"}
    

@app.post("/admin/users/{user_id}/enable")
def user_enable(user_id:int, user=Depends(current_user),db:Session=Depends(get_db)):

    if user["role"]!="ADMIN":
        raise HTTPException(status_code=403,detail="Forbidden")
    
    user_ = db.query(dbmodels.User).get(user_id)
    if not user_:
        raise HTTPException(404, "User not found")

    user_.is_active = True
    db.commit()

    return {"status": "user enabled"}


@app.get("/admin/auditlogs")
def get_auditLogs(user=Depends(current_user),db:Session=Depends(get_db)):

    if user["role"]!="ADMIN":
        raise HTTPException(status_code=403,detail="Forbidden")
    
    return db.query(dbmodels.AuditLog).order_by(
        dbmodels.AuditLog.timestamp.desc()).limit(100).all()


@app.post("/predict/csvUpload")
async def csv_prediction(file:UploadFile=File(...,description="Upload the engine history formatted as CSV"),
                         user=Depends(current_user),db:Session=Depends(get_db)):
    
    if user["role"]!="USER":
        raise HTTPException(status_code=403,detail="Forbidden")
    
    try:
        content=await file.read()
        df=pd.read_csv(StringIO(content.decode("utf-8")))
    except Exception:
        raise HTTPException(status_code=400,detail="Upload the engine history in valid CSV format")
    
    try:
        pred_result=_predictRUL(df)
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))
    

    auditLogs(
        db=db,
        user_id=user["user_id"],
        action="PREDICT_RUL_CSV",
        endpoint="/predict/csvUpload"
    )
    
    return pred_result


@app.post("/predict/liveData")
async def live_prediction(payload:live_data, user=Depends(current_user),db:Session=Depends(get_db)):

    if user["role"]!="USER":
        raise HTTPException(status_code=403,detail="Forbidden")
    
    try:
        df=pd.DataFrame([row.model_dump() for row in payload.sensor_data])
    except Exception as e:
        raise HTTPException(status_code=400,detail="Invalid data format")
    
    try:
        pred_result=_predictRUL(df)
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))
    

    auditLogs(
        db=db,
        user_id=user["user_id"],
        action="PREDICT_RUL_CSV",
        endpoint="/predict/liveData"
    )
    
    return pred_result

@app.get("/dashboard/org-summary")
def org_summary(
    user=Depends(current_user),
    db: Session = Depends(get_db)
):
    org=db.query(Organisation).filter_by(org_id=user["org_id"]).first()
    org_id = user["org_id"]

    total_users = db.query(User).filter_by(org_id=org_id).count()
    org_admins = db.query(User).filter_by(org_id=org_id, org_admin=True).count()
    normal_users = total_users - org_admins

    total_predictions = db.query(AuditLog).filter(
        AuditLog.user_id.in_(
            db.query(User.user_id).filter_by(org_id=org_id)
        ),
        AuditLog.action.like("PREDICT%")
    ).count()

    return {
        "organization_name": org.org_name,
        "total_users": total_users,
        "org_admins": org_admins,
        "normal_users": normal_users,
        "total_predictions": total_predictions
    }