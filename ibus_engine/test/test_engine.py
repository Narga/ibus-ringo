#from nose.tools import eq_
from ibus_engine.base_backend import BaseBackend
from ibus_engine.abbr import AbbreviationExpander


class TestEngine():
    def setup(self):
        config = {
            "input-method": "telex",
            "output-charset": "utf-8",
            "skip-non-vietnamese": True,
            "auto-capitalize-abbreviations": False,
            "default-input-methods": {
                "telex": {
                    "a": "a^",
                    "o": "o^",
                    "e": "e^",
                    "w": ["u*", "o*", "a+", "<ư"],
                    "d": "d-",
                    "f": "\\",
                    "s": "/",
                    "r": "?",
                    "x": "~",
                    "j": ".",
                    "]": "<ư",
                    "[": "<ơ",
                    "}": "<Ư",
                    "{": "<Ơ"
                },
            }
        }

        self.eng = BaseBackend(
            config=config,
            abbr_expander=AbbreviationExpander(),
            auto_corrector=None)

    def send_keys(self, input, engine):
        [self.send_key(character, engine) for character in input]
        return self

    def send_key(self, input, engine):
        engine.process_key_event(ord(input), 0)

    def send_bksp(self, engine):
        engine.on_backspace_pressed()
        return self

    def send_space(self, engine):
        engine.on_space_pressed()
        return self

    def test_bug_123(self):
        """
        Should not raise IndexError when backspace is sent repeatedly
        """

        self.send_bksp(self.eng)
        self.send_bksp(self.eng)
        self.send_bksp(self.eng)
        self.send_bksp(self.eng)
