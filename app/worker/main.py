from celery import Celery
from minio import Minio
import time
import os
from app.modules.main import CFA

# Wait for rabbitmq to be started
time.sleep(15)

CELERY_BROKER_ADDRESS = str(os.environ['CELERY_BROKER_ADDRESS'])
CELERY_BACKEND_ADDRESS = str(os.environ['CELERY_BACKEND_ADDRESS'])
MINIO_ADDRESS = str(os.environ['MINIO_ADDRESS'])
AWS_ACCESS_KEY_ID = str(os.environ['AWS_ACCESS_KEY_ID'])
AWS_SECRET_ACCESS_KEY = str(os.environ['AWS_SECRET_ACCESS_KEY'])

celery = Celery('main',
                broker=CELERY_BROKER_ADDRESS,
                backend=CELERY_BACKEND_ADDRESS
                )

celery.conf.task_routes = {'cfa.*': {'queue': 'cfa'}}

cfa = CFA()
minioClient = Minio(MINIO_ADDRESS,
                        access_key=AWS_ACCESS_KEY_ID,
                        secret_key=AWS_SECRET_ACCESS_KEY,
                        secure=False
                        )

@celery.task(name='cfa.create_model')  # Named task
def create_model(**params):
    cfa.create_model(params.get("model_name"), params.get("graph_conf"))
    return {"info": "Success"}

@celery.task(name='cfa.delete_model')  # Named task
def delete_model(**params):
    cfa.delete_model(params.get("model_name"))
    return {"info": "Success"}

@celery.task(name='cfa.train_model')  # Named task
def train_model(**params):
    cfa.train_model(params.get("model_name"), minioClient, params.get("data_name"))
    return {"info": "Success"}

@celery.task(name='cfa.infer')  # Named task
def infer(**params):
    return cfa.cf_analysis(params.get("model_name"), params.get("observed_data"), params.get("intervention"))

@celery.task(name='cfa.save_graph_plot')  # Named task
def save_graph_plot(**params):
    cfa.save_graph_plot(params.get("model_name"), minioClient, params.get("filename"))
    return {"info": "Success"}

@celery.task(name='cfa.get_model_list')  # Named task
def get_model_list():
    return cfa.get_model_list()

@celery.task(name='cfa.get_model_info')  # Named task
def get_model_info(**params):
    return cfa.get_model_info(params.get("model_name"))