import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIRECTORY = BASE_DIR / "models"


model_=joblib.load(MODEL_DIRECTORY/"bestmodel(XGboost)_FD004.pkl")
scalerSensors_=joblib.load(MODEL_DIRECTORY/"Scalled Sensors by clusters.pkl")
featureList_=joblib.load(MODEL_DIRECTORY/"feature_list.pkl")
kmeans_=joblib.load(MODEL_DIRECTORY/"kmeans_operSettings.pkl")

Window=1
opCol=['op1','op2','op3']
sensorCol=['s3','s4','s9','s11','s12','s13','s14','s15','s20']
keepCols=['cycle']+['op1','op2','op3']+['s3','s4','s9','s11','s12','s13','s14','s15','s20']

def _validateInput(df:pd.DataFrame):
    leftout=set(keepCols)-set(df.columns)
    if len(leftout)>0:
        raise ValueError(f"Missing columns: {leftout}")
    if len(df)<Window:
        raise ValueError(f"At least {Window} cycles required, got len{df}")

def _assignCluster(df:pd.DataFrame) -> int:
    opColumns = df.reindex(columns=list(kmeans_.feature_names_in_)).iloc[-1:]
    return int(kmeans_.predict(opColumns)[0])

def _scaledSensors(df:pd.DataFrame,clusterId) -> (pd.DataFrame):
    df_scaled=df.copy()
    df_scaled[sensorCol]=scalerSensors_[clusterId].transform(df_scaled[sensorCol])
    return df_scaled

def _buildFeatures(df:pd.DataFrame) -> pd.DataFrame:
    g=df.sort_values('cycle').copy()
    g["clusterId"] = _assignCluster(g)
    for s in sensorCol:
        g[f"{s}_rmean"] = g[s].rolling(Window,min_periods=1).mean()
        g[f"{s}_rstd"]  =g[s].rolling(Window,min_periods=1).std().fillna(0)

    for s in sensorCol:
        g[f"{s}_lag1"]=g[s].shift(1).bfill()
        g[f"{s}_delta"]=g[s]-g[f"{s}_lag1"]

    return g.iloc[-1:]

def _predictRUL(enginehistory:pd.DataFrame)->dict:

    _validateInput(enginehistory)

    clusterNumber=_assignCluster(enginehistory)

    scaled=_scaledSensors(enginehistory,clusterNumber)

    features=_buildFeatures(scaled)


    X=features[featureList_]
    
    predicted_Rul=float(model_.predict(X)[0])

    return {
        "Predicted_RUL" : round(predicted_Rul,2),
        "Operating Cluster" : clusterNumber,
        "Current Cycle" : int(enginehistory['cycle'].iloc[-1])
    }

if __name__=="__main__":
    BASE_DIRECTORY=Path("..")/"data"/"beforeProcessing"
    sample=pd.read_csv(BASE_DIRECTORY/"test_FD004.txt",sep=r"\s+",header=None)
    sample.columns=['unit','cycle']+opCol+[f"s{i}" for i in range(1,22)]

    engine_df=sample[sample.unit==5].tail(10)

    pred=_predictRUL(engine_df)
    print(pred)