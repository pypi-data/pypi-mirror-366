"""
Main class entry point.
"""


from codecs import Codec, CodecInfo, StreamReader, StreamWriter, register

from .codecs.decoder import SCSUIncrementalDecoder, SignedSCSUIncrementalDecoder
from .codecs.encoder import SCSUIncrementalEncoder, SignedSCSUIncrementalEncoder
from .codecs.info import CODEC_NAME, ENCODING_NAME, SIGNATURE_SUFFIX


class SCSUCodec(Codec):
    """SCSU text codec class."""
    add_signature = False

    def encode(self, s, errors="strict"):
        """
        Encode a string as SCSU.

        :param s: The string to encode.
        :param errors: The default error scheme to use.
        :return: The encoded string.
        """
        encoder = SignedSCSUIncrementalEncoder(errors) if self.add_signature else SCSUIncrementalEncoder(errors)
        return encoder.encode(s, True), len(s)

    def decode(self, s, errors="strict"):
        """
        Decode bytes as SCSU.

        :param s: The bytes to decode.
        :param errors: The default error scheme to use.
        :return: The decoded string.
        """
        decoder = SignedSCSUIncrementalDecoder(errors) if self.add_signature else SCSUIncrementalDecoder(errors)
        return decoder.decode(s, True), len(s)


class SCSUStreamReader(SCSUCodec, StreamReader):
    """SCSU text stream reader."""
    pass


class SCSUStreamWriter(SCSUCodec, StreamWriter):
    """SCSU text stream writer."""
    pass


class SignedSCSUCodec(SCSUCodec):
    """SCSU text codec class that handles a byte-order mark."""
    add_signature = True


class SignedSCSUStreamReader(SignedSCSUCodec, StreamReader):
    """SCSU text stream reader that handles a byte-order mark."""
    pass


class SignedSCSUStreamWriter(SignedSCSUCodec, StreamWriter):
    """SCSU text stream writer that handles a byte-order mark."""
    pass


def scsu_search_function(encoding_name: str):
    """
    Try to get the codec information, given a codec name.

    :param encoding_name: The codec name.
    :return: The codec information if found; None otherwise.
    """
    if encoding_name[:len(CODEC_NAME)].casefold() == CODEC_NAME.casefold():
        if encoding_name[len(CODEC_NAME):].casefold() == SIGNATURE_SUFFIX.casefold():
            return CodecInfo(name=ENCODING_NAME + SIGNATURE_SUFFIX,
                             encode=SignedSCSUCodec().encode,
                             decode=SignedSCSUCodec().decode,
                             streamreader=SignedSCSUStreamReader,
                             streamwriter=SignedSCSUStreamWriter,
                             incrementalencoder=SignedSCSUIncrementalEncoder,
                             incrementaldecoder=SignedSCSUIncrementalDecoder)
        else:
            return CodecInfo(name=ENCODING_NAME,
                             encode=SCSUCodec().encode,
                             decode=SCSUCodec().decode,
                             streamreader=SCSUStreamReader,
                             streamwriter=SCSUStreamWriter,
                             incrementalencoder=SCSUIncrementalEncoder,
                             incrementaldecoder=SCSUIncrementalDecoder)

    return None


register(scsu_search_function)
