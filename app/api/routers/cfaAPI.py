from fastapi import APIRouter, Depends
from fastapi.params import Body
from fastapi.responses import FileResponse
from celery import Celery
from minio import Minio
from minio.commonconfig import DISABLED, ENABLED, AndOperator, Filter
from minio.replicationconfig import (DeleteMarkerReplication, Destination,
                                     ReplicationConfig, Rule)
import logging
from .utils import get_obj_from_s3, get_temp_dir
import os
logger = logging.getLogger("gunicorn.error")

CELERY_BROKER_ADDRESS = str(os.environ['CELERY_BROKER_ADDRESS'])
CELERY_BACKEND_ADDRESS = str(os.environ['CELERY_BACKEND_ADDRESS'])
MINIO_ADDRESS = str(os.environ['MINIO_ADDRESS'])
AWS_ACCESS_KEY_ID = str(os.environ['AWS_ACCESS_KEY_ID'])
AWS_SECRET_ACCESS_KEY = str(os.environ['AWS_SECRET_ACCESS_KEY'])

router = APIRouter(
    prefix="/cfa",
    tags=['CounterFactual-Analytics']
)

celery = Celery(
    'main',
    broker=CELERY_BROKER_ADDRESS,
    backend=CELERY_BACKEND_ADDRESS,
)

celery.conf.task_routes = {'cfa.*': {'queue': 'cfa'}}

try:
    minioClient = Minio(MINIO_ADDRESS,
                        access_key=AWS_ACCESS_KEY_ID,
                        secret_key=AWS_SECRET_ACCESS_KEY,
                        secure=False
                        )
    minioClient.make_bucket("data")
    minioClient.make_bucket("graph")
except:
    pass

@router.post("/create_model")
async def create_model(params: dict = Body(...)):
    try:
        celery.send_task('cfa.create_model', kwargs=params)
        return {"info": "creating model..."}
    except Exception as e:
        return {"info": e}
    
@router.post("/delete_model")
async def delete_model(params: dict = Body(...)):
    try:
        celery.send_task('cfa.delete_model', kwargs=params)
        return {"info": "deleting model..."}
    except Exception as e:
        return {"info": e}
    
@router.post("/train_model")
async def train_model(params: dict = Body(...)):
    try:
        celery.send_task('cfa.train_model', kwargs=params)
        return {"info": "training model..."}
    except Exception as e:
        return {"info": e}

@router.post("/infer")
async def infer(params: dict = Body(...)):
    try:
        async_ = params.pop("async_")
        res = celery.send_task('cfa.infer', kwargs=params)
        if async_:
            return {"result": "calculating..."}
        return {"result": res.get()}
    except Exception as e:
        return {"info": e}
    
@router.post("/save_graph_plot")
async def save_graph_plot(params: dict = Body(...)):
    try:
        celery.send_task('cfa.save_graph_plot', kwargs=params)
        return {"info": "saving graph..."}
    except Exception as e:
        return {"info": e}
    
@router.get("/get_model_list")
async def get_model_list():
    try:
        res = celery.send_task('cfa.get_model_list')
        return {"result": res.get()}
    except Exception as e:
        return {"info": e}
    
@router.get("/get_model_info")
async def get_model_info(params: dict = Body(...)):
    try:
        res = celery.send_task('cfa.get_model_info', kwargs=params)
        return {"result": res.get()}
    except Exception as e:
        return {"info": e}

@router.get("/get_graph_plot/{graph_name}")
async def get_spesific_artifact(graph_name: str, tempdir=Depends(get_temp_dir)):
    try:
        get_obj_from_s3(minioClient, "graph", graph_name, os.path.join(tempdir, graph_name))
        return FileResponse(os.path.join(tempdir, graph_name))
    except:
        return {"error": "artifact not found"}


