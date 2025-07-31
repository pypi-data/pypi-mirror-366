"""
Common functions for the DaqData clients and servers
"""
import asyncio
import os
from pathlib import Path
import logging
import time
from typing import List, Callable, Tuple, Any, Dict, AsyncIterator, Optional
import numpy as np
from pandas import to_datetime, Timestamp
from datetime import datetime
import decimal

# rich formatting
from rich import print
from rich.logging import RichHandler
from rich.pretty import pprint, Pretty
from rich.console import Console

## gRPC imports
# Standard gRPC protobuf types
from google.protobuf.struct_pb2 import Struct
from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf import timestamp_pb2

# protoc-generated marshalling / demarshalling code
# from .daq_data_pb2
# import daq_data_pb2_grpc
from daq_data import daq_data_pb2
from .daq_data_pb2 import PanoImage
from daq_data.daq_data_pb2 import PanoImage, StreamImagesResponse, StreamImagesRequest
from panoseti_util import pff, control_utils
from .state import ReaderState, DataProductConfig

CFG_DIR = Path('daq_data/config')


def get_dp_config(dps: List[str]) -> Dict[str, DataProductConfig]:
    """
    Returns a dictionary of DataProductConfig objects for the given data products.
    """
    dp_cfg = {}
    for dp in dps:
        if dp == 'img16' or dp == 'ph1024':
            image_shape = (32, 32)
            bytes_per_pixel = 2
        elif dp == 'img8':
            image_shape = (32, 32)
            bytes_per_pixel = 1
        elif dp == 'ph256':
            image_shape = (16, 16)
            bytes_per_pixel = 2
        else:
            raise ValueError(f"Unknown data product: {dp}")

        bytes_per_image = bytes_per_pixel * image_shape[0] * image_shape[1]
        is_ph = 'ph' in dp
        pano_image_type = PanoImage.Type.PULSE_HEIGHT if is_ph else PanoImage.Type.MOVIE

        # Directly instantiate the dataclass instead of creating a dictionary
        dp_cfg[dp] = DataProductConfig(
            name=dp,
            is_ph=is_ph,
            pano_image_type=pano_image_type,
            image_shape=image_shape,
            bytes_per_pixel=bytes_per_pixel,
            bytes_per_image=bytes_per_image,
        )
    return dp_cfg


def make_rich_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    Sets up a logger with a RichHandler for console output and a FileHandler
    for writing logs to a file. Also silences noisy third-party loggers.

    Args:
        name (str): The name for the logger (e.g., 'daq_data').
        level (int): The logging level (e.g., logging.INFO).

    Returns:
        logging.Logger: A configured logger instance.
    """
    # 1. Silence noisy third-party loggers
    # The 'watchfiles' logger can be verbose, so we set its level higher.
    logging.getLogger("watchfiles").setLevel(logging.WARNING)

    # 2. Define log directory and file path
    log_dir = Path("daq_data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / f"{name}_{datetime.now().strftime('%Y-%m-%d')}.log"

    # 3. Get the logger and set its level.
    # We use getLogger(name) to get our specific application logger.
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent messages from being passed to the root logger
    logger.propagate = False

    # 4. Configure and add the RichHandler for console output
    # This handler is for pretty-printing logs to the terminal.
    console_handler = RichHandler(
        level=level,
        show_time=True,
        show_level=True,
        show_path=False, # Set to False for cleaner output
        rich_tracebacks=True,
        tracebacks_theme="monokai",
    )
    console_handler.setFormatter(logging.Formatter("[%(funcName)s()] %(message)s", datefmt="%H:%M:%S"))

    # 5. Configure and add the FileHandler for file output
    # This handler writes logs to the file defined above.
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s] - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    # 6. Add handlers to the logger, but only if they haven't been added already
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

def parse_pano_timestamps(pano_image: PanoImage) -> Dict[str, Any]:
    """Parse PanoImage header to get nanosecond-precision timestamps."""
    h = MessageToDict(pano_image.header)
    td = {}
    # Add nanosecond-precision Pandas Timestamp from panoseti packet timing
    if pano_image.shape == [16, 16]:
        td['wr_unix_timestamp'] = pff.wr_to_unix_decimal(h['pkt_tai'], h['pkt_nsec'], h['tv_sec'])
    elif pano_image.shape == [32, 32]:
        h_q0 = h['quabo_0']
        td['wr_unix_timestamp'] = pff.wr_to_unix_decimal(h_q0['pkt_tai'], h_q0['pkt_nsec'], h_q0['tv_sec'])
    nanoseconds_since_epoch = int(td['wr_unix_timestamp'] * decimal.Decimal('1e9'))
    td['pandas_unix_timestamp'] = to_datetime(nanoseconds_since_epoch, unit='ns')
    return td

def parse_pano_image(pano_image: daq_data_pb2.PanoImage) -> Dict[str, Any]:
    """Unpacks a PanoImage message into its components"""
    parsed_pano_image = MessageToDict(pano_image, preserving_proto_field_name=True, always_print_fields_with_no_presence=True)
    pano_timestamps = parse_pano_timestamps(pano_image)
    parsed_pano_image['header'].update(pano_timestamps)
    pano_type = parsed_pano_image['type']
    image_array = np.array(pano_image.image_array).reshape(pano_image.shape)
    bytes_per_pixel = pano_image.bytes_per_pixel
    if bytes_per_pixel == 1:
        image_array = image_array.astype(np.uint8)
    elif bytes_per_pixel == 2:
        if pano_type == 'MOVIE':
            image_array = image_array.astype(np.uint16)
        elif pano_type == 'PULSE_HEIGHT':
            image_array = image_array.astype(np.int16)
    else:
        raise ValueError(f"unsupported bytes_per_pixel: {bytes_per_pixel}")

    parsed_pano_image['image_array'] = image_array
    return parsed_pano_image

def format_stream_images_response(stream_images_response: StreamImagesResponse) -> str:
    parsed_pano_image = parse_pano_image(stream_images_response.pano_image)
    module_id = parsed_pano_image['module_id']
    pano_type = parsed_pano_image['type']
    header = parsed_pano_image['header']
    img = parsed_pano_image['image_array']
    frame_number = parsed_pano_image['frame_number']
    file = parsed_pano_image['file']
    name = stream_images_response.name
    message = stream_images_response.message
    server_timestamp = stream_images_response.timestamp.ToDatetime().isoformat()
    return f"{name=} {server_timestamp=} {file} (f#{frame_number}) {pano_type=} "


""" hp_io test macros """
def get_daq_active_file(sim_cfg, module_id):
    sim_data_dir = sim_cfg['files']['data_dir']
    sim_run_dir = sim_cfg['files']['sim_run_dir_template'].format(module_id=module_id)
    os.makedirs(f"{sim_data_dir}/{sim_run_dir}", exist_ok=True)
    daq_active_file = sim_cfg['files']['daq_active_file'].format(module_id=module_id)
    return f"{sim_data_dir}/{sim_run_dir}/{daq_active_file}"

def get_sim_pff_path(sim_cfg, module_id, seqno, is_ph, is_simulated):
    """
    Returns the path of the pff files in the simulated daq directory.
    """
    sim_data_dir = sim_cfg['files']['data_dir']
    if is_simulated:
        run_dir = sim_cfg['files']['sim_run_dir_template'].format(module_id=module_id)
        os.makedirs(f"{sim_data_dir}/{run_dir}", exist_ok=True)
    else:
        run_dir = sim_cfg['files']['real_run_dir']

    if is_ph:
        ph_pff = sim_cfg['files']['ph_pff_template'].format(module_id=module_id, seqno=seqno)
        return f"{sim_data_dir}/{run_dir}/{ph_pff}"
    else:
        movie_pff = sim_cfg['files']['movie_pff_template'].format(module_id=module_id, seqno=seqno)
        return f"{sim_data_dir}/{run_dir}/{movie_pff}"

def is_daq_active_sync(simulate_daq, sim_cfg=None):
    """Returns True iff the data stream from hashpipe or simulated hashpipe is active."""
    if simulate_daq:
        if sim_cfg is None:
            raise ValueError("sim_cfg must be provided when simulate_daq is True")
        daq_active_files = [get_daq_active_file(sim_cfg, mid) for mid in sim_cfg['sim_module_ids']]
        daq_active = any([os.path.exists(file) for file in daq_active_files])
    else:
        daq_active = control_utils.is_hashpipe_running()
    return daq_active

async def is_daq_active(simulate_daq, sim_cfg=None, retries=1, delay: float = 0.5):
    """Returns True iff the data stream from hashpipe or simulated hashpipe is active."""
    for i in range(retries):
        if is_daq_active_sync(simulate_daq, sim_cfg):
            return True
        await asyncio.sleep(delay)
    return False
