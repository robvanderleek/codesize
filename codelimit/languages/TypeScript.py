from codelimit.common.Language import Language
from codelimit.common.Token import Token
from codelimit.common.TokenRange import TokenRange
from codelimit.common.scope.Header import Header
from codelimit.common.scope.scope_utils import get_blocks, get_headers
from codelimit.common.token_matching.predicates.Balanced import Balanced
from codelimit.common.token_matching.predicates.Lookahead import Lookahead
from codelimit.common.token_matching.predicates.Name import Name
from codelimit.common.token_matching.predicates.Operator import Operator
from codelimit.common.token_matching.predicates.Or import Or


class TypeScript(Language):
    def extract_headers(self, tokens: list[Token]) -> list[Header]:
        return get_headers(
            tokens, [Name(), Balanced("(", ")"), Lookahead(Or("{", Operator(":")))]
        )

    def extract_blocks(
        self, tokens: list[Token], headers: list[Header]
    ) -> list[TokenRange]:
        return get_blocks(tokens, "{", "}")