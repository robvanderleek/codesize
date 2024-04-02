from pygments.lexers import PythonLexer
from pygments.lexers import JavascriptLexer

from codelimit.common.lexer_utils import lex
from codelimit.common.token_matching.Matcher import Matcher
from codelimit.common.token_matching.predicates.Balanced import Balanced
from codelimit.common.token_matching.predicates.Keyword import Keyword
from codelimit.common.token_matching.predicates.Lookahead import Lookahead
from codelimit.common.token_matching.predicates.Name import Name
from codelimit.common.token_matching.predicates.Optional import Optional


def test_match_keyword():
    code = "def foo(): pass\ndef bar(): pass\n"
    tokens = lex(PythonLexer(), code)

    result = Matcher(Keyword("def")).match(tokens)

    assert len(result) == 2
    assert result[0].token_string() == "def"
    assert result[1].token_string() == "def"


def test_match_name():
    code = "def foo(): pass\ndef bar(): pass\n"
    tokens = lex(PythonLexer(), code)

    result = Matcher(Name()).match(tokens)

    assert len(result) == 2
    assert result[0].token_string() == "foo"
    assert result[1].token_string() == "bar"


def test_match_function_header():
    code = "def foo(): pass\ndef bar(): pass\n"
    tokens = lex(PythonLexer(), code)

    result = Matcher([Keyword("def"), Name()]).match(tokens)

    assert len(result) == 2
    assert result[0].token_string() == "def foo"
    assert result[1].token_string() == "def bar"


def test_lookahead():
    code = "def foo(): pass\ndef bar(): pass\n"
    tokens = lex(PythonLexer(), code)

    result = Matcher([Keyword("def"), Lookahead(Name())]).match(tokens)

    assert len(result) == 2
    assert result[0].token_string() == "def"
    assert result[1].token_string() == "def"


def test_reset_pattern():
    code = "foo bar()"
    tokens = lex(PythonLexer(), code)

    result = Matcher([Name(), Balanced("(", ")")]).match(tokens)

    assert len(result) == 1


def test_string_pattern():
    code = "def bar()"
    tokens = lex(PythonLexer(), code)

    result = Matcher(["def", Name()]).match(tokens)

    assert len(result) == 1


def test_optional():
    code = ""
    code += "foo() {}\n"
    code += "function bar() {}\n"
    tokens = lex(JavascriptLexer(), code)

    result = Matcher(
        [Optional("function"), Name(), Balanced("(", ")"), Lookahead("{")]
    ).match(tokens)

    assert len(result) == 2


def test_ignore_incomplete_match():
    code = ""
    code += "def bar(\n"
    code += "def foo():\n"
    code += "  pass\n"
    tokens = lex(PythonLexer(), code)

    result = Matcher(["def", Name(), Balanced("(", ")")]).match(tokens)

    assert len(result) == 1
