import io
import os
import tempfile

import pycodestyle
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from editorWidgetTool.tools.dictionary import pyDictionary
pythonKeywords = [
    'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else',
    'except', 'False', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'None',
    'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'True', 'try', 'while', 'with', 'yield', ',']

predefinedFunctionNames = ['abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes', 'callable',
                           'chr', 'classmethod', 'compile', 'complex', 'delattr', 'dict', 'dir', 'divmod', 'enumerate',
                           'eval', 'exec', 'filter', 'float', 'format', 'frozenset', 'getattr', 'globals', 'hasattr',
                           'hash', 'help', 'hex', 'id', 'input', 'int', 'isinstance', 'issubclass', 'iter', 'len',
                           'list', 'locals', 'map', 'max', 'memoryview', 'min', 'next', 'object', 'oct', 'open', 'ord',
                           'pow', 'print', 'property', 'range', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
                           'sorted', 'staticmethod', 'str', 'sum', 'tuple', 'type', 'vars', 'zip']

classFunction = ['__init__', '__del__', '__repr__', '__str__', '__cmp__', '__call__', '__len__', '__getitem__', '__setitem__', '__delitem__',
                    '__iter__', '__contains__', '__getslice__', '__setslice__', '__delslice__', '__add__', '__sub__', '__mul__', '__div__', '__mod__',
                    '__pow__', '__lshift__', '__rshift__', '__and__', '__xor__', '__or__', '__iadd__', '__isub__', '__imul__', '__idiv__', '__imod__',
                    '__ipow__', '__ilshift__', '__irshift__', '__iand__', '__ixor__', '__ior__', '__neg__', '__pos__', '__abs__', '__invert__',
                    '__complex__', '__int__', '__long__', '__float__', '__oct__', '__hex__', '__index__', '__coerce__', '__enter__', '__exit__']

decorators = ['@staticmethod', '@classmethod', '@property']

mathFunction = ['acos', 'acosh', 'asin', 'asinh', 'atan', 'atan2', 'atanh', 'ceil', 'copysign', 'cos', 'cosh', 'degrees', 'e', 'erf', 'erfc',
                'exp', 'expm1', 'fabs', 'factorial', 'floor', 'fmod', 'frexp', 'fsum', 'gamma', 'hypot', 'inf', 'isclose', 'isfinite', 'isinf',
                'isnan', 'ldexp', 'lgamma', 'log', 'log10', 'log1p', 'log2', 'modf', 'nan', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan',
                'tanh', 'tau', 'trunc']

operators = [
    '=',
    # Comparison
    '==', '!=', '<', '<=', '>', '>=',
    # Arithmetic
    '\+', '-', '\*', '/', '//', '\%', '\*\*',
    # In-place
    '\+=', '-=', '\*=', '/=', '\%=',
    # Bitwise
    '\^', '\|', '\&', '\~', '>>', '<<',
]

braces = [
    '\{', '\}', '\(', '\)', '\[', '\]',
]


class pythonHighLighter(QSyntaxHighlighter):
    keywordColor: QColor = QColor(255, 91, 0, 255)
    functionColor: QColor = QColor(178, 101, 100, 255)
    builtInColor: QColor = QColor(233, 118, 51, 255)
    # color melanzana
    selfColor: QColor = QColor(191, 0, 127, 255)
    classFunctionColor: QColor = QColor(239, 0, 159, 255)
    methodColor: QColor = QColor(220, 158, 0, 255)
    braceColor: QColor = QColor(200, 200, 200, 255)
    numberColor: QColor = QColor(103, 151, 187, 255)
    stringColor: QColor = QColor(99, 99, 181, 255)
    commentColor: QColor = QColor(113, 128, 147, 255)  # grigio bluastro
    comment2Color: QColor = QColor(113, 128, 147)  # grigio bluastro
    operatorColor: QColor = QColor(255, 255, 255)  # bianco
    identifierColor: QColor = QColor(255, 255, 255)  # bianco
    commentLineColor: QColor = QColor(113, 128, 147)  # grigio bluastro
    commentDocColor: QColor = QColor(113, 128, 147)  # grigio bluastro
    commentDocKeywordColor: QColor = QColor(255, 195, 0)  # giallo dorato
    errorColor: QColor = QColor(255, 0, 0)  # rosso
    pepColor: QColor = QColor(40, 100, 40)  # verde

    def __init__(self, document, editor):
        super().__init__(document)
        self.document = document
        self.editor = editor
        self.rules = []
        self.errorUnderline = QTextCharFormat()
        self.errorUnderline.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)
        self.pythonPatternRules()

    def pythonPatternRules(self):
        self.rules = []
        self.rules += [(r'\b%s\b' % w, 0, self.keywordColor) for w in pythonKeywords]
        # se la parola è "self" è di un colore diverso
        self.rules += [(r'\b%s\b' % w, 0, self.selfColor) for w in ['self']]

        self.rules += [(r'\b%s\b' % w, 0, self.functionColor) for w in predefinedFunctionNames]
        # se una parola è preceduta da def o class e non è in classFunction allora è un metodo
        self.rules += [(r'\bdef\b\s*(\w+)', 1, self.methodColor)]
        self.rules += [(r'\b%s\b' % w, 0, self.classFunctionColor) for w in classFunction]
        self.rules += [(f'{b}', 0, self.braceColor) for b in braces]
        self.rules += [(f'{o}', 0, self.operatorColor) for o in operators]

        self.rules += [(r'\b[+-]?[0-9]+[lL]?\b', 0, self.numberColor),
                       (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, self.numberColor),
                       (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, self.numberColor),
                       (r'\".*\"', 0, self.stringColor), (r'\"\"\".*\"\"\"', 0, self.stringColor),
                       (r'\'.*\'', 0, self.stringColor), (r'\'\'\'.*\'\'\'', 0, self.stringColor),
                       (r'#.*$', 0, self.commentColor), (r'#.*$', 0, self.comment2Color),
                       (r'#.*$', 0, self.commentLineColor), (r'#.*$', 0, self.commentDocColor),
                       (r'#.*$', 0, self.commentDocKeywordColor), (r'#.*$', 0, self.commentColor)]

    def highlightBlock(self, text):
        """
        Fa gli highlight del testo in base alle regole definite in self.rules
        :param text:
        :return:
        """
        wordList = []
        for pattern, index, color in self.rules:
            expression = QRegularExpression(pattern)
            iterator = expression.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                wordList.append(match.captured(index))
                self.setFormat(match.capturedStart(index), match.capturedLength(index), color)

    def setColor(self, color: QColor, colorName: str):
        print(f"change in color {colorName} to {color.name()}")
        if colorName == "keywordColor":
            self.keywordColor = color
        elif colorName == "functionColor":
            self.functionColor = color
        elif colorName == "builtInColor":
            self.builtInColor = color
        elif colorName == "selfColor":
            self.selfColor = color

        self.pythonPatternRules()

    def setKeywordColor(self, color: QColor):
        self.keywordColor = color
        self.pythonPatternRules()

    def setFunctionColor(self, color: QColor):
        self.functionColor = color
        self.pythonPatternRules()

    def setBuiltInColor(self, color: QColor):
        self.builtInColor = color
        self.pythonPatternRules()

