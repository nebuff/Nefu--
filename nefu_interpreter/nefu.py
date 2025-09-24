# 0.5 Alpha Nefu Interpreter with choice support

import sys
import time
import re
import os
import platform

if platform.system() != "Windows":
    import curses
else:
    import msvcrt

class LoopBreakException(Exception):
    pass

class NefuInterpreter:
    def __init__(self, filename):
        self.filename = filename
        self.variables = {}
        self.labels = {}
        self.lines = []
        self.current_line = 0
        self.running = True

    def parse_file(self):
        with open(self.filename, encoding='utf-8') as f:
            self.lines = [line.rstrip('\n') for line in f]
        # Preprocess labels
        for idx, line in enumerate(self.lines):
            if line.strip().startswith('lbl '):
                label = line.strip().split(' ', 1)[1]
                self.labels[label] = idx

    def run(self):
        self.parse_file()
        self.current_line = 0
        while self.current_line < len(self.lines) and self.running:
            raw_line = self.lines[self.current_line]
            line = raw_line.strip()
            if not line or line.startswith('#'):
                self.current_line += 1
                continue
            try:
                self.execute_line(line)
            except Exception as e:
                print(f"\n[ERROR] Line {self.current_line+1}: {raw_line}")
                print(f"        {e}")
                self.running = False
                return
            self.current_line += 1

    def substitute_vars(self, text):
        return re.sub(r'!vars/(\w+)!', lambda m: str(self.variables.get(m.group(1), '')), text)

    def strip_quotes(self, text):
        text = text.strip()
        if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
            return text[1:-1]
        return text

    def eval_condition(self, cond):
        cond = self.substitute_vars(cond).strip()
        m = re.match(r'(.+?)\s*(==|=|!=|<=|>=|<|>)\s*(.+)', cond)
        if m:
            left, op, right = m.groups()
            left = self.strip_quotes(left.strip())
            right = self.strip_quotes(right.strip())
            try:
                left_val = float(left)
                right_val = float(right)
            except:
                left_val, right_val = left, right
            if op in ("=", "=="): return left_val == right_val
            if op == "!=": return left_val != right_val
            if op == "<": return left_val < right_val
            if op == ">": return left_val > right_val
            if op == "<=": return left_val <= right_val
            if op == ">=": return left_val >= right_val
        return cond.lower() == "true"

    def find_matching_closing(self, start_index):
        depth = 1
        i = start_index
        while i < len(self.lines):
            l = self.lines[i].strip()
            if '{' in l: depth += l.count('{')
            if '}' in l:
                depth -= l.count('}')
                if depth == 0:
                    return i
            i += 1
        raise Exception("Missing closing '}' for block")

    def run_block(self, start_idx, end_idx):
        saved_current = self.current_line
        i = start_idx
        while i < end_idx:
            self.current_line = i
            line = self.lines[i].strip()
            if not line or line.startswith('#'):
                i += 1
                continue
            prev_current = self.current_line
            self.execute_line(line)
            if self.current_line == prev_current:
                i = prev_current + 1
            else:
                i = self.current_line + 1
        self.current_line = saved_current

    # New: TUI choice menu
    def handle_choice(self, title, options):
        if platform.system() == "Windows":
            selected = 0
            while True:
                os.system('cls')
                print(f":{title}")
                for i, opt in enumerate(options):
                    prefix = "→ " if i == selected else "  "
                    print(f"{prefix}{opt}")
                key = msvcrt.getch()
                if key == b'\xe0':
                    key2 = msvcrt.getch()
                    if key2 == b'H': selected = (selected - 1) % len(options)
                    elif key2 == b'P': selected = (selected + 1) % len(options)
                elif key == b'\r':
                    return selected
        else:
            def _curses_choice(stdscr):
                curses.curs_set(0)
                selected = 0
                while True:
                    stdscr.clear()
                    stdscr.addstr(f":{title}\n")
                    for i, opt in enumerate(options):
                        if i == selected:
                            stdscr.addstr(f"> {opt}\n", curses.A_REVERSE)
                        else:
                            stdscr.addstr(f"  {opt}\n")
                    key = stdscr.getch()
                    if key == curses.KEY_UP: selected = (selected - 1) % len(options)
                    elif key == curses.KEY_DOWN: selected = (selected + 1) % len(options)
                    elif key in (10, 13): return selected
            selected = curses.wrapper(_curses_choice)
        return selected

    def execute_line(self, line):
        if line == "}": return
        if '>!vars/' in line:
            value, var = line.split('>!vars/', 1)
            var = var.rstrip('!').strip()
            value = self.substitute_vars(value.strip())
            self.variables[var] = self.strip_quotes(value)
            return
        if line.startswith('wait '):
            t = line[5:].strip()
            if t.endswith('ms'): time.sleep(float(t[:-2])/1000.0)
            elif t.endswith('s'): time.sleep(float(t[:-1]))
            else: raise Exception(f"Invalid wait duration: {t}")
            return
        if line == 'dsp clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            return
        if line.startswith('goto '):
            label = line[5:].strip()
            if label in self.labels: self.current_line = self.labels[label]; return
            else: raise Exception(f"Unknown label: {label}")
        if line.startswith('lbl '): return
        if line.startswith('dsp '):
            content = line[4:].strip()
            if content.startswith('{'):
                block_start = self.current_line + 1
                block_end = self.find_matching_closing(block_start)
                for i in range(block_start, block_end):
                    l = self.strip_quotes(self.substitute_vars(self.lines[i].strip()))
                    print(l)
                self.current_line = block_end
                return
            else:
                parts = re.findall(r'"[^"]*"|\'[^\']*\'|!vars/\w+!', content)
                if not parts:
                    out = self.strip_quotes(self.substitute_vars(content))
                    print(out)
                    return
                line_out = ''
                for p in parts:
                    if p.startswith('!vars/'):
                        var_name = p[6:-1]
                        line_out += str(self.variables.get(var_name, ''))
                    else:
                        line_out += self.strip_quotes(p)
                print(line_out)
                return
        if line.startswith('getinput'):
            block_start = self.current_line + 1
            block_end = self.find_matching_closing(block_start)
            prompt_lines = []
            var = None
            input_inline = False
            for i in range(block_start, block_end):
                b = self.lines[i].strip()
                if b.startswith('dsp '):
                    content = b[4:].strip()
                    if content.endswith(' input'):
                        input_inline = True
                        content = content[:-6].strip()
                    prompt_lines.append(self.strip_quotes(self.substitute_vars(content)))
                if '!getinput!>!vars/' in b:
                    var = b.split('!getinput!>!vars/',1)[1].rstrip('!')
            if input_inline:
                prompt = ' '.join(prompt_lines)
                user_input = input(prompt + ' ')
            else:
                for pl in prompt_lines: print(pl)
                user_input = input()
            if var: self.variables[var] = user_input
            self.current_line = block_end
            return
        # New: choice command
        if line.startswith('choice '):
            m = re.match(r'choice title=(["\'])(.*?)\1\s*{', line)
            if not m: raise Exception("Malformed choice syntax")
            title = m.group(2)
            block_start = self.current_line + 1
            block_end = self.find_matching_closing(block_start)
            options = []
            for i in range(block_start, block_end):
                l = self.lines[i].strip()
                if re.match(r'\d+\)', l): options.append(l.split(')',1)[1].strip())
            selected_index = self.handle_choice(title, options)
            self.variables["choice_selected"] = str(selected_index)
            self.current_line = block_end
            return
        if line.startswith('if '):
            cond_text = None
            if line.endswith('{'):
                cond_text = line[3:-1].strip()
                block_start = self.current_line + 1
            else:
                next_idx = self.current_line + 1
                if next_idx < len(self.lines) and self.lines[next_idx].strip().startswith('{'):
                    cond_text = line[3:].strip()
                    block_start = next_idx + 1
                else: raise Exception("Malformed if: missing '{'")
            block_end_idx = self.find_matching_closing(block_start)
            cond_true = self.eval_condition(cond_text)
            if cond_true:
                self.run_block(block_start, block_end_idx)
                self.current_line = block_end_idx
                after_else_idx = block_end_idx + 1
                if after_else_idx < len(self.lines):
                    next_line = self.lines[after_else_idx].strip()
                    if next_line.startswith('else'):
                        if next_line.endswith('{'): else_block_start = after_else_idx + 1
                        else: else_block_start = after_else_idx + 2
                        else_block_end = self.find_matching_closing(else_block_start)
                        self.current_line = else_block_end
                return
            else:
                after_else_idx = block_end_idx + 1
                if after_else_idx < len(self.lines):
                    next_line = self.lines[after_else_idx].strip()
                    if next_line.startswith('else'):
                        if next_line.endswith('{'): else_block_start = after_else_idx + 1
                        else: else_block_start = after_else_idx + 2
                        else_block_end = self.find_matching_closing(else_block_start)
                        self.run_block(else_block_start, else_block_end)
                        self.current_line = else_block_end
                        return
                self.current_line = block_end_idx
                return
        if line.startswith('repeat '):
            count = line[7:].strip()
            block_start = self.current_line + 1
            block_end = self.find_matching_closing(block_start)
            if count == "~":
                try:
                    while True: self.run_block(block_start, block_end)
                except LoopBreakException: pass
                self.current_line = block_end
                return
            else:
                try: times = int(count)
                except: raise Exception(f"Invalid repeat count: {count}")
                for _ in range(times):
                    try: self.run_block(block_start, block_end)
                    except LoopBreakException: break
                self.current_line = block_end
                return
        if line == "exit": self.running = False; return
        if line.startswith('else'): return
        raise Exception(f"Unknown command: {line}")

def main():
    if len(sys.argv) < 2:
        print('Usage: nefu <file.nfu>')
        sys.exit(1)
    filename = sys.argv[1]
    interpreter = NefuInterpreter(filename)
    interpreter.run()

if __name__ == '__main__':
    main()
