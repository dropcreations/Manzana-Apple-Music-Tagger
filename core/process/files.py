import os
from utils import logger

def getFiles(path):
    logger.info("Getting files ready...")
    path = os.path.realpath(path)

    if os.path.isdir(path):
        content = os.listdir(path)
        content = [os.path.join(path, file) for file in content if os.path.splitext(file)[1] in [".mp4", ".m4a"]]

        if os.path.join(path, "Cover.mp4") in content:
            content.remove(
                os.path.join(
                    path,
                    "Cover.mp4"
                )
            )
        if len(content) == 0:
            logger.error("Input folder has no any supported file!", 1)
    else:
        if os.path.splitext(path)[1] in [".mp4", ".m4a"]:
            content = [path]
        else:
            logger.error("Input file is not supported!", 1)

    return content