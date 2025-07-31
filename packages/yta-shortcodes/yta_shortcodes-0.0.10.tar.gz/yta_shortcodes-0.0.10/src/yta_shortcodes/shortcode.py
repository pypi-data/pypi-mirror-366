from yta_shortcodes.enums import ShortcodeDuration, SimpleShortcodeStart, BlockShortcodeStart
from yta_shortcodes.tag_type import ShortcodeTagType
from yta_validation import PythonValidator
from typing import Union


class Shortcode:
    """
    Base shortcode class that represent the minimum
    a shortcode can have. This class is pretended 
    to be used as a model to create a custom class.

    This class represent a shortcode once its been
    detected in the code with the Shortcode parser
    based on its corresponding shortcode tag that
    was registered to enable the detection, and
    includes the attributes found, the content (if
    existing) and the indexes of the words that 
    were inmediately before the start and end tag.
    """

    name: str
    """
    The shortcode name that represent the shortcode
    meaning.
    """
    _type: ShortcodeTagType
    """
    The shortcode type, that can be 'simple' or
    'block' scoped.
    """
    _context: any
    """
    TODO: I don't know what this is for
    """
    content: Union[None, str]
    """
    The content of the shortcode, that will be None
    if a simple-scoped shortcode, or a string if
    block-scoped.
    """
    attributes: list[dict]
    """
    The list of attributes found when reading the
    shortcode. These attributes can be single values
    (from args) or key-values (from kwargs).
    """
    start_previous_word_index: Union[int, None]
    """
    The index of the word that is inmediately before
    the start tag of this shortcode. Could be None if
    the shortcode is just at the begining. This index
    is considered within the text empty of shortcodes.
    """
    end_previous_word_index: Union[int, None]
    """
    The index of the word that is inmediately before
    the end tag of this shortcode. It is None if the
    shortcode is a simple one. This index is 
    considered within the text empty of shortcodes.
    """

    def __init__(
        self,
        tag: str,
        type: ShortcodeTagType,
        context: any,
        content: str,
        attributes: list[dict],
        start_previous_word_index: Union[int, None] = None,
        end_previous_word_index: Union[int, None] = None,
    ):
        type = ShortcodeTagType.to_enum(type)

        self.tag = tag
        self.type = type
        self._context = context
        self.content = content
        self.attributes = attributes
        self.start_previous_word_index = start_previous_word_index
        self.end_previous_word_index = end_previous_word_index

    @property
    def is_block_scoped(self):
        """
        Check if this shortcode is a block-scoped one
        [shortcode_tag] ... [/shortcode_tag].
        """
        return self._type == ShortcodeTagType.BLOCK
    
    @property
    def is_simple_scoped(self):
        """
        Check if this shortcode is a simple-scoped one
        [shortcode_tag].
        """
        return self._type == ShortcodeTagType.SIMPLE

class YTAShortcode(Shortcode):
    """
    Custom shortcode class that includes the
    ability to calculate the 'start' and 
    'duration' fields from a given transcription
    of the text in which it has been found. It
    will use the words next to the shortcode and
    their transcription time moment to obtain
    this shortcode 'start' and 'duration' values.
    """

    start: Union[BlockShortcodeStart, SimpleShortcodeStart, float, None] = None
    """
    The start time moment in which the shortcode 
    behaviour must be applied. This needs to be 
    calculated with a transcription of the text
    provided when obtaining this shortcode.
    """
    duration: Union[ShortcodeDuration, float, None] = None
    """
    The time the shortcode behaviour must last. This
    needs to be calculated with a transcription of
    the text provided when obtaining this shortcode.
    """

    @property
    def end(
        self
    ) -> Union[float, None]:
        """
        The end time moment in which the shortcode
        behaviour must end. This is calculated with the
        'start' and 'duration' parameters if set and
        valid and returned as a float number, or as None
        if not able to calculate.
        """
        if (
            PythonValidator.is_number(self.start) and
            PythonValidator.is_number(self.duration)
        ):
            return self.start + self.duration
        
        return None

    def __init__(
        self,
        tag: str,
        type: ShortcodeTagType,
        context: any,
        content: str,
        attributes: list[dict],
        start_previous_word_index: Union[int, None] = None,
        end_previous_word_index: Union[int, None] = None,
    ):
        super().__init__(tag, type, context, content, attributes, start_previous_word_index, end_previous_word_index)
        self.start = float(attributes.get('start', None)) if attributes.get('start', None) is not None else None
        self.duration = float(attributes.get('duration', None)) if attributes.get('duration', None) is not None else None

    def calculate_start_and_duration(
        self,
        transcription: 'AudioTranscription'
    ):
        """
        Processes this shortcode 'start' and 'duration'
        fields by using the 'transcription' (transcription
        object from 'yta_audio' library) if needed (if
        'start' and 'duration' fields are not numbers
        manually set by the user in the shortcode when
        written).

        This will consider the current 'start' and
        'duration' strategy and apply them to the words
        related to the shortcode to obtain the real 'start'
        and 'duration' number values.
        """
        # TODO: Here below I have simplified the code but
        # it is commented because if the value is not one
        # in the dict it will fail... but I think there is
        # no possibility of being not one in the dict
        if PythonValidator.is_instance_of(self.start, [SimpleShortcodeStart, BlockShortcodeStart]):
            if self.is_simple_scoped:
                # self.start = {
                #     ShortcodeStart.BETWEEN_WORDS: (transcription.words[self.start_previous_word_index].start + transcription.words[self.start_previous_word_index + 1].start) / 2
                # }[self.start]

                self.start = {
                    SimpleShortcodeStart.BETWEEN_WORDS: (transcription.words[self.start_previous_word_index].start + transcription.words[self.start_previous_word_index + 1].start) / 2
                }.get(self.start, self.start)

                # if self.start == SimpleShortcodeStart.BETWEEN_WORDS:
                #     self.start = (transcription.words[self.start_previous_word_index].start + transcription.words[self.start_previous_word_index + 1].start) / 2
            else:
                # self.start = {
                #     ShortcodeStart.START_OF_FIRST_SHORTCODE_CONTENT_WORD: transcription.words[self.start_previous_word_index + 1].start,
                #     ShortcodeStart.MIDDLE_OF_FIRST_SHORTCODE_CONTENT_WORD: (transcription.words[self.start_previous_word_index + 1].start + transcription.words[self.start_previous_word_index + 1].end) / 2,
                #     ShortcodeStart.END_OF_FIRST_SHORTCODE_CONTENT_WORD: transcription.words[self.start_previous_word_index + 1].end
                # }[self.start]

                self.start = {
                    BlockShortcodeStart.START_OF_FIRST_SHORTCODE_CONTENT_WORD: transcription.words[self.start_previous_word_index + 1].start,
                    BlockShortcodeStart.MIDDLE_OF_FIRST_SHORTCODE_CONTENT_WORD: (transcription.words[self.start_previous_word_index + 1].start + transcription.words[self.start_previous_word_index + 1].end) / 2,
                    BlockShortcodeStart.END_OF_FIRST_SHORTCODE_CONTENT_WORD: transcription.words[self.start_previous_word_index + 1].end
                }.get(self.start, self.start)

                # if self.start == BlockShortcodeStart.START_OF_FIRST_SHORTCODE_CONTENT_WORD:
                #     self.start = transcription.words[self.start_previous_word_index + 1].start
                # elif self.start == BlockShortcodeStart.MIDDLE_OF_FIRST_SHORTCODE_CONTENT_WORD:
                #     self.start = (transcription.words[self.start_previous_word_index + 1].start + transcription.words[self.start_previous_word_index + 1].end) / 2
                # elif self.start == BlockShortcodeStart.END_OF_FIRST_SHORTCODE_CONTENT_WORD:
                #     self.start = transcription.words[self.start_previous_word_index + 1].end

        if PythonValidator.is_instance_of(self.duration, ShortcodeDuration):
            if self.type == ShortcodeTagType.SIMPLE:
                # self.duration = {
                #     ShortcodeDuration.FILE_DURATION: FILE_DURATION
                # }[self.duration]

                self.duration = {
                    ShortcodeDuration.FILE_DURATION: ShortcodeDuration.FILE_DURATION.value
                }.get(self.duration, self.duration)

                # if self.duration == ShortcodeDuration.FILE_DURATION:
                #     # This duration must be set when the file is ready, so 
                #     # we use a number value out of limits to flag it
                #     # TODO: Maybe I can keep the enum and detect it later
                #     self.duration = ShortcodeDuration.FILE_DURATION.value
            else:
                # self.duration = {
                #     ShortcodeDuration.SHORTCODE_CONTENT: transcription.words[self.previous_end_word_index].end - transcription.words[self.previous_start_word_index + 1].start
                # }[self.duration]

                self.duration = {
                    ShortcodeDuration.SHORTCODE_CONTENT: transcription.words[self.end_previous_word_index].end - transcription.words[self.end_previous_word_index + 1].start
                }.get(self.duration, self.duration)

                # if self.duration == ShortcodeDuration.SHORTCODE_CONTENT:
                #     self.duration = transcription.words[self.end_previous_word_index].end - transcription.words[self.end_previous_word_index + 1].start