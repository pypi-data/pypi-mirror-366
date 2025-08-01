import logging
from dataclasses import dataclass

from humanize.time import precisedelta
from pydub import AudioSegment, silence

logger = logging.getLogger("subtitle_tool.audio")


@dataclass
class AudioSplitter:
    """
    Utility class to split audio segments.

    Attributes:
        min_silence_length (int): duration in milliseconds when a sound period
            with less volume than silence_threshold is considered a segment of
            silence. (default: 200 milliseconds)
        silence_threshold (int): volume in dBFS (decibels relative to full scale)
            that is considered silence (default: -40 dBFS)
    """

    min_silence_length: int = 100
    silence_threshold: int = -40

    def split_audio(
        self,
        audio_clip: AudioSegment,
        segment_length: int = 30,
        keep_silence: bool = True,
    ) -> list[AudioSegment]:
        """
        Splits an audio file into segments based on silence.

        Args:
            audio_clip (AudioSegment): Audio clip to be split
            segment_length (int): Audio segment length in seconds (default: 30)
            keep_silence (bool): Whether silence should be kept in the segments
                (default: True)

        Returns:
            list[AudioSegment]: List of segments from the audio file.
        """

        chunks: list[AudioSegment] = silence.split_on_silence(
            audio_clip,
            min_silence_len=self.min_silence_length,
            silence_thresh=self.silence_threshold,
            keep_silence=keep_silence,  # keep silence in the chunks
        )  # type: ignore
        logging.debug(f"Extracted a total of {len(chunks)} chunks")

        # Debugging metrics
        min_duration = 9999
        max_duration = 0
        segments_above_thr = 0

        # Creating a new segment group with the top segment empty
        cur_segment = AudioSegment.silent(duration=0)
        segments = []
        for chunk in chunks:
            # Current segment is the last in the list
            segment_dur = cur_segment.duration_seconds
            chunk_dur = chunk.duration_seconds

            if segment_dur + chunk_dur < segment_length:
                logger.debug(f"Adding chunk ({chunk_dur}) to segment ({segment_dur})")
                cur_segment += chunk
            else:
                logging.debug(
                    f"Adding chunk ({chunk_dur}) overflows the segment ({segment_dur})"
                )
                # Only add segments to the list of segments if they have
                # something in them.
                # This covers the case when the initial segment extracted
                # is longer than the minimum duration period.
                if cur_segment.duration_seconds > 0:
                    # Metrics
                    if segment_dur < min_duration:
                        min_duration = segment_dur
                    if segment_dur > max_duration:
                        max_duration = segment_dur
                    if segment_dur > segment_length:
                        segments_above_thr += 1

                    segments.append(cur_segment)
                cur_segment = chunk
                logger.debug(f"Most recent segment is new chunk ({chunk_dur})")
        # Add the cur_segment to the list to complete the pass
        segment_dur = cur_segment.duration_seconds
        if segment_dur < min_duration:
            min_duration = segment_dur
        if segment_dur > max_duration:
            max_duration = segment_dur
        if segment_dur > segment_length:
            segments_above_thr += 1
        segments.append(cur_segment)

        segments_length = int(sum(segment.duration_seconds for segment in segments))
        min_duration = int(min_duration)
        max_duration = int(max_duration)
        avg_duration = int(segments_length / len(segments))
        logger.debug(f"Grouped segments {len(segments)}")
        logger.debug(
            f"Segments playtime: {segments_length} ({precisedelta(segments_length)})"
        )
        logger.debug(f"Minimum segment duration: {precisedelta(min_duration)}")
        logger.debug(f"Maximum segment duration: {precisedelta(max_duration)}")
        logger.debug(f"Average segment duration: {precisedelta(avg_duration)}")
        logger.debug(
            f"Segments longer than {precisedelta(segment_length)}: {segments_above_thr}"
        )

        return segments
