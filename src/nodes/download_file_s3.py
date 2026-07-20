from ..client_s3 import get_s3_instance
S3_INSTANCE = get_s3_instance()


class DownloadFileS3:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required":{
                "s3_path": ("STRING", {"default": "input/example.png"}),
                "local_path": ("STRING", {"default": "input/example.png"}),
            }
        }
    
    CATEGORY = "ComfyS3"
    INPUT_NODE = True
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("local_path",)
    FUNCTION = "download_file_s3"
    
    def download_file_s3(self, s3_path, local_path):
        result_path = S3_INSTANCE.download_file(s3_path=s3_path, local_path=local_path)

        if result_path is None:
            raise FileNotFoundError(
                f"[ComfyS3] Could not download file from S3: {s3_path} — "
                f"the file does not exist or is not accessible. Check the S3 path and bucket."
            )

        print(f"Downloaded file from S3 to {result_path}")
        return (result_path,)