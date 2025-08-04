import shutil
import textwrap
import tempfile
import threading
import logging
import pyttsx4
import re
import sys
import os
import speech_recognition as sr
import warnings

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

warnings.filterwarnings(
    "ignore",
    message="pkg_resources is deprecated as an API",
    category=UserWarning,
    module=".*pkgdata"
)
import pygame

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_COMMANDS = {
    'voice': [
        "switch to voice", "voice mode", "enable voice", "listen to me", "activate voice"
    ],
    'keyboard': [
        "switch to keyboard", "keyboard mode", "type mode", "disable voice", "back to typing"
    ],
    'standby': [
        "standby", "go to sleep", "wait mode", "stop listening"
    ],
    'deactivate': [
        "deactivate", "shutdown"
    ],
    'pause': [
        "pause", "hold on", "wait", "wait a minute"
    ],
    'resume': [
        "resume", "continue", "carry on", "ok continue"
    ],
    'stop': [
        "stop", "halt", "end", "cancel"
    ]
}

ASSISTANT_GENDER = "Female" # Default gender for the assistant
DEFAULT_MODE = 'keyboard'  # Default input mode'

from HoloTTS import HoloTTS
from HoloSTT import HoloSTT
from HoloWave import HoloWave

class HoloEcho:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, commands=None):
        # Call the QObject initializer
        super().__init__()
        if hasattr(self, "initialized"):
            return
        self.ambInputLock    = threading.Lock()
        self.engine          = pyttsx4.init()
        self.recognizer      = sr.Recognizer()
        self.gender          = ASSISTANT_GENDER
        self.mode            = DEFAULT_MODE
        # Always merge user commands (if any) with the system default commands
        self.commands        = {**DEFAULT_COMMANDS, **(commands or {})}
        self.wordRepl        = None 
        self.decibelFactor   = 0
        self.semitoneFactor  = 0
        self.stepFactor      = 0
        self.soundChannel    = 2  # Default sound channel
        self.soundChoice     = 1  # Default sound choice
        self.timeOut         = 10  # seconds
        self.standardMaleVoice   = None  # Default
        self.standardFemaleVoice = None  # Default
        self.advancedMaleVoice   = None  # Default
        self.advancedFemaleVoice = None  # Default
        self.sounds          = {}
        self.synthesisMode   = 'Standard'  # Default synthesis mode
        self.isActivated     = False  # Activation state
        self.useFallback     = True
        self.printing        = False  # Flag to prevent printing during synthesis
        self.synthesizing    = False  # Flag to indicate if synthesis is in progress
        self.fileName        = None  # File name for sound playback
        self.deactivating    = False  # Flag to indicate deactivation state
        self.processing      = False  # Flag to indicate if processing is in progress
        self.paused          = False
        self.storedOutput    = []  # List to store synthesized output
        self.storedInput     = ''  # Holds the last recognized input NOT USED AT THIS TIME
        self.ambInput        = None  # Holds background input for processing
        self._buildPhraseMap()

        self.holoTTS  = HoloTTS(self) # Initialize the HoloTTS generator
        self.holoSTT  = HoloSTT(self) # Initialize the HoloTTS recognizer
        self.holoWave = HoloWave(self)  # Initialize the HoloWave instance
        self.initialized = True

    def _buildPhraseMap(self):
        self.phraseMap = {}
        for cmd, phrases in self.commands.items():
            for phrase in phrases:
                self.phraseMap[phrase] = cmd

        # print("Phrase Map:")
        # for cmd, phrases in self.commands.items():
        #     phraseList = ', '.join(f'"{p}"' for p in phrases)
        #     print(f"  {cmd}: {phraseList}")


    def getProperty(self, propName):
        """
        Retrieves properties from the TTS engine, HoloEcho instance, or special settings.
        """
        propMap = {
            # pyttsx4/pyttsx3 engine properties
            "rate":   lambda: self.engine.getProperty('rate'),
            "volume": lambda: self.engine.getProperty('volume'),
            "voice":  lambda: self.engine.getProperty('voice'),
            "voices": lambda: self.engine.getProperty('voices'),
            "pitch":  lambda: self.engine.getProperty('pitch'),  # pyttsx4 only

            # pygame mixer properties
            "soundChannel": lambda v: setattr(self, "soundChannel", int(v)),
            "soundChoice":  lambda v: setattr(self, "soundChoice", int(v)),

            # HoloEcho specific configs
            "gender":        lambda v: setattr(self, "gender", v.lower()),
            "mode":          lambda v: setattr(self, "mode", v.lower()),
            "timeOut":       lambda v: setattr(self, "timeOut", int(v)),
            "useFallback":   lambda v: setattr(self, "useFallback", bool(v)),
            "printing":      lambda v: setattr(self, "printing", bool(v)),
            "synthesizing":  lambda v: setattr(self, "synthesizing", bool(v)),
            "synthesisMode": lambda v: setattr(self, "synthesisMode", v),
            "commands":      lambda v: setattr(self, "commands", v),
            "wordRepl":      lambda v: setattr(self, "wordRepl", v),
        }
        getter = propMap.get(propName)
        if getter:
            return getter()
        else:
            raise AttributeError(f"Unknown property: '{propName}'. Allowed: {list(propMap)}")

    def setProperty(self, propName, value):
        """
        Sets properties on the TTS engine or HoloEcho instance.
        Supports both pyttsx4 engine properties and HoloEcho-specific settings.
        """
        propMap = {
            # pyttsx4/pyttsx3 engine properties
            "rate":   lambda v: self.engine.setProperty('rate', v),
            "volume": lambda v: self.engine.setProperty('volume', v),
            "voice":  lambda v: self.engine.setProperty('voice', v),
            "pitch":  lambda v: self.engine.setProperty('pitch', v),  # pyttsx4 only

            # pygame mixer properties
            "soundChannel": lambda v: setattr(self, "soundChannel", int(v)),
            "soundChoice":  lambda v: setattr(self, "soundChoice", int(v)),

            # HoloEcho specific configs
            "standardMaleVoice":   lambda v: setattr(self, "standardMaleVoice", int(v)),
            "standardFemaleVoice": lambda v: setattr(self, "standardFemaleVoice", int(v)),
            "advancedMaleVoice":   lambda v: setattr(self, "advancedMaleVoice", int(v)),
            "advancedFemaleVoice": lambda v: setattr(self, "advancedFemaleVoice", int(v)),
            "gender":          lambda v: setattr(self, "gender", v.lower()),
            "mode":            lambda v: setattr(self, "mode", v.lower()),
            "timeOut":         lambda v: setattr(self, "timeOut", int(v)),
            "useFallback":     lambda v: setattr(self, "useFallback", bool(v)),
            "printing":        lambda v: setattr(self, "printing", bool(v)),
            "synthesizing":    lambda v: setattr(self, "synthesizing", bool(v)),
            "synthesisMode":   lambda v: setattr(self, "synthesisMode", v),
            "commands":        self._setCommands,  # UPDATED: use merge
            "wordRepl":        lambda v: setattr(self, "wordRepl", v),
        }
        setter = propMap.get(propName)
        if setter:
            setter(value)
        else:
            raise AttributeError(f"Unknown property: '{propName}'. Allowed: {list(propMap)}")

    def _setCommands(self, userCommands):
        # Always start from the current self.commands (usually has the defaults)
        merged = {}
        # Extend or create each group
        for key in DEFAULT_COMMANDS:
            if userCommands and key in userCommands:
                userList = userCommands[key]
                defaultList = DEFAULT_COMMANDS[key]
                # Combine user + default, no dups, preserve user order
                merged[key] = userList + [x for x in defaultList if x not in userList]
            else:
                merged[key] = DEFAULT_COMMANDS[key][:]
        # If user added new keys (not in defaults), add them as well
        if userCommands:
            for key in userCommands:
                if key not in merged:
                    merged[key] = userCommands[key]
        self.commands = merged
        self._buildPhraseMap()

    def listVoices(self) -> list:
        """Prints and returns all available voices: [idx], Name, Lang, and full ID on its own line."""
        return self.holoTTS.listVoices()

    def manageCommands(self):
        if not self.isActivated:
            return
        while self.synthesizing:
            inBackground = self.ambientInput()
            if inBackground:
                if not (self.paused or self.deactivating):
                    self.handleBackgroundCommands(inBackground)
                    if self.holoSTT.allowInterruption(inBackground):
                        self.handleInterruptionCommands(inBackground)
                else:
                    self.handleBackgroundCommands(inBackground)

    def handleBackgroundCommands(self, command):
        if not self.isActivated:
            return
        if not command:
            return

        # Find the action for the command phrase (case-insensitive)
        action = self.phraseMap.get(command.lower())

        # Mapping action to method calls
        actionMap = {
            "pause":  self.pause,
            "resume": self.resume,
            "stop":   self.stop,
        }

        func = actionMap.get(action)
        if func:
            func()

    def handleInterruptionCommands(self, command):
        if not self.isActivated:
            return
        if command and not self.paused:
            with self.ambInputLock:
                self.ambInput = command
                self.stop()

    def parseCommands(self, command):
        if not command:
            return

        # Find the action for the command phrase (case-insensitive)
        action = self.phraseMap.get(command.lower())
        actionMap = {
            'standby':    self.handleStandby,
            'deactivate': self.handleDeactivation,
            'voice':      lambda: self.handleSwitch('voice'),
            'keyboard':   lambda: self.handleSwitch('keyboard')
        }
        func = actionMap.get(action)
        if func:
            func()

    def handleStandby(self):
        if self.isActivated:
            self.isActivated = False
        return 'standby'

    def handleDeactivation(self):
        self.engine.stop()
        del self.engine
        sys.exit(0)

    def handleSwitch(self, mode):
        if self.mode != mode:
            self.mode = mode
        return mode

    def handleAmbientInput(self) -> str:
        if not self.isActivated:
            return
        if self.deactivating:
            return None
        with self.ambInputLock:
            if self.ambInput:
                msg = self.ambInput
                self.ambInput = None
                return msg.lower().strip()

    def voiceInput(self) -> str:
        return self.holoSTT.voiceInput()

    def ambientInput(self) -> str:
        if self.mode == "keyboard":
            return self.keyboardInput()
        return self.holoSTT.ambientInput()

    def keyboardInput(self, keyboardMsg):
        return self.holoSTT.keyboardInput(keyboardMsg)

    def printMessage(self, type, text, name=None):
        self.printing = True
        name = name if name else self.name if self.name else "Assistant"
        type = type.lower()
        labelMap = {
            'user': "\nYou said",
            'assistant': f"{name.title()}"
        }
        label = labelMap.get(type, "Message")

        try:
            term_width = shutil.get_terminal_size((100, 20)).columns
        except Exception:
            term_width = 100
        lines = text.split('\n')
        wrapped_lines = [
            textwrap.fill(line, width=term_width, subsequent_indent='    ')
            for line in lines
        ]
        wrapped = "\n".join(wrapped_lines)

        print(f"{label}:\n {wrapped}\n")
        self.printing = False

    def getSound(self, key: int) -> None:
        self.holoWave.getSound(key)

    def createFile(self, media: str, delete: bool=False) -> None:
        with tempfile.NamedTemporaryFile(delete=delete, suffix=media) as temp_file:
            self.fileName = temp_file.name

    def transcribeContext(self, text: str) -> str:
        if not text or not isinstance(text, str):
            return ""
        return re.sub(r"([.!?]\s*)(\w)", lambda x: x.group(1) + x.group(2).upper(), text.capitalize())

    def setSynthesisMode(self, mode: str=None):
        self.synthesisMode = mode if mode else "Standard"
        return self.synthesisMode

    def getSynthesisMode(self):
        return self.synthesisMode if getattr(self, 'synthesisMode', None) else "Standard"

    def synthesize(self, text: str) -> None:
        if self.mode == "keyboard":
            return
        self.holoTTS.synthesize(text)

    def pause(self) -> None:
        self.holoTTS.pause()

    def resume(self) -> None:
        self.holoTTS.resume()

    def stop(self) -> None:
        self.holoTTS.stop()

    def _adjustAttributes(self) -> None:
        self.holoTTS.adjustAttributes()

    def resetAttributes(self) -> None:
        self.holoTTS.resetAttributes()

    def resetProperty(self, prop: str) -> None:
        self.holoTTS.resetProperty(prop)

    def increaseProperty(self, prop: str, value: int = 1) -> None:
        self.holoTTS.increaseProperty(prop, value)

    def decreaseProperty(self, prop: str, value: int = 1) -> None:
        self.holoTTS.decreaseProperty(prop, value)
