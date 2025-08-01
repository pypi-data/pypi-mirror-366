"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/nodes/stream_in.proto')
_sym_db = _symbol_database.Default()
from ...api import datatype_pb2 as api_dot_datatype__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19api/nodes/stream_in.proto\x12\x07synapse\x1a\x12api/datatype.proto"E\n\x0eStreamInConfig\x12$\n\tdata_type\x18\x01 \x01(\x0e2\x11.synapse.DataType\x12\r\n\x05shape\x18\x02 \x03(\r")\n\x0eStreamInStatus\x12\x17\n\x0fthroughput_mbps\x18\x01 \x01(\x02b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.nodes.stream_in_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_STREAMINCONFIG']._serialized_start = 58
    _globals['_STREAMINCONFIG']._serialized_end = 127
    _globals['_STREAMINSTATUS']._serialized_start = 129
    _globals['_STREAMINSTATUS']._serialized_end = 170