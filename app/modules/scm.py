import networkx as nx
import dowhy.gcm as gcm
import pandas as pd
from tempfile import TemporaryDirectory
import os
from .utils import upload_img_to_s3, get_csv_object

def do_create_model(graph_conf):
    return gcm.InvertibleStructuralCausalModel(nx.DiGraph(graph_conf))

def do_get_data(minioClient, data_name):
    return get_csv_object(minioClient, data_name)

def do_assign_cm(causal_model, data):
    gcm.auto.assign_causal_mechanisms(causal_model, data,
                                      quality=gcm.auto.AssignmentQuality.BETTER
                                      )
    return causal_model

def do_save_graph_plot(causal_model_graph, minioClient, filename):
    with TemporaryDirectory() as tempdir:
        outname = f"{filename}.png"
        filename = os.path.join(tempdir, f'{filename}.png')
        gcm.util.plot(causal_model_graph, filename=filename)
        upload_img_to_s3(minioClient, filename, outname)

def do_fit_model(causal_model, data):
    gcm.fit(causal_model, data)
    return causal_model

def mfunc(n):
    return lambda x : n

def do_cf_analysis(causal_model, observed_data, intervention, model_info):
    intervention = {k: mfunc(v) for k,v in intervention.items()}
    if len(observed_data)>0:
        observed_data = pd.DataFrame(observed_data, index=[0])
        return gcm.counterfactual_samples(causal_model,intervention,observed_data = observed_data)
    else:
        noise_data = {k:0 for k in model_info['nodes']}
        return gcm.counterfactual_samples(causal_model,intervention,
                                          noise_data=pd.DataFrame(noise_data, index=[0]))
