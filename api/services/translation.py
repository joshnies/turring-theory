import os
from os import path
from typing import Optional
from uuid import uuid4
import boto3
import shutil

from api.config import AWS_STORAGE_BUCKET_NAME
from cli import log
from theory.core import Theory
from ..config import DEBUG


class TranslationService:
    """Translation service."""

    @staticmethod
    def translate(theory: Theory, input_path: str, data):
        """
        Translate file or directory.

        :param theory: Theory instance.
        :param input_path: Path to file in Firebase Storage bucket.
        :param data: Request body data from "/translate" endpoint.
        :returns: Path to output file in Firebase Storage bucket.
        """

        job_id = str(uuid4())
        s3_input_path = f'inputs/{input_path}'
        log(f'Job started: {job_id}')

        # Create temp directories for downloaded and translated files
        temp_inp_dir = path.join('temp', 'inputs', job_id)
        os.makedirs(temp_inp_dir, exist_ok=True)

        temp_out_dir = path.join('temp', 'outputs', job_id)
        os.makedirs(temp_out_dir, exist_ok=True)

        is_file = '.' in input_path

        # Initialize S3 bucket
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(AWS_STORAGE_BUCKET_NAME)
        translated_file_paths = list()

        if is_file:
            new_path = TranslationService.__translate_file(
                theory=theory,
                temp_inp_dir=temp_inp_dir,
                temp_out_dir=temp_out_dir,
                bucket=bucket,
                s3_key=s3_input_path,
                data=data
            )

            if new_path is not None:
                translated_file_paths.append(new_path)
        else:
            objects = bucket.objects.filter(Prefix=s3_input_path)

            for o in objects:
                new_path = TranslationService.__translate_file(
                    theory=theory,
                    temp_inp_dir=temp_inp_dir,
                    temp_out_dir=temp_out_dir,
                    bucket=bucket,
                    s3_key=o.key,
                    data=data
                )

                if new_path is not None:
                    translated_file_paths.append(new_path)

        # Generate project files
        theory.create_project_files(temp_out_dir, translated_file_paths)

        # Zip contents
        zip_file_path = shutil.make_archive(temp_out_dir, 'zip', temp_out_dir)

        # Upload output zip to S3
        remote_out_path = f'outputs/' + path.basename(zip_file_path)
        s3.Bucket(AWS_STORAGE_BUCKET_NAME).upload_file(
            zip_file_path, remote_out_path)

        # Delete output file from local storage
        if not DEBUG:
            # TODO: Delete "temp_out_dir" and its contents
            os.remove(zip_file_path)

        log(f'Job completed: {job_id}')

        return remote_out_path

    @staticmethod
    def __translate_file(theory, temp_inp_dir: str, temp_out_dir: str, bucket, s3_key: str, data) -> Optional[str]:
        # Download file
        filename = path.basename(s3_key)

        if filename.strip() == '':
            return None

        log(f'Downloading "{s3_key}"...')
        local_inp_path = path.join(temp_inp_dir, filename)
        bucket.download_file(s3_key, local_inp_path)

        # Translate input file
        local_out_path = path.join(
            temp_out_dir, theory.tar_lang_def.get_translated_file_name(filename))
        theory.translate(local_inp_path, local_out_path, request_data=data)

        # Delete downloaded input file
        os.remove(local_inp_path)

        return local_out_path
