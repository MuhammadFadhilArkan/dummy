from .scm import do_create_model, do_get_data,do_assign_cm, do_save_graph_plot, do_fit_model,do_cf_analysis

class CFA():
    def __init__(self):
        self.models = {}
        self.models_info = {}

    def get_model_list(self):
        return list(self.models.keys())
    
    def get_model_info(self, model_name):
        return self.models_info[model_name]
    
    def delete_model(self, model_name):
        try:
            del self.models[model_name]
            del self.models_info[model_name]
        except:
            pass

    def create_model(self, model_name, graph_conf):
        self.models[model_name] = do_create_model(graph_conf)
        self.models_info[model_name] = {"fitted": False}
    
    def train_model(self, model_name, minioClient, data_name):
        data = do_get_data(minioClient, data_name)
        self.models[model_name] = do_assign_cm(self.models[model_name], data)
        self.models[model_name] = do_fit_model(self.models[model_name], data)
        self.models_info[model_name] = {"fitted": True,
                                        "nodes": data.columns.tolist() 
                                        }

    def cf_analysis(self, model_name, observed_data, intervention):
        return do_cf_analysis(self.models[model_name], observed_data, intervention, self.models_info[model_name]).to_dict('list')
    
    def save_graph_plot(self, model_name, minioClient, filename):
        causal_model_graph = self.models[model_name].graph
        do_save_graph_plot(causal_model_graph, minioClient, filename)