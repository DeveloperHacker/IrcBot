import re
from teach_file import keys

white = "00"
black = "01"
blue = "02"
green = "03"
red = "04"
brown = "05"
purple = "06"
orange = "07"
yellow = "08"
light_green = "09"
cyan = "10"
dark_green = "11"
dark_blue = "12"
magenta = "13"
dark_gray = "14"
gray = "15"
empty = ""

bold = ""
italics = ""
underlined = ""

c_str = [green + bold, bold + empty]
c_digits = [yellow, empty]
c_symbols = [orange, empty]
c_first = [blue, empty]
c_second = [blue + bold, bold + empty]
c_third = [magenta + bold, bold + empty]

first = {
    "char",
    "character",
    "str",
    "string",
    "byte",
    "list",
    "int",
    "integer",
    "bool",
    "boolean",
    "short",
    "float",
    "double"
}

second = {
    "def",
    "fn",
    "if",
    "else",
    "elif",
    "then",
    "end"
    "not",
    "in",
    "is",
    "as",
    "for",
    "while",
    "return",
    "true",
    "false",
    "none",
    "local",
    "until",
    "function",
    "repeat",
    "then",
    "end"
}

third = {
    "self",
    "this"
}


class Brain:
    @staticmethod
    def get_tags(text: str):
        text = text.lower()
        tokens = Brain.broke_string(text)
        found = {}
        for tag, collocations in keys.items():
            for collocation, key in collocations:
                if key == "regexp" and re.search(".*\s.*".join(collocation), text) is not None:
                    if tag not in found: found[tag] = 0
                    found[tag] += 1
                if key == "word":
                    cur = 0
                    for token in tokens:
                        if token == collocation[cur]: cur += 1
                        if cur == len(collocation): break
                    if cur == len(collocation):
                        if tag not in found: found[tag] = 0
                        found[tag] += 1
        return found

    @staticmethod
    def get_args(text: str, meaning: str):
        tokens = Brain.broke_string(text)
        if meaning == "in": return [token for i, token in enumerate(tokens) if i > 0 and tokens[i - 1] in ["in", "в"]]
        if meaning == "description":
            right = None
            for i, ch in reversed(list(enumerate(text))):
                if right is None and ch == '"':
                    right = i
                    break
            tmp = re.findall(r":\s+\"", text)
            left = text.index(tmp[0]) + len(tmp[0]) if tmp else None
            if right and left and right > left: return text[left: right]
        return None

    @staticmethod
    def get_dst(string: str, names: set) -> list:
        names = {name.lower() for name in names}
        string = string.lower()
        tokens = Brain.broke_string(string)
        if len(tokens) <= 1: return set()
        result = set()
        for i, token in enumerate(tokens):
            left = (i == 0 or tokens[i - 1] in {",", "."})
            right = (i == len(tokens) - 1 or tokens[i + 1] in {".", ";", ",", ":", "!"})
            if left and right and token in names: result.add(token)
        if tokens[0] in names: result.add(tokens[0])
        if tokens[-1] in names: result.add(tokens[-1])
        return result

    @staticmethod
    def broke_string(string: str) -> list:
        tokens = [x for x in re.split(r"(?:\s+|([:,!?\'\"]))", string) if x]
        return tokens

    @staticmethod
    def clear_string(string: str) -> str:
        skip = 0
        result = []
        for ch in string:
            if ch.isdigit() and skip > 0:
                skip -= 1
                continue
            if ch == empty:
                skip = 2
                continue
            if ch in {bold, italics, underlined}: continue
            skip = 0
            result.append(ch)
        return "".join(result)

    @staticmethod
    def clear_text(text: list) -> list:
        return [Brain.clear_string(line) for line in text]

    @staticmethod
    def format_text(text: list):
        if len(text) == 0: return []
        text = "\\n".join(text)
        lines = [[]]
        token = ""
        spaces = 0
        in_str = False
        left_quote = None
        for ch in text:
            token += ch
            if ch == '\\' and token == '\\': continue
            if not in_str and token == '"' or token == '\'':
                in_str = True
                left_quote = token
            elif in_str and token == left_quote:
                in_str = False
                left_quote = None
            if not in_str:
                if token == " ":
                    spaces += 1
                elif token == "\\n":
                    lines.append([])
                    spaces = 0
                else:
                    if spaces >= 4: lines.append([' ' for i in range(0, spaces)])
                    spaces = 0
            lines[-1].append(token)
            token = ''
        lines_tmp = []
        for line in lines:
            line_tmp = []
            right = True
            for ch in reversed(line):
                if ch != ' ': right = False
                if not right: line_tmp.append(ch)
            line = [ch for ch in reversed(line_tmp)]
            if len(line) > 0 and line[0] == "\\n":
                line = line[1:]
                if len(line) == 0: continue
            lines_tmp.append(line)
        lines = lines_tmp
        return ["".join(line) for line in lines]

    @staticmethod
    def paint_text(text: list):
        if len(text) == 0: return []
        text = "\n".join(text)
        text += " "
        lines = [[empty]]
        token = ""
        word = ""
        in_str = False
        left_quote = None
        for ch in text:
            token += ch
            if ch == '\\' and token == '\\': continue
            if not in_str and token == '"' or token == '\'':
                in_str = True
                left_quote = token
                lines[-1].append(c_str[0])
            elif in_str and token == left_quote:
                in_str = False
                left_quote = None
            if in_str:
                lines[-1].append(token)
            else:
                word += token
                if not token.isalpha() and not token.isnumeric() and token != '_':
                    k_word = word[:-1]
                    t_word = k_word.lower()
                    if t_word in first:
                        lines[-1].extend([c_first[0], k_word, c_first[1]])
                    elif t_word in second:
                        lines[-1].extend([c_second[0], k_word, c_second[1]])
                    elif t_word in third:
                        lines[-1].extend([c_third[0], k_word, c_third[1]])
                    elif t_word.isnumeric():
                        lines[-1].extend([c_digits[0], k_word, c_digits[1]])
                    else:
                        lines[-1].extend(k_word)
                    if not token.isspace() and not token.isdigit() and not token.isalpha() \
                            and token not in ['\'', '"', '(', '{', '[', ']', '}', ')']:
                        lines[-1].extend([c_symbols[0], token, c_symbols[1]])
                    else:
                        if token == "\n": lines.append([empty])
                        else: lines[-1].append(token)
                    word = ""
            if not in_str and token == '"' or token == '\'': lines[-1].append(c_str[1])
            token = ''
        return ["".join(line) for line in lines]
