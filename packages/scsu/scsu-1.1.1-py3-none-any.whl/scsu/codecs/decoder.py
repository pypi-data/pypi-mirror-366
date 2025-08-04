"""
Decoding objects.
"""


from codecs import IncrementalDecoder
from math import ceil
from pickle import dumps, loads
from sys import byteorder as native_byteorder

from .info import CODEC_NAME, SIGNATURE_SUFFIX
from .states import Mode, DecoderState
from .tags import *
from ..window.bytes import decode_window_parameter
from ..window.supplement import decode_supplementary_window_parameter
from ..window.unicode import *


class SCSUDecodeError(BaseException):
    """Exception for SCSU decoding errors."""
    def message(self):
        """
        Get the message to display for a SCSU decoding error.

        :return: The exception message.
        """
        return self.args[0]

    def end(self):
        """
        Get the byte position where decoding failed.

        :return: The index of the byte that threw the error.
        """
        return self.args[1]


class SCSUIncrementalDecoder(IncrementalDecoder):
    """An incremental SCSU decoder."""
    state: DecoderState

    def __init__(self, errors="strict"):
        super().__init__(errors)
        self.reset()

    @staticmethod
    def name():
        """Get the codec name."""
        return CODEC_NAME

    @staticmethod
    def default_state():
        """Get a default state for the decoder."""
        state = DecoderState()
        state.signed = True
        return state

    def reset(self):
        """Reset the decoder state to the default state."""
        self.state = self.default_state()

    def getstate(self) -> int:
        """
        Get the decoder state.

        :return: The decoder state as an integer.
        """
        if self.state == self.default_state():
            return 0
        else:
            return int.from_bytes(dumps(self.state), byteorder=native_byteorder)

    def setstate(self, state: int):
        """
        Set the decoder state.

        :param state: The decoder state as an integer.
        """
        if state == 0:
            self.reset()
        else:
            self.state = loads(state.to_bytes(length=ceil(state.bit_length() / 8), byteorder=native_byteorder))

    def decode(self, s: bytes, final=False):
        """
        Incrementally decode bytes from SCSU.

        :param s: The bytes to decode.
        :param final: True if the given bytes are the final bytes to decode; false otherwise.
        :return: The decoded Unicode string.
        """
        output = ""
        last_index = 0

        for index, b in enumerate(s):
            try:
                output += self._decode_byte(b)
            except SCSUDecodeError as e:
                raise UnicodeDecodeError(self.name(), s, index, index + e.end(), e.message())

            last_index = index

        if final:
            if self.state.parameter_bytes_remaining > 0:
                raise UnicodeDecodeError(self.name(), s, last_index, last_index + len(self.state.instruction_buffer),
                                         f"incomplete instruction {self.state.instruction_buffer!r}")

            if len(self.state.surrogate_buffer) > 0:
                raise UnicodeDecodeError(self.name(), s, last_index, last_index + len(self.state.surrogate_buffer),
                                         f"leftover surrogate {self.state.surrogate_buffer!r}")

        if not self.state.signed:
            self.state.signed = True

            if output[0] == BYTE_ORDER_MARK:
                output = output[1:]

        return output

    def _decode_byte(self, b: int) -> str:
        """Decode a single byte while updating the decoder state."""
        output = ""

        if self.state.mode == Mode.SINGLE_BYTE:
            if self.state.parameter_bytes_remaining == 0:
                self.state.instruction_buffer.clear()

                if b in SQn or b in SDn:
                    self.state.instruction_buffer.append(b)
                    self.state.parameter_bytes_remaining = 1
                elif b in (SDX, SQU):
                    self.state.instruction_buffer.append(b)
                    self.state.parameter_bytes_remaining = 2
                elif b == SXR:
                    raise SCSUDecodeError(f"reserved single-byte mode instruction 0x{SXR:02X}", 1)
                elif b == SCU:
                    self.state.mode = Mode.UNICODE
                elif b in SCn:
                    self.state.active_window_index = SCn.index(b)
                else:
                    if b & 0x80:
                        output += self.state.active_window().decode(b)
                    else:
                        output += self.state.ascii().decode(b)
            else:
                self.state.instruction_buffer.append(b)
                self.state.parameter_bytes_remaining -= 1

                if self.state.parameter_bytes_remaining == 0:
                    instruction, parameters = self.state.instruction_buffer[0], self.state.instruction_buffer[1:]
                    assert instruction in SQn or instruction in SDn or instruction in (SDX, SQU)

                    if instruction in SQn:
                        assert len(parameters) == 1
                        index, quote_parameter = SQn.index(instruction), parameters[0]

                        if quote_parameter & 0x80:
                            output += self.state.dynamic_windows[index].decode(quote_parameter)
                        else:
                            output += self.state.static_windows[index].decode(quote_parameter)
                    elif instruction == SDX:
                        assert len(parameters) == 2
                        window_definition = decode_supplementary_window_parameter(parameters)

                        self.state.dynamic_windows[window_definition.index] = window_definition.window
                        self.state.active_window_index = window_definition.index
                    elif instruction == SQU:
                        assert len(parameters) == 2

                        if is_surrogate_byte_pair(parameters):
                            self.state.surrogate_buffer.extend(parameters)
                        else:
                            output += decode_bytes(parameters)
                    elif instruction in SDn:
                        assert len(parameters) == 1
                        index, window_parameter = SDn.index(instruction), decode_window_parameter(parameters[0])

                        self.state.dynamic_windows[index] = window_parameter
                        self.state.active_window_index = index

                    self.state.instruction_buffer.clear()
        elif self.state.mode == Mode.UNICODE:
            if self.state.parameter_bytes_remaining == 0:
                self.state.instruction_buffer.clear()

                if b in UCn:
                    self.state.mode = Mode.SINGLE_BYTE
                    self.state.active_window_index = UCn.index(b)
                elif b in UDn:
                    self.state.instruction_buffer.append(b)
                    self.state.parameter_bytes_remaining = 1
                elif b in (UQU, UDX):
                    self.state.instruction_buffer.append(b)
                    self.state.parameter_bytes_remaining = 2
                elif b == UXR:
                    raise SCSUDecodeError(f"reserved Unicode mode instruction 0x{UXR:02X}", 1)
                else:
                    self.state.instruction_buffer.append(b)
                    self.state.parameter_bytes_remaining = 1
            else:
                self.state.instruction_buffer.append(b)
                self.state.parameter_bytes_remaining -= 1

                if self.state.parameter_bytes_remaining == 0:
                    instruction, parameters = self.state.instruction_buffer[0], self.state.instruction_buffer[1:]

                    if instruction in UDn:
                        assert len(parameters) == 1
                        index, window_parameter = UDn.index(instruction), decode_window_parameter(parameters[0])

                        self.state.mode = Mode.SINGLE_BYTE
                        self.state.dynamic_windows[index] = window_parameter
                        self.state.active_window_index = index
                    elif instruction == UQU:
                        assert len(parameters) == 2

                        if is_surrogate_byte_pair(parameters):
                            self.state.surrogate_buffer.extend(parameters)
                        else:
                            output += decode_bytes(parameters)
                    elif instruction == UDX:
                        assert len(parameters) == 2
                        window_definition = decode_supplementary_window_parameter(parameters)

                        self.state.mode = Mode.SINGLE_BYTE
                        self.state.dynamic_windows[window_definition.index] = window_definition.window
                        self.state.active_window_index = window_definition.index
                    else:
                        if is_surrogate_byte_pair(self.state.instruction_buffer):
                            self.state.surrogate_buffer.extend(self.state.instruction_buffer)
                        else:
                            output += decode_bytes(self.state.instruction_buffer)

                    self.state.instruction_buffer.clear()

        assert len(self.state.surrogate_buffer) in (0, 2, 4)
        if len(self.state.surrogate_buffer) > 0:
            first_surrogate = self.state.surrogate_buffer[:2]

            if is_trailing_surrogate_byte_pair(first_surrogate):
                self.state.surrogate_buffer = self.state.surrogate_buffer[2:]
                raise SCSUDecodeError(f"trailing first surrogate {first_surrogate!r}", 2)

            if len(self.state.surrogate_buffer) == 4:
                second_surrogate = self.state.surrogate_buffer[2:]

                if is_leading_surrogate_byte_pair(first_surrogate) \
                        and is_trailing_surrogate_byte_pair(second_surrogate):
                    output += decode_bytes(self.state.surrogate_buffer)
                    self.state.surrogate_buffer.clear()
                elif is_leading_surrogate_byte_pair(first_surrogate) \
                        and is_leading_surrogate_byte_pair(second_surrogate):
                    self.state.surrogate_buffer = self.state.surrogate_buffer[2:]
                    raise SCSUDecodeError(f"leading second surrogate {second_surrogate!r}", 2)
                elif is_trailing_surrogate_byte_pair(second_surrogate):
                    self.state.surrogate_buffer.clear()
                    raise SCSUDecodeError(f"unmatched trailing second surrogate {second_surrogate!r}", 4)

        return output


class SignedSCSUIncrementalDecoder(SCSUIncrementalDecoder):
    """An incremental SCSU decoder that handles a byte-order mark."""
    @staticmethod
    def name():
        return CODEC_NAME + SIGNATURE_SUFFIX

    @staticmethod
    def default_state():
        state = DecoderState()
        state.signed = False
        return state
