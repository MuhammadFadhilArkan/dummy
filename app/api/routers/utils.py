from tempfile import TemporaryDirectory

def get_obj_from_s3(minioClient, bucket_name, obj_name, temp_name):
    minioClient.fget_object(bucket_name, obj_name, temp_name)

async def get_temp_dir():
    dir = TemporaryDirectory()
    try:
        yield dir.name
    finally:
        del dir