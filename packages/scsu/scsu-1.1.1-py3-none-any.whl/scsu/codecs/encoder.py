"""
Encoding objects.
"""


from codecs import IncrementalEncoder
from math import ceil
from pickle import dumps, loads
from sys import byteorder as native_byteorder

from .info import CODEC_NAME, SIGNATURE_SUFFIX, BOM_SCSU
from .states import Mode, EncoderState
from .tags import *
from ..window.candidates import StaticWindowFit, DynamicWindowFit, DynamicWindowCandidate, preferred_window_candidate
from ..window.supplement import SupplementaryWindowDefinition, define_supplementary_window
from ..window.unicode import *


class SCSUEncodeError(BaseException):
    """Exception for SCSU encoding errors."""
    def message(self):
        """
        Get the message to display for a SCSU encoding error.

        :return: The exception message.
        """
        return self.args[0]


class SCSUIncrementalEncoder(IncrementalEncoder):
    """An incremental SCSU encoder."""
    state: EncoderState

    def __init__(self, errors="strict"):
        super().__init__(errors)
        self.reset()

    @staticmethod
    def name():
        """Get the codec name."""
        return CODEC_NAME

    @staticmethod
    def default_state():
        """Get a default state for the encoder."""
        state = EncoderState()
        state.signed = True
        return state

    def reset(self):
        """Reset the encoder state to the default state."""
        self.state = self.default_state()

    def getstate(self) -> int:
        """
        Get the encoder state.

        :return: The encoder state as an integer.
        """
        if self.state == self.default_state():
            return 0
        else:
            return int.from_bytes(dumps(self.state), byteorder=native_byteorder)

    def setstate(self, state: int):
        """
        Set the encoder state.

        :param state: The encoder state as an integer.
        """
        if state == 0:
            self.reset()
        else:
            self.state = loads(state.to_bytes(length=ceil(state.bit_length() / 8), byteorder=native_byteorder))

    def encode(self, s: str, final=False) -> bytes:
        """
        Incrementally encoder characters to SCSU.

        :param s: The characters to encode.
        :param final: True if the given characters are the final characters to encode; false otherwise.
        :return: The encoded byte array.
        """
        output = bytearray()
        last_index = 0

        for index, c in enumerate(s):
            if not self.state.signed:
                output.extend(BOM_SCSU)
                self.state.signed = True

            self.state.input_buffer.append(c)

            if self.state.input_buffer_full():
                c = self.state.input_buffer.popleft()
                lookahead = "".join(self.state.input_buffer)

                try:
                    output.extend(self._encode_char(c, lookahead))
                except SCSUEncodeError as e:
                    raise UnicodeEncodeError(self.name(), s, index, index + 1, e.message())

                last_index = index

        if final and len(self.state.input_buffer) > 0:
            while len(self.state.input_buffer) > 0:
                c = self.state.input_buffer.popleft()
                lookahead = "".join(self.state.input_buffer)

                try:
                    output.extend(self._encode_char(c, lookahead))
                except SCSUEncodeError as e:
                    raise UnicodeEncodeError(self.name(), s, last_index, last_index + 1, e.message())

                last_index += 1

        return bytes(output)

    def _encode_char(self, c: str, lookahead: str = "") -> bytearray:
        """Encode a single character while updating the encoder state."""
        if not in_bmp(c) and not in_smp(c):
            raise SCSUEncodeError(f"{c!r} not in BMP or SMP")

        output = bytearray()
        self.state.increment_window_ages()

        if self.state.mode == Mode.SINGLE_BYTE:
            if c in self.state.ascii():
                b = self.state.ascii().encode(c)

                if is_single_byte_tag(b):
                    output.append(SQn[0])

                output.append(b)
            elif is_compressible(c):
                dynamic_window_fit = self.state.dynamic_window_fit(c)

                if c in self.state.active_window():
                    output.append(self.state.active_window().encode(c))
                    self.state.reset_active_window_age()
                elif type(dynamic_window_fit) is DynamicWindowFit:
                    if len(lookahead) >= 1 and lookahead[0] in self.state.active_window():
                        output.append(SQn[dynamic_window_fit.index])
                        output.append(dynamic_window_fit.window.encode(c))
                        self.state.reset_window_age(dynamic_window_fit.index)
                    else:
                        output.append(SCn[dynamic_window_fit.index])
                        output.append(dynamic_window_fit.window.encode(c))
                        self.state.active_window_index = dynamic_window_fit.index
                        self.state.reset_active_window_age()
                elif in_bmp(c):
                    static_window_fit = self.state.static_window_fit(c)

                    if type(static_window_fit) is StaticWindowFit:
                        candidate = preferred_window_candidate(c, lookahead)

                        if type(candidate) is DynamicWindowCandidate:
                            output.extend(self._encode_new_window_definition(candidate))
                            output.append(self.state.active_window().encode(c))
                            self.state.reset_active_window_age()
                        else:
                            output.append(SQn[static_window_fit.index])
                            output.append(static_window_fit.window.encode(c))
                    else:
                        candidate = preferred_window_candidate(c)
                        assert type(candidate) is DynamicWindowCandidate

                        output.extend(self._encode_new_window_definition(candidate))
                        output.append(self.state.active_window().encode(c))
                        self.state.reset_active_window_age()
                else:
                    window_definition = define_supplementary_window(c, self.state.oldest_window_index())

                    output.extend(self._encode_supplementary_window_definition(window_definition))
                    output.append(self.state.active_window().encode(c))
                    self.state.reset_active_window_age()
            else:
                c_encoded = encode_str(c)

                if in_bmp(c) and len(lookahead) >= 1 and is_compressible(lookahead[0]) \
                        and not (len(lookahead) >= 2 and not is_compressible(lookahead[1])):
                    output.append(SQU)
                else:
                    output.append(SCU)
                    self.state.mode = Mode.UNICODE

                    if is_unicode_tag(c_encoded):
                        output.append(UQU)

                output.extend(c_encoded)
        elif self.state.mode == Mode.UNICODE:
            dynamic_window_fit = self.state.dynamic_window_fit(c)

            if is_compressible(c) and len(lookahead) >= 1 and is_compressible(lookahead[0]):
                if c in self.state.ascii():
                    output.append(UCn[self.state.active_window_index])
                    self.state.mode = Mode.SINGLE_BYTE

                    b = self.state.ascii().encode(c)

                    if is_single_byte_tag(b):
                        output.append(SQn[0])

                    output.append(b)
                elif type(dynamic_window_fit) is DynamicWindowFit:
                    output.append(UCn[dynamic_window_fit.index])
                    self.state.mode = Mode.SINGLE_BYTE
                    self.state.active_window_index = dynamic_window_fit.index

                    output.append(self.state.active_window().encode(c))
                    self.state.reset_active_window_age()
                elif in_bmp(c):
                    candidate = preferred_window_candidate(c)
                    assert type(candidate) is DynamicWindowCandidate

                    output.extend(self._encode_new_window_definition(candidate))
                    output.append(self.state.active_window().encode(c))
                    self.state.reset_active_window_age()
                else:
                    window_definition = define_supplementary_window(c, self.state.oldest_window_index())

                    output.extend(self._encode_supplementary_window_definition(window_definition))
                    output.append(self.state.active_window().encode(c))
                    self.state.reset_active_window_age()
            else:
                c_encoded = encode_str(c)

                if is_unicode_tag(c_encoded):
                    output.append(UQU)

                output.extend(c_encoded)

                if type(dynamic_window_fit) is DynamicWindowFit:
                    self.state.reset_window_age(dynamic_window_fit.index)

        return output

    def _encode_new_window_definition(self, candidate: DynamicWindowCandidate) -> bytearray:
        """Encode the instructions to define a new window in the BMP, then make the new window active."""
        output = bytearray()
        new_window_index = self.state.oldest_window_index()

        if self.state.mode == Mode.SINGLE_BYTE:
            output.append(SDn[new_window_index])
        elif self.state.mode == Mode.UNICODE:
            output.append(UDn[new_window_index])
            self.state.mode = Mode.SINGLE_BYTE

        output.append(candidate.parameter)

        self.state.dynamic_windows[new_window_index] = candidate.window
        self.state.active_window_index = new_window_index

        return output

    def _encode_supplementary_window_definition(self, definition: SupplementaryWindowDefinition) -> bytearray:
        """Encode the instructions to define a new window in the SMP, then make the new window active."""
        output = bytearray()

        if self.state.mode == Mode.SINGLE_BYTE:
            output.append(SDX)
        elif self.state.mode == Mode.UNICODE:
            output.append(UDX)

        output.extend(bytes(definition))

        self.state.dynamic_windows[definition.index] = definition.window
        self.state.active_window_index = definition.index

        return output


class SignedSCSUIncrementalEncoder(SCSUIncrementalEncoder):
    """An incremental SCSU encoder that handles a byte-order mark."""
    @staticmethod
    def name():
        return CODEC_NAME + SIGNATURE_SUFFIX

    @staticmethod
    def default_state():
        state = EncoderState()
        state.signed = False
        return state
