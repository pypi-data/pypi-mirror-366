import hashlib
import os
from typing import List
from time import time
from rara_subject_indexer.config import LOGGER


def md5sum(file_path: str) -> str:
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    except Exception as e:
        LOGGER.exception(f"Could not read file {file_path}: {e}")
        return None
    return hash_md5.hexdigest()


def find_checksums(root_dir: str) -> List[str]:
    if not os.path.exists(root_dir):
        LOGGER.error(f"Failed generating checksums. Directory {root_dir} does not exist!")
        return []
    
    LOGGER.info(f"Generating checksums for files in directory {root_dir}...")
    start = time()

    checksums = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            full_path = os.path.join(root, file)
            checksum = md5sum(full_path)
            if checksum:
                LOGGER.debug(f"{checksum} {full_path}")
                checksums.append(checksum)
              
    duration = time() - start
    LOGGER.info(f"Generating checksums for files in directory {root_dir} took: {duration}s")
    return checksums