import pandas as pd

def upload_img_to_s3(minioClient, filename, outname):
    minioClient.fput_object("graph", outname, filename)

def get_csv_object(minioClient, name):
    try:
        response = minioClient.get_object("data", name)
        df = pd.read_csv(response)
    finally:
        response.close()
        response.release_conn()

        return df
