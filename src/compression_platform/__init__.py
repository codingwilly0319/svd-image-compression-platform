from .compression import CompressionResult, CompressionVariant, compress_image
from .platform import ImageCompressionPlatform
from .records import CompressionRecord, RecordStore


__all__ = [
    "CompressionRecord",
    "CompressionResult",
    "CompressionVariant",
    "ImageCompressionPlatform",
    "RecordStore",
    "compress_image",
]
