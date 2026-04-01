import re

g_content = []
g_cursor_pos = 0
g_cursor_pos_row = 0
g_history = [] 
g_cursor_visible = False 
g_cursor_pos_row_visible = False
g_commands = {} 
g_memory = None

HIGHLIGHT_START = "\033[42m"  
HIGHLIGHT_END = "\033[0m"

def cursor_pos_checker():
    global g_content, g_cursor_pos, g_cursor_pos_row
    if g_cursor_pos_row >= len(g_content):
        g_cursor_pos_row = len(g_content)-1
    elif g_cursor_pos_row < 0:
        g_cursor_pos_row = 0
    for i, line in enumerate(g_content):
        if i == g_cursor_pos_row:
            if g_cursor_pos >= len(line):
                g_cursor_pos = len(line)-1
            elif g_cursor_pos < 0:
                g_cursor_pos = 0
    return g_content, g_cursor_pos, g_cursor_pos_row

def highlight_cursor(line, cursor_pos):
    if line == "" or cursor_pos >= len(line):
        return line
    return (
        line[:cursor_pos]
        + HIGHLIGHT_START + line[cursor_pos] + HIGHLIGHT_END
        + line[cursor_pos + 1:]
    )

def row_marker(index, is_row_visible, cursor_row):
    if is_row_visible:
        return "*" if index == cursor_row else " "
    else:
        return ""

def display_content(content, cursor_pos, text="0"):
    global g_cursor_pos_row, g_cursor_pos, g_content, g_memory
    if g_content != []:
        for i, line in enumerate(g_content):
            prefix = row_marker(i, g_cursor_pos_row_visible, g_cursor_pos_row)
            if i == g_cursor_pos_row and g_cursor_visible:
                print(prefix + highlight_cursor(line, g_cursor_pos))
            else:
                print(prefix + line)
        return content, cursor_pos

def show_content(content, cursor_pos, text):
    return content, cursor_pos

def show_info(content, cursor_pos, text):
    for cmd, (_, desc,_) in g_commands.items():
        print(f"{cmd} - {desc}")
    return content, cursor_pos  

def on_off_cursor(content, cursor_pos, text=''):
    global g_cursor_visible
    g_cursor_visible = not g_cursor_visible  
    return content, cursor_pos 

def on_off_cursor(content, cursor_pos, cursor_pos_row, text=''):
    global g_cursor_visible, g_cursor_pos_row
    g_cursor_visible = not g_cursor_visible  
    return content, cursor_pos, g_cursor_pos_row

def on_off_line_cursor(content, cursor_pos, cursor_pos_row, text=''):
    global g_cursor_pos_row_visible
    g_cursor_pos_row_visible = not g_cursor_pos_row_visible  
    return content, cursor_pos, cursor_pos_row

def move_cursor_left(content, cursor_pos, text):
    return content,cursor_pos - 1

def move_cursor_up(content, cursor_pos, cursor_pos_row, text):
    return g_content, cursor_pos, g_cursor_pos_row - 1

def move_cursor_down(content, cursor_pos, cursor_pos_row, text):
    return g_content, cursor_pos, g_cursor_pos_row+1

def move_cursor_right(content, cursor_pos, text):
    return content, g_cursor_pos+1

def move_cursor_to_beginning_of_the_line(content, cursor_pos, text):
    return content, 0

def move_cursor_end_of_line(content, cursor_pos, text):
    return content, len(content)

def move_to_next_word(content, cursor_pos, text):
    match = re.search(r"\s[a-zA-Z0-9\!\.\"]", content[cursor_pos:])
    if match:
        cursor_pos += match.end()-1
    return content, cursor_pos

def finding_first_letter(content, cursor_pos):
    while cursor_pos >= 0:
        cursor_pos -=1
        snippet = content[cursor_pos:cursor_pos+2]
        if re.match(r"\s\S", snippet):
            break
    return content,cursor_pos+1

def move_to_previous_word(content, cursor_pos, text):
    return finding_first_letter(content, cursor_pos - 2)

def insert_text (content, cursor_pos, text):
    content = content[:cursor_pos] + text + content[cursor_pos:]
    return content, cursor_pos

def append_text (content, cursor_pos, text):
    content = content[:cursor_pos+1] + text + content[cursor_pos+1:]
    return content, cursor_pos+len(text)

def delete_character(content, cursor_pos, text):
    return  content[:cursor_pos] + content[cursor_pos+1:], cursor_pos

def delete_trailing_space(content, cursor_pos):
    end_pos = cursor_pos
    while end_pos < len(content) and content[end_pos].isspace():
        end_pos += 1
    if end_pos > cursor_pos:
        content = content[:cursor_pos] + content[end_pos:]
    return content, cursor_pos
            
def delete_word(content, cursor_pos, text):
    _, cursor_pos_next = move_to_next_word(content, cursor_pos, text)
    if content[cursor_pos].isspace():
        return delete_trailing_space(content, cursor_pos)
    elif cursor_pos_next != cursor_pos:
        content = content[:cursor_pos] + content[cursor_pos_next:]
    else:
        content = content[:cursor_pos]
    return content, cursor_pos

def copy_line(content, cursor_pos, cursor_pos_row, text):
    global g_content, g_memory
    for i, line in enumerate(g_content):
        if i == cursor_pos_row:
            g_memory = line
    return content, cursor_pos, cursor_pos_row

def paste_line_below_cursor(content, cursor_pos, cursor_pos_row, text):
    global g_content, g_cursor_pos, g_cursor_pos_row
    if g_memory != None:
        for i, line in enumerate(g_content):
            if i == cursor_pos_row:
                list_content = list(g_content)
                list_content.insert(cursor_pos_row+1, g_memory)
                g_content = tuple(list_content)
                g_cursor_pos_row = cursor_pos_row + 1
    return g_content, g_cursor_pos, g_cursor_pos_row

def paste_line_above_cursor(content, cursor_pos, cursor_pos_row, text):
    global g_content, g_cursor_pos, g_cursor_pos_row
    if g_memory != None:
        for i, line in enumerate(g_content):
            if i == cursor_pos_row:
                list_content = list(g_content)
                list_content.insert(cursor_pos_row, g_memory)
                g_content = tuple(list_content)
                g_cursor_pos_row = cursor_pos_row
    return g_content, g_cursor_pos, g_cursor_pos_row

def delete_line(content, cursor_pos, cursor_pos_row, text):
    global g_content
    for i, line in enumerate(g_content):
        if i == cursor_pos_row:
            g_content.remove(line)
    return g_content, cursor_pos, cursor_pos_row

def insert_line_below(content, cursor_pos, cursor_pos_row, text):
    global g_content
    g_content.insert(g_cursor_pos_row+1, "")
    return g_content, cursor_pos, cursor_pos_row + 1

def insert_line_above(content, cursor_pos, cursor_pos_row, text):
    global g_content
    g_content.insert(g_cursor_pos_row, "")
    return content, cursor_pos, g_cursor_pos_row

def undo(content, cursor_pos, cursor_pos_row, text):
    global g_history, g_cursor_pos, g_cursor_pos_row, g_cursor_visible, g_cursor_pos_row_visible, g_memory
    if g_history:
        content, cursor_pos, cursor_pos_row, cursor_visible, cursor_visible_row, memory, _, _ = g_history.pop()  # Restore the last state
        g_cursor_visible = cursor_visible
        g_cursor_pos_row_visible = cursor_visible_row
        g_memory = memory
    return content, cursor_pos, cursor_pos_row

def repeat(content, cursor_pos, cursor_pos_row, text):
    if g_history:
        _, _, _, _, _, _, last_cmd, last_text = g_history[-1]
        return execute_command(last_cmd, last_text)
    return content, cursor_pos, cursor_pos_row

def populate_commands():
    global g_commands
    g_commands = {
        "?": (show_info, "display this help info", "one_line"),
        ".": (on_off_cursor, "toggle row cursor on and off", "multiple_line"),
        ";": (on_off_line_cursor, "toggle line cursor on and off", "multiple_line"), 
        "h": (move_cursor_left, "move cursor left", "one_line"),
        "j": (move_cursor_up, "move cursor up", "multiple_line"),
        "k": (move_cursor_down, "move cursor down","multiple_line"),
        "l": (move_cursor_right, "move cursor right", "one_line"),
        "^": (move_cursor_to_beginning_of_the_line, "move cursor to beginning of the line", "one_line"),
        "$": (move_cursor_end_of_line, "move cursor to the end of line", "one_line"),
        "w": (move_to_next_word, "move cursor to beginning of next word", "one_line"),
        "b": (move_to_previous_word, "move cursor to beginning of previous word", "one_line"),
        "i": (insert_text, "insert <text> before cursor", "one_line"),
        "a": (append_text, "append <text> after cursor", "one_line"),
        "x": (delete_character, "delete character at cursor", "one_line"),
        "dw": (delete_word, "delete word and trailing spaces at cursor", "one_line"),
        "yy": (copy_line, "copy current line to memory", "multiple_line"),
        "p": (paste_line_below_cursor, "paste copied line(s) below line cursor", "multiple_line"),
        "P": (paste_line_above_cursor, "paste copied line(s) above line cursor", "multiple_line"),
        "dd": (delete_line, "delete line", "multiple_line"),
        "o": (insert_line_below, "insert empty line below", "multiple_line"),
        "O": (insert_line_above, "insert empty line above", "multiple_line"),
        "u": (undo, "undo previous command", "multiple_line"),
        "r": (repeat, "repeat last command", "multiple_line"),
        "s": (show_content, "show content", "one_line"),
        "q": ("quit", "quit program", "one_line")
    }

def parse_command(input):
    if len(input) > 1 and input[:2] in g_commands:
        return input[:2], input[2:]
    elif len(input) > 0 and input[0] in g_commands:
        return input[0], input[1:]
    else:
        return None, None

def filter_command(cmd, text):
    if cmd in ["i", "a"]:
        if text == "":
            return False
    elif cmd in ["h", "j", "k", "l", "^", "$", "w", "b", "x", "dw", "yy","dd"] and g_content == []:
            return False
    elif cmd == "q":
        return exit()
    else:
        if text != "":
            return False
    return True


def one_line(cmd, text):
    global g_content, g_cursor_pos, g_cursor_pos_row
    if g_content == [] and cmd in ["i", "a","?"]:
        g_content = [""]
    line = g_content[g_cursor_pos_row]
    g_content[g_cursor_pos_row], cursor_pos = g_commands[cmd][0](line, g_cursor_pos, text)
    return g_content, cursor_pos, g_cursor_pos_row


def execute_command(cmd, text):
    global g_content, g_cursor_pos, g_cursor_pos_row, g_history, g_cursor_visible, g_cursor_pos_row_visible, g_memory
    if cmd not in ["u", "r", "?", "s"]:
        content_tuple = tuple(g_content)
        g_history.append((content_tuple, g_cursor_pos, g_cursor_pos_row, g_cursor_visible, g_cursor_pos_row_visible, g_memory, cmd, text))
    g_content = list(g_content)
    if g_commands[cmd][2] == "one_line":
        g_content, g_cursor_pos, g_cursor_pos_row = one_line(cmd, text)
    elif g_commands[cmd][2] == "multiple_line":
        g_content, g_cursor_pos, g_cursor_pos_row = g_commands[cmd][0](g_content, g_cursor_pos, g_cursor_pos_row, text)
    cursor_pos_checker()
    return g_content, g_cursor_pos, g_cursor_pos_row

def process_command(command):
    cmd, text = parse_command(command)
    if filter_command(cmd, text):
        return execute_command(cmd, text)
    else:
        cmd = input(">")
        return process_command(cmd)

    
if __name__ == "__main__":
    populate_commands()
    while True:
        cmd = input(">")
        g_content, g_cursor_pos, g_cursor_pos_row = process_command(cmd)
        if cmd not in ["?"]:
            display_content(g_content, g_cursor_pos)
