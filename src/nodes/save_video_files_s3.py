import os
import re

from ..client_s3 import get_s3_instance
S3_INSTANCE = get_s3_instance()


class SaveVideoFilesS3:
    def __init__(self):
        self.s3_output_dir = os.getenv("S3_OUTPUT_DIR")
        self.container_id = os.getenv("VAST_CONTAINERLABEL")
        self.prefix_append = ""

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "filename_prefix": ("STRING", {"default": "VideoFiles"}),
            "filenames": ("VHS_FILENAMES", )
            }}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("s3_video_paths",)
    FUNCTION = "save_video_files"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)
    CATEGORY = "ComfyS3"

    def save_video_files(self, filenames, filename_prefix="VideoFiles"):
        filename_prefix += self.prefix_append
        local_files = filenames[1]
        full_output_folder, _, _, _, filename_prefix = S3_INSTANCE.get_save_path(filename_prefix)
        s3_video_paths = list()

        # The prefix no longer appears in the key, so get_save_path's prefix-based counter
        # can't be used. Derive it from the trailing number of the existing keys instead.
        existing_files = S3_INSTANCE.get_files(full_output_folder) or []
        counters = [int(m.group(1)) for f in existing_files
                    if (m := re.search(r'_(\d+)\.[^.]+$', f))]
        counter = max(counters, default=0) + 1

        # Only include the container ID in the key when running in a Vast.ai container
        container_part = f"{self.container_id}_" if self.container_id else ""
        for path in local_files:
            # Keep the original basename so files sharing an extension don't overwrite
            # each other; the shared trailing counter keeps runs distinct.
            stem, ext = os.path.splitext(os.path.basename(path))
            file = f"{stem}_{container_part}{counter:05}{ext}"

            # Upload the local file to S3
            s3_path = os.path.join(full_output_folder, file)
            s3_path = s3_path.replace('\\', '/')

            file_path = S3_INSTANCE.upload_file(path, s3_path)
            if file_path is None:
                raise RuntimeError(f"Failed to upload {path} to S3 at {s3_path}")

            # Add the s3 path to the s3_image_paths list
            s3_video_paths.append(file_path)
        
        return (s3_video_paths,)
