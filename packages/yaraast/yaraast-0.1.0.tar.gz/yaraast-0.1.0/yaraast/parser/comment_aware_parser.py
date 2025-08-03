"""Comment-aware YARA parser."""

from __future__ import annotations

from typing import TYPE_CHECKING

from yaraast.ast.base import ASTNode, Location, YaraFile
from yaraast.ast.comments import Comment
from yaraast.ast.meta import Meta
from yaraast.lexer import Token, TokenType
from yaraast.lexer.comment_preserving_lexer import CommentPreservingLexer
from yaraast.parser.better_parser import Parser

if TYPE_CHECKING:
    from yaraast.ast.rules import Rule
    from yaraast.ast.strings import StringDefinition


class CommentAwareParser(Parser):
    """Parser that preserves and attaches comments to AST nodes."""

    def __init__(self):
        super().__init__()
        self.pending_comments: list[Comment] = []

    def parse(self, text: str) -> YaraFile:
        """Parse YARA rule text with comment preservation."""
        lexer = CommentPreservingLexer(text)
        self.tokens = lexer.tokenize()
        self.position = 0
        self.text = text

        # Process initial comments
        self._collect_leading_comments()

        yara_file = self._parse_yara_file()

        # Attach any trailing comments
        if self.pending_comments:
            yara_file.trailing_comment = self._make_comment_group()

        return yara_file

    def _current_token(self) -> Token | None:
        """Get current token, skipping comments but collecting them."""
        while self.position < len(self.tokens):
            token = self.tokens[self.position]
            if token.type == TokenType.COMMENT:
                self._collect_comment(token)
                self.position += 1
            else:
                return token
        return None

    def _peek_token(self, offset: int = 1) -> Token | None:
        """Peek at token, handling comments."""
        saved_pos = self.position
        saved_comments = list(self.pending_comments)

        # Skip forward
        for _ in range(offset):
            self._advance()

        token = self._current_token()

        # Restore position and comments
        self.position = saved_pos
        self.pending_comments = saved_comments

        return token

    def _advance(self) -> None:
        """Advance position, collecting comments."""
        if self.position < len(self.tokens):
            if self.tokens[self.position].type != TokenType.COMMENT:
                self.position += 1

            # Collect any comments after advancing
            while (
                self.position < len(self.tokens)
                and self.tokens[self.position].type == TokenType.COMMENT
            ):
                self._collect_comment(self.tokens[self.position])
                self.position += 1

    def _collect_comment(self, token: Token) -> None:
        """Collect a comment token."""
        text = token.value
        is_multiline = text.startswith("/*")

        # Clean comment text
        text = text[2:-2].strip() if is_multiline else text[2:].strip()

        comment = Comment(text=text, is_multiline=is_multiline)
        comment.location = Location(line=token.line, column=token.column)
        self.pending_comments.append(comment)

    def _collect_leading_comments(self) -> None:
        """Collect leading comments before any code."""
        while (
            self.position < len(self.tokens)
            and self.tokens[self.position].type == TokenType.COMMENT
        ):
            self._collect_comment(self.tokens[self.position])
            self.position += 1

    def _attach_comments(self, node: ASTNode) -> None:
        """Attach pending comments to a node."""
        if self.pending_comments:
            node.leading_comments = list(self.pending_comments)
            self.pending_comments.clear()

    def _make_comment_group(self) -> Comment | None:
        """Create a comment from pending comments."""
        if not self.pending_comments:
            return None

        if len(self.pending_comments) == 1:
            return self.pending_comments[0]

        # Combine multiple comments
        combined_text = "\n".join(c.text for c in self.pending_comments)
        comment = Comment(text=combined_text, is_multiline=True)
        if self.pending_comments[0].location:
            comment.location = self.pending_comments[0].location

        return comment

    def _parse_rule(self) -> Rule:
        """Parse rule with comment attachment."""
        rule = super()._parse_rule()

        # Attach any comments that were before the rule
        self._attach_comments(rule)

        return rule

    def _parse_string_definition(self) -> StringDefinition:
        """Parse string definition with comment attachment."""
        string_def = super()._parse_string_definition()

        # Check for inline comment after the string
        if self._current_token() and self._current_token().type == TokenType.COMMENT:
            comment_token = self.tokens[self.position]
            self.position += 1

            comment = Comment(
                text=(
                    comment_token.value[2:].strip()
                    if comment_token.value.startswith("//")
                    else comment_token.value[2:-2].strip()
                ),
                is_multiline=comment_token.value.startswith("/*"),
            )
            comment.location = Location(line=comment_token.line, column=comment_token.column)
            string_def.trailing_comment = comment

        return string_def

    def _parse_meta_statement(self) -> Meta:
        """Parse meta statement with comment attachment."""
        # The better_parser doesn't have _parse_meta_statement
        # We need to implement this ourselves
        key = self._current_token().value
        self._advance()

        if not self._match(TokenType.ASSIGN):
            raise Exception("Expected '=' in meta")

        # Parse value
        if self._match(TokenType.STRING) or self._match(TokenType.INTEGER):
            value = self._previous().value
        elif self._match(TokenType.BOOLEAN_TRUE):
            value = True
        elif self._match(TokenType.BOOLEAN_FALSE):
            value = False
        else:
            raise Exception("Expected meta value")

        meta = Meta(key=key, value=value)

        # Check for inline comment
        if self._current_token() and self._current_token().type == TokenType.COMMENT:
            comment_token = self.tokens[self.position]
            self.position += 1

            comment = Comment(
                text=(
                    comment_token.value[2:].strip()
                    if comment_token.value.startswith("//")
                    else comment_token.value[2:-2].strip()
                ),
                is_multiline=comment_token.value.startswith("/*"),
            )
            comment.location = Location(line=comment_token.line, column=comment_token.column)
            meta.trailing_comment = comment

        return meta
