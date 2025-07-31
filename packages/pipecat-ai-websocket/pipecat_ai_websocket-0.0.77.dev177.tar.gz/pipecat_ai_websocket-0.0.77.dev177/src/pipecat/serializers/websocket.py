import base64
import json
from typing import Optional

from loguru import logger
from pydantic import BaseModel
from pipecat.audio.utils import create_stream_resampler, pcm_to_ulaw, ulaw_to_pcm
from pipecat.frames.frames import (
    AudioRawFrame,
    CancelFrame,
    EndFrame,
    Frame,
    InputAudioRawFrame,
    InputDTMFFrame,
    KeypadEntry,
    StartFrame,
    StartInterruptionFrame,
    TransportMessageFrame,
    TransportMessageUrgentFrame,
    TextFrame
)
from pipecat.serializers.base_serializer import FrameSerializer, FrameSerializerType


class TelematicSerializer(FrameSerializer):

    class InputParams(BaseModel):
        sample_rate: int =  8000
        auto_hang_up: bool = True

    def __init__(
        self,
        stream_id: str,
        call_id: Optional[str] = None,
        auth_id: Optional[str] = None,
        auth_token: Optional[str] = None,
        params: Optional[InputParams] = None,

    ):
 
        self._stream_id = stream_id
        self._call_id = call_id
        self._auth_id = auth_id
        self._auth_token = auth_token
        self._params = params or TelematicSerializer.InputParams()
        self._input_resampler = create_stream_resampler()
        self._output_resampler = create_stream_resampler()
        self._hangup_attempted = False

    @property
    def type(self) -> FrameSerializerType:
        return FrameSerializerType.BINARY

    async def setup(self, frame: StartFrame):
        self._sample_rate = 8000

    async def serialize(self, frame: Frame) -> str | bytes | None:
        if (
            self._params.auto_hang_up
            and not self._hangup_attempted
            and isinstance(frame, (EndFrame, CancelFrame))
        ):
            self._hangup_attempted = True
            await self._hang_up_call()
            return None

        elif isinstance(frame, StartInterruptionFrame):
            return json.dumps({
                "event": "clearAudio",
                "streamId": self._stream_id
            })

        elif isinstance(frame, AudioRawFrame):
            data = frame.audio  # Expecting PCM16 at 8000 Hz

            if not data:
                return None

            payload = base64.b64encode(data).decode("utf-8")
            return json.dumps({
                "type": "streamAudio",
                "data": {
                    "audioDataType": "raw",
                    "sampleRate": 8000, # or self._sample_rate
                    "audioData": payload
                }
            })

        elif isinstance(frame, (TransportMessageFrame, TransportMessageUrgentFrame)):
            return json.dumps(frame.message)

        return None

    async def _hang_up_call(self):
        # TODO: Implement call hang-up using Plivo API
        logger.info("Hang-up triggered, but implementation is pending.")

    async def deserialize(self, data: str | bytes) -> Frame | None:
        if isinstance(data, bytes):
            if not data:
                return None
            return InputAudioRawFrame(
                                        audio=data,
                                        num_channels=1,
                                        sample_rate=8000  # or self._sample_rate
                                     )

        elif isinstance(data, str):
            text = data.strip()
            if text:
                return TextFrame(text=text)

        return None