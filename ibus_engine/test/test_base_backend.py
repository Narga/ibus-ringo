from nose.tools import eq_
from ibus_engine.base_backend import BaseBackend

try:
    from unittest.mock import Mock
except:
    from mock import Mock


class TestBaseBackend():

    def setup(self):
        self.expander = Mock()
        self.corrector = Mock()
        self.config = {
            "enable-text-expansion": False,
            "skip-non-vietnamese": True
        }

        self.backend = BaseBackend(
            config=self.config,
            abbr_expander=self.expander,
            auto_corrector=self.corrector)

    def test_update_composition(self):
        """
        update_composition() should create a new history entry.
        """
        string = "blah"

        self.backend.update_composition(string)

        expected = {
            "type": "update-composition",
            "raw-string": "",
            "editing-string": string
        }

        eq_(self.backend.last_action(), expected)

    def test_commit_composition(self):
        """
        commit_composition() should create a new history entry based on
        the last editing_string.
        """

        string = "blah"

        self.backend.commit_composition(string)

        expected = {
            "type": "commit-composition",
            "raw-string": "",
            "editing-string": string
        }

        eq_(self.backend.last_action(), expected)

    def test_text_expansion(self):
        """
        It should expand text if possible and allowed on space key press.
        FIXME: Just space key?
        """
        string = "bl"
        expanded = "blah"

        self.expander.expand = Mock(return_value=expanded)
        self.config["enable-text-expansion"] = True
        self.backend.update_composition = Mock()

        self.backend.editing_string = string
        self.backend.on_space_pressed()

        expected = {
            "type": "string-expansion",
            "raw-string": "",
            "editing-string": expanded
        }

        eq_(self.backend.last_action(), expected)
        self.backend.update_composition.assert_called_once_with(expanded)

    def test_reset(self):
        """
        reset() should create a history entry.
        """
        self.backend.reset()

        expected = {
            "type": "reset",
            "raw-string": "",
            "editing-string": ""
        }

        eq_(self.backend.last_action(), expected)

    def test_correction(self):
        """
        Should auto-correct.
        """
        string = "casl"
        corrected = "cas"

        self.expander.expand = Mock(return_value=string)
        self.corrector.suggest = Mock(return_value=corrected)

        self.backend.history.append({
            "type": "update-composition",
            "raw-string": string,
            "editing-string": string
        })

        self.backend.on_space_pressed()

        last_action = self.backend.last_action()
        eq_(last_action["type"], "string-correction")
        eq_(last_action["editing-string"], corrected + ' ')

    def test_backspace_undo_correction(self):
        self.backend.update_composition("ab", "ab")
        self.auto_corrector.suggest = Mock(return_value="aoe")
        self.config["enable-text-expansion"] = False
        self.config["skip-non-vietnamese"] = True

        self.backend.on_space_pressed()
        eq_(self.backend.last_action()["editing-string"], "aoe ")

        swallow = self.backend.on_backspace_pressed()
        eq_(self.backend.last_action()["editing-string"], "ab")
        eq_(swallow, True)

        swallow = self.backend.on_backspace_pressed()
        eq_(swallow, True)
        eq_(self.backend.last_action()["editing-string"], "a")

        swallow = self.backend.on_backspace_pressed()
        eq_(swallow, True)
        eq_(self.backend.last_action()["editing-string"], "")

        swallow = self.backend.on_backspace_pressed()
        eq_(swallow, False)

    def test_undo_update_composition(self):
        self.backend.update_composition("câ", "caa")
        self.backend.update_composition("cấ", "caas")

        self.backend.undo_last_action()

        last_action = self.backend.last_action()
        expected = {
            "type": "undo",
            "raw-string": "caa",
            "editing-string": "câ"
        }
        eq_(last_action, expected)

    def test_non_vietnamese(self):
        """
        It should keep non-Vietnamese strings intact.
        """
        string = "casl"

        self.corrector.suggest = Mock(return_value=string)

        self.backend.history.append({
            "type": "update-composition",
            "raw-string": string,
            "editing-string": string
        })

        self.backend.on_space_pressed()

        last_action = self.backend.last_action()
        eq_(last_action["type"], "update-composition")
        eq_(last_action["editing-string"], string)
