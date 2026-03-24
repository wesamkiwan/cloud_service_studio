import re
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont

class SqlHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569cd6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES", "UPDATE", "SET",
            "DELETE", "CREATE", "DROP", "TABLE", "INDEX", "VIEW", "GRANT", "REVOKE",
            "COMMIT", "ROLLBACK", "AND", "OR", "NOT", "AS", "INNER", "LEFT", "RIGHT",
            "OUTER", "JOIN", "ON", "ORDER BY", "GROUP BY", "HAVING", "LIMIT", "OFFSET",
            "ASC", "DESC"
        ]
        
        # Create regex pattern for keywords. \b matches word boundaries.
        for keyword in keywords:
            pattern = re.compile(rf"\b{keyword}\b", re.IGNORECASE)
            self.rules.append((pattern, keyword_format))
            
        # Strings (Single Quotes)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#ce9178"))
        self.rules.append((re.compile(r"'[^']*'"), string_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#b5cea8"))
        self.rules.append((re.compile(r"\b\d+(\.\d+)?\b"), number_format))
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6a9955"))
        self.rules.append((re.compile(r"--[^\n]*"), comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)
