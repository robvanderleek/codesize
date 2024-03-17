from codelimit.common.Language import Language
from codelimit.common.Token import Token
from codelimit.common.TokenRange import TokenRange
from codelimit.common.scope.Header import Header
from codelimit.common.scope.scope_utils import get_headers, get_blocks
from codelimit.common.token_matching.predicates.Balanced import Balanced
from codelimit.common.token_matching.predicates.Lookahead import Lookahead
from codelimit.common.token_matching.predicates.Name import Name
from codelimit.common.token_matching.predicates.Symbol import Symbol


class Cpp(Language):
    def __init__(self):
        super().__init__(True)

    def extract_headers(self, tokens: list[Token]) -> list[Header]:
        return get_headers(tokens, [Name(), Balanced("(", ")"), Lookahead(Symbol("{"))])

    def extract_blocks(
            self, tokens: list[Token], headers: list[Header]
    ) -> list[TokenRange]:
        return get_blocks(tokens, "{", "}", extract_nested=True)
