# Copyright 2024 Luminary Cloud, Inc. All Rights Reserved.
from luminarycloud._proto.api.v0.luminarycloud.geometry import geometry_pb2 as geometrypb
from luminarycloud._proto.upload import upload_pb2 as uploadpb
from os import PathLike
from .._client import Client
from .upload import upload_file
from typing import Optional
from luminarycloud._helpers import util
import uuid
import random
import time

import logging

logger = logging.getLogger(__name__)


def create_geometry(
    client: Client,
    cad_file_path: PathLike | str,
    project_id: str,
    *,
    name: Optional[str] = None,
    scaling: Optional[float] = None,
    wait: bool = False,
) -> geometrypb.Geometry:

    # TODO(onshape): Document this publicly when we release
    cad_file_path_str = str(cad_file_path)
    if "https://" in cad_file_path_str and ".onshape.com" in cad_file_path_str:
        if name is None:
            # Onshape will fill in an empty string with the document - element name
            name = ""

        web_geometry_reply = client.UploadWebGeometry(
            uploadpb.UploadWebGeometryRequest(
                project_id=project_id,
                url=cad_file_path_str,
            )
        )
        url = ""
        web_geometry_id = web_geometry_reply.web_geometry_id
    else:
        cad_file_meta = util.get_file_metadata(cad_file_path)
        logger.info(
            f"creating geometry in {project_id} by uploading file: {cad_file_meta.name}.{cad_file_meta.ext}, "
            + f"size: {cad_file_meta.size} bytes, sha256: {str(cad_file_meta.sha256_checksum)}, "
            + f"crc32c: {cad_file_meta.crc32c_checksum}"
        )

        finish_res = upload_file(
            client,
            project_id,
            uploadpb.ResourceParams(geometry_params=uploadpb.GeometryParams()),
            cad_file_path,
        )[1]
        url = finish_res.url
        web_geometry_id = ""

        if name is None:
            # if the caller did not provide a name, use the file name
            name = cad_file_meta.name

    if scaling is None:
        # default to no scaling
        scaling = 1.0

    create_geo_res: geometrypb.CreateGeometryResponse = client.CreateGeometry(
        geometrypb.CreateGeometryRequest(
            project_id=project_id,
            name=name,
            url=url,
            web_geometry_id=web_geometry_id,
            scaling=scaling,
            wait=False,
            request_id=str(uuid.uuid4()),
        )
    )
    geo = create_geo_res.geometry

    # Prefer polling on the client than waiting on the server (although waiting on the server
    # notifies the clients potentially faster).
    if wait:
        last_version_id = ""
        while not last_version_id:
            jitter = random.uniform(0.5, 1.5)
            time.sleep(2 + jitter)
            req = geometrypb.GetGeometryRequest(geometry_id=create_geo_res.geometry.id)
            res_geo: geometrypb.GetGeometryResponse = client.GetGeometry(req)
            geo = res_geo.geometry
            last_version_id = geo.last_version_id

    logger.info(f"created geometry {geo.name} ({geo.id})")
    return geo
