"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/nodes/stream_out.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1aapi/nodes/stream_out.proto\x12\x07synapse"I\n\x10UDPUnicastConfig\x12\x1b\n\x13destination_address\x18\x01 \x01(\t\x12\x18\n\x10destination_port\x18\x02 \x01(\r"_\n\x0fStreamOutConfig\x12\r\n\x05label\x18\x01 \x01(\t\x120\n\x0budp_unicast\x18\x02 \x01(\x0b2\x19.synapse.UDPUnicastConfigH\x00B\x0b\n\ttransport"E\n\x0fStreamOutStatus\x12\x17\n\x0fthroughput_mbps\x18\x01 \x01(\x02\x12\x19\n\x11failed_send_count\x18\x02 \x01(\x04b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.nodes.stream_out_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_UDPUNICASTCONFIG']._serialized_start = 39
    _globals['_UDPUNICASTCONFIG']._serialized_end = 112
    _globals['_STREAMOUTCONFIG']._serialized_start = 114
    _globals['_STREAMOUTCONFIG']._serialized_end = 209
    _globals['_STREAMOUTSTATUS']._serialized_start = 211
    _globals['_STREAMOUTSTATUS']._serialized_end = 280