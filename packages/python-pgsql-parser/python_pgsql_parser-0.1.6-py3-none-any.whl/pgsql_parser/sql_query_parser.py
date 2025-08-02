import json
from typing import List, Dict, Optional
from .sqlparser import SQLLexer, Token, TokenType


class SimpleSqlQueryParser:
    """
    A simple SQL query parser that extracts table names, column names, and aliases
    from SELECT statements, leveraging a provided SQLLexer for tokenization.

    This parser aims to handle basic SELECT...FROM and JOIN structures.

    Limitations:
    - Relies heavily on token sequence and might not handle all valid SQL
      syntax variations or complex nested expressions perfectly.
    - Does not build a full Abstract Syntax Tree (AST).
    - Error handling for malformed queries is basic.
    - Assumes the query is a single SELECT statement.
    - Implicit alias detection is a heuristic and may misinterpret certain keywords
      (e.g., 'SELECT col DESC' might parse 'DESC' as an alias).
    """

    def __init__(self, query: str, lexer: SQLLexer = None):
        """
        Initializes the parser with the SQL query string and an SQLLexer instance.

        Args:
            query: The SQL query string to parse.
            lexer: An instance of SQLLexer to tokenize the query.
        """
        self.query = query
        self.lexer = lexer or SQLLexer()
        self.tokens: List[Token] = []
        self.table_name: Optional[str] = None
        self.tables_in_scope: Dict[str, str] = {}  # alias -> original_table_name
        self.select_elements: List[Dict[str, Optional[str]]] = []
        self._parse()

    def _look_ahead_match(
        self,
        start_index: int,
        look_ahead: Optional[int] = 1,
        expected_value: Optional[str] = None,
    ):
        pos = start_index + look_ahead
        if pos < len(self.tokens) and expected_value:
            tok = self.tokens[pos]
            return tok.value.strip('"').upper() == expected_value.upper
        return False

    def _look_ahead_not_match(
        self,
        start_index: int,
        look_ahead: Optional[int] = 1,
        expected_value: Optional[str] = None,
    ):
        pos = start_index + look_ahead
        if pos < len(self.tokens) and expected_value:
            tok = self.tokens[pos]
            return tok.value.strip('"').upper() != expected_value.upper

        return True

    def _look_ahead_type_match(
        self,
        start_index: int,
        look_ahead: Optional[int] = 1,
        expected_value: Optional[TokenType] = None,
    ):
        pos = start_index + look_ahead
        if pos < len(self.tokens) and expected_value:
            tok = self.tokens[pos]
            if isinstance(expected_value, list):
                return tok.token_type in expected_value
            return tok.token_type == expected_value
        return False

    def _look_ahead_type_not_match(
        self,
        start_index: int,
        look_ahead: Optional[int] = 1,
        expected_value: Optional[TokenType] = None,
    ):
        pos = start_index + look_ahead
        if pos < len(self.tokens) and expected_value:
            tok = self.tokens[pos]
            if isinstance(expected_value, list):
                return tok.token_type not in expected_value
            return tok.token_type != expected_value

        return True

    def read_parentheses_enclosure(self, start_index: int):
        s_index = start_index
        cur_index = s_index
        parentheses_balance = 0
        while cur_index < len(self.tokens):
            if self.tokens[cur_index].value == "(":
                parentheses_balance += 1
            elif parentheses_balance > 0 and self.tokens[cur_index].value == ")":
                parentheses_balance -= 1
            elif parentheses_balance == 0:
                cur_index -= 1
                break
            cur_index += 1

        return cur_index

    def _read_table_and_alias(self, start_index, end_index) -> int:
        token = self.tokens[start_index]
        tbname = token.value.strip('"')
        if not self.tables_in_scope:
            self.table_name = tbname
        # print("DDDDD----", start_index, end_index, token.value)
        # if start_index + 1 < end_index:
        #     print(
        #         "DDDDD---1",
        #         self.tokens[start_index + 1].token_type,
        #         self.tokens[start_index + 1].value,
        #     )
        # if start_index + 2 < end_index:
        #     print(
        #         "DDDDD---2",
        #         self.tokens[start_index + 2].token_type,
        #         self.tokens[start_index + 2].value,
        #     )

        if start_index == end_index - 1:
            self.tables_in_scope[tbname] = tbname
            return start_index
        elif start_index == end_index - 2:
            self.tables_in_scope[self.tokens[start_index + 1].value.strip('"')] = tbname
            return start_index + 1
        elif self._look_ahead_match(
            start_index, expected_value="AS"
        ) and self._look_ahead_type_match(
            start_index,
            look_ahead=2,
            expected_value=[TokenType.IDENTIFIER, TokenType.QUOTED_IDENTIFIER],
        ):
            self.tables_in_scope[self.tokens[start_index + 2].value.strip('"')] = tbname
            return start_index + 2
        elif self._look_ahead_type_match(
            start_index,
            expected_value=[TokenType.IDENTIFIER, TokenType.QUOTED_IDENTIFIER],
        ) and self._look_ahead_type_match(
            start_index,
            look_ahead=2,
            expected_value=[TokenType.KEYWORD, TokenType.PUNCTUATION],
        ):
            self.tables_in_scope[self.tokens[start_index + 1].value.strip('"')] = tbname
            return start_index + 1
        else:
            self.tables_in_scope[tbname] = tbname
            return start_index

    def _skip_join_keywords(self, start_index, end_index) -> int:
        curr_pos = start_index
        while curr_pos < end_index:
            token = self.tokens[curr_pos]
            print(curr_pos, token.value)
            if token.token_type == TokenType.KEYWORD and token.value.upper() in [
                "INNER",
                "LEFT",
                "RIGHT",
                "FULL",
                "CROSS",
                "JOIN",
                "OUTER",
            ]:
                curr_pos += 1
            else:
                curr_pos -= 1
                break
        return curr_pos

    def _skip_to_join_keywords(self, start_index, end_index) -> int:
        curr_pos = start_index
        while curr_pos < end_index:
            token = self.tokens[curr_pos]
            if token.token_type != TokenType.KEYWORD or token.value.upper() not in [
                "INNER",
                "LEFT",
                "RIGHT",
                "FULL",
                "CROSS",
                "JOIN",
                "OUTER",
            ]:
                curr_pos += 1
            else:
                break
        return curr_pos

    def _parse(self):
        """
        Internal method to parse the SQL query using tokens from the lexer.
        """
        # Tokenize the query, filtering out whitespace and comments for easier parsing logic
        self.tokens = self.lexer.tokenize(self.query)

        if not self.tokens:
            return

        # Find SELECT and FROM keywords to delineate clauses
        select_idx = -1
        from_idx = -1
        end_of_from_idx = len(
            self.tokens
        )  # Default to end of tokens if no subsequent clause

        for i, token in enumerate(self.tokens):
            if token.token_type == TokenType.KEYWORD:
                if select_idx == -1 and token.value.upper() == "SELECT":
                    select_idx = i
                elif from_idx == -1 and token.value.upper() == "FROM":
                    from_idx = i

                # Keywords that mark the end of the FROM clause
                elif token.value.upper() in [
                    "WHERE",
                    "GROUP",
                    "ORDER",
                    "LIMIT",
                    "OFFSET",
                    "HAVING",
                ]:
                    if (
                        from_idx != -1 and i > from_idx
                    ):  # Ensure FROM clause has already been found
                        end_of_from_idx = i
                        break  # Stop at the first such clause

        if select_idx == -1:
            # Not a SELECT query, or malformed (e.g., starts with FROM)
            return

        # --- Phase 1: Parse FROM/JOIN clause to build tables_in_scope ---
        if from_idx != -1:
            current_token_idx = from_idx + 1
            while current_token_idx < end_of_from_idx:
                token = self.tokens[current_token_idx]
                # Identify table name or alias
                if token.token_type in (
                    TokenType.IDENTIFIER,
                    TokenType.QUOTED_IDENTIFIER,
                ):
                    current_token_idx = self._read_table_and_alias(
                        current_token_idx, end_of_from_idx
                    )
                elif token.token_type == TokenType.KEYWORD and token.value.upper() in [
                    "INNER",
                    "LEFT",
                    "RIGHT",
                    "FULL",
                    "CROSS",
                    "JOIN",
                    "OUTER",
                ]:
                    current_token_idx = self._skip_join_keywords(
                        current_token_idx, end_of_from_idx
                    )
                elif token.token_type == TokenType.KEYWORD and token.value.upper() in [
                    "ON"
                ]:
                    current_token_idx = self._skip_to_join_keywords(
                        current_token_idx, end_of_from_idx
                    )
                elif token.value == "(":
                    current_token_idx = self.read_parentheses_enclosure(
                        current_token_idx
                    )

                current_token_idx += 1

        # --- Phase 2: Parse SELECT clause elements ---
        current_token_idx = select_idx + 1
        select_tokens_end_idx = from_idx if from_idx != -1 else len(self.tokens)

        current_element_tokens: List[Token] = []
        paren_balance = 0  # To handle functions like COUNT(*) or CONCAT(a, b)

        while current_token_idx < select_tokens_end_idx:
            token = self.tokens[current_token_idx]

            if token.token_type == TokenType.PUNCTUATION:
                if token.value == "(":
                    paren_balance += 1
                elif token.value == ")":
                    paren_balance -= 1
                elif token.value == "," and paren_balance == 0:
                    # End of a select element, process it
                    self._process_select_element_tokens(current_element_tokens)
                    current_element_tokens = []  # Reset for next element
                    current_token_idx += 1
                    continue  # Skip to next iteration to avoid adding comma to next element

            current_element_tokens.append(token)
            current_token_idx += 1

        # Process the last collected element (or the only one if no commas)
        if current_element_tokens:
            self._process_select_element_tokens(current_element_tokens)

    def _process_select_element_tokens(self, tokens: List[Token]):
        """
        Processes a list of tokens representing a single select element
        (e.g., 'u.id', 'name AS full_name', 'COUNT(*)').
        Extracts column name, alias, and resolves associated table.
        """
        if not tokens:
            return
        # print("--------------------------------------")
        # for token in tokens:
        #     print(token.token_type, token.value)
        # print("--------------------------------------")
        associated_table: Optional[str] = self.table_name
        if len(tokens) == 1:
            self.select_elements.append(
                {
                    "column": tokens[0].value,
                    "alias": None,
                    "table": associated_table,
                }
            )
            return

        if len(tokens) == 2:
            self.select_elements.append(
                {
                    "column": tokens[0].value,
                    "alias": tokens[1].value,
                    "table": associated_table,
                }
            )
            return

        if len(tokens) == 3:
            if (
                tokens[1].token_type == TokenType.KEYWORD
                and tokens[1].value.upper() == "AS"
            ):
                self.select_elements.append(
                    {
                        "column": tokens[0].value,
                        "alias": tokens[2].value,
                        "table": associated_table,
                    }
                )
            elif tokens[1].value == ".":
                potential_table_or_alias = tokens[0].value.strip('"')
                associated_table = self._get_associated_table_name(
                    potential_table_or_alias
                )
                self.select_elements.append(
                    {
                        "column": tokens[2].value,
                        "alias": None,
                        "table": associated_table,
                    }
                )
            else:
                raise f"Unknow syntax:{json.dumps(tokens, indent=2)}"
            return

        if (
            len(tokens) == 4
            and tokens[0].token_type
            in [TokenType.IDENTIFIER, TokenType.QUOTED_IDENTIFIER]
            and tokens[1].value == "."
            and tokens[2].token_type
            in [TokenType.IDENTIFIER, TokenType.QUOTED_IDENTIFIER]
            and tokens[3].token_type
            in [TokenType.IDENTIFIER, TokenType.QUOTED_IDENTIFIER]
        ):
            self.select_elements.append(
                {
                    "column": tokens[2].value.strip('"'),
                    "alias": tokens[3].value.strip('"'),
                    "table": self._get_associated_table_name(
                        tokens[0].value.strip('"')
                    ),
                }
            )
            return

        if (
            len(tokens) == 5
            and tokens[0].token_type
            in [TokenType.IDENTIFIER, TokenType.QUOTED_IDENTIFIER]
            and tokens[1].value == "."
            and tokens[2].token_type
            in [TokenType.IDENTIFIER, TokenType.QUOTED_IDENTIFIER]
            and tokens[3].value == "AS"
            and tokens[4].token_type
            in [TokenType.IDENTIFIER, TokenType.QUOTED_IDENTIFIER]
        ):
            self.select_elements.append(
                {
                    "column": tokens[2].value.strip('"'),
                    "alias": tokens[4].value.strip('"'),
                    "table": self._get_associated_table_name(
                        tokens[0].value.strip('"')
                    ),
                }
            )
            return

        alias: Optional[str] = None
        raw_column_expression: List[Token] = None
        if (
            tokens[-2].token_type == TokenType.KEYWORD
            and tokens[-2].value.upper() == "AS"
        ):
            alias = tokens[-1].value.strip('"')
            raw_column_expression = tokens[0:-2]
        elif (
            tokens[-2].token_type in [TokenType.PUNCTUATION] and tokens[-2].value != "."
        ):
            alias = tokens[-1].value.strip('"')
            raw_column_expression = tokens[0:-1]

        for tok in raw_column_expression:
            print(tok.token_type)

        tb = self._get_associated_table_name()
        if len(raw_column_expression) > 5 and raw_column_expression[1].value == "(":
            if (
                raw_column_expression[2].token_type
                in [TokenType.IDENTIFIER, TokenType.QUOTED_IDENTIFIER]
                and raw_column_expression[3].value == "."
            ):
                tb = self._get_associated_table_name(
                    raw_column_expression[2].value.strip('"')
                )
        self.select_elements.append(
            {
                "column": "".join([tok.value for tok in raw_column_expression]),
                "alias": alias,
                "table": tb,
            }
        )

    def _get_associated_table_name(
        self, potential_table_or_alias: Optional[str] = None
    ) -> str:
        if potential_table_or_alias is None:
            return self.get_table_name()

        if potential_table_or_alias in self.tables_in_scope:
            associated_table = self.tables_in_scope[potential_table_or_alias]
        else:
            # If it's not a known alias, assume it's a direct table name
            associated_table = potential_table_or_alias
            # Add to tables_in_scope if it's a direct table reference not yet seen
            self.tables_in_scope[potential_table_or_alias] = potential_table_or_alias
        return associated_table

    def get_table_name(self) -> Optional[str]:
        """
        Returns the primary table name extracted from the FROM clause (the first one encountered).
        Returns None if no table name is found.
        """
        return self.table_name

    def get_select_elements(self) -> List[Dict[str, Optional[str]]]:
        """
        Returns a list of dictionaries, where each dictionary represents a selected element
        and contains 'column', 'alias', and 'table' information.
        The 'table' will be the actual table name, resolved from aliases if used.
        """

        return self.select_elements

    def get_all_tables_in_scope(self) -> Dict[str, str]:
        """
        Returns a dictionary mapping aliases (or original table names if no alias)
        to their original table names found in the FROM/JOIN clause.
        """
        return self.tables_in_scope
