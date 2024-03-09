from codelimit.common.TokenRange import TokenRange
from codelimit.common.scope.Header import Header
from codelimit.common.scope.ScopeExtractor import ScopeExtractor
from codelimit.common.scope.scope_extractor_utils import has_curly_suffix, has_name_prefix
from codelimit.common.token_utils import get_balanced_symbol_token_indices


class JavaScopeExtractor(ScopeExtractor):
    def __init__(self):
        super().__init__(True)

    def extract_headers(self, tokens: list) -> list:
        result = []
        balanced_tokens = get_balanced_symbol_token_indices(tokens, "(", ")")
        for bt in balanced_tokens:
            if has_name_prefix(tokens, bt[0]) and has_curly_suffix(tokens, bt[1]):
                result.append(
                    Header(
                        tokens[bt[0] - 1].value,
                        TokenRange(tokens[bt[0] - 1: bt[1] + 1]),
                    )
                )
        return result

    def extract_blocks(self, tokens: list, headers: list) -> list:
        balanced_tokens = get_balanced_symbol_token_indices(tokens, "{", "}", True)
        blocks = [TokenRange(tokens[bt[0]: bt[1] + 1]) for bt in balanced_tokens]
        sorted_by_line = sorted(blocks, key=lambda tr: tr.tokens[0].location.line)
        sorted_by_columns = sorted(
            sorted_by_line, key=lambda tr: tr.tokens[0].location.column
        )
        return sorted_by_columns
