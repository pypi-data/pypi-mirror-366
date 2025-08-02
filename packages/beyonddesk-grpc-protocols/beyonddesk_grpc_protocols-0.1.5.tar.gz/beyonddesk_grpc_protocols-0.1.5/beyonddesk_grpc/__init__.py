"""BeyondDesk gRPC Protocol Definitions"""

__version__ = "0.1.4"

# Import generated classes when available
try:
    from .user_service.user_service_pb2 import *
    from .user_service.user_service_pb2_grpc import *
except ImportError as e:
    print(f"⚠️  gRPC files not generated yet: {e}")
    pass

__all__ = [
    "__version__",
    # Will be populated by the * imports above
]