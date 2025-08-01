from enum import StrEnum

class EmitDataType(StrEnum):
    """Defines valid data types for emitting events."""
    ACTIVITY = 'activity'
    CODE = 'code'
    THINKING = 'thinking'

class PromptRole(StrEnum):
    """Defines valid prompt roles."""
    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'

class AttachmentType(StrEnum):
    """Defines valid attachment types."""
    AUDIO = 'audio'
    DOCUMENT = 'document'
    IMAGE = 'image'
    VIDEO = 'video'
