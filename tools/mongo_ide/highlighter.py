import re
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor

class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []
        
        # Strings/Keys
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#ce9178"))
        self.rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#b5cea8"))
        self.rules.append((re.compile(r"\b-?\d+(\.\d*)?([eE][+-]?\d+)?\b"), number_format))
        
        # Booleans and Null
        bool_format = QTextCharFormat()
        bool_format.setForeground(QColor("#569cd6"))
        for word in ["true", "false", "null"]:
            self.rules.append((re.compile(rf"\b{word}\b"), bool_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)
