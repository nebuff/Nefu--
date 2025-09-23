import sys
import time
import re
import os

class NefuInterpreter:
    def __init__(self, filename):
        self.filename = filename
        self.variables = {}
        self.labels = {}
        self.lines = []
        self.current_line = 0
        self.loop_stack = []
        self.loop_counters = []
        self.loop_limits = []
        self.loop_start_lines = []
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
            line = self.lines[self.current_line].strip()
            if not line or line.startswith('#'):
                self.current_line += 1
                continue
            self.execute_line(line)
            self.current_line += 1

    def execute_line(self, line):
        # Variable assignment
        if re.match(r'.+>!vars/.+!', line):
            value, var = line.split('>!vars/', 1)
            var = var.rstrip('!').strip()
            value = value.strip().strip('"')
            # Try to evaluate as int or float
            try:
                value = eval(value, {}, self.variables)
            except:
                pass
            self.variables[var] = value
            return
        # wait
        if line.startswith('wait '):
            t = line[5:].strip()
            if t.endswith('ms'):
                time.sleep(float(t[:-2])/1000)
            elif t.endswith('s'):
                time.sleep(float(t[:-1]))
            return
        # dsp clear
        if line == 'dsp clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            return
        # goto
        if line.startswith('goto '):
            label = line[5:].strip()
            if label in self.labels:
                self.current_line = self.labels[label]
            return
        # lbl (already handled in parse)
        if line.startswith('lbl '):
            return
        # dsp
        if line.startswith('dsp '):
            content = line[4:].strip()
            if content.startswith('{') and content.endswith('}'):
                content = content[1:-1]
            # Remove surrounding quotes if present (single or double)
            if (content.startswith('"') and content.endswith('"')) or (content.startswith("'") and content.endswith("'")):
                content = content[1:-1]
            # Replace variables
            content = re.sub(r'!vars/(\w+)!', lambda m: str(self.variables.get(m.group(1), '')), content)
            # Inline wait
            content = re.sub(r'\*wait(\d+)s\*', lambda m: (print('', end='', flush=True), time.sleep(int(m.group(1))))[1] or '', content)
            print(content)
            return
        # getinput
        if line.startswith('getinput {'):
            # Read block
            block = []
            i = self.current_line + 1
            while i < len(self.lines) and not self.lines[i].strip().startswith('}'): 
                block.append(self.lines[i].strip())
                i += 1
            prompt = ''
            var = None
            for b in block:
                if b.startswith('dsp '):
                    prompt = b[4:].strip().strip('{}"')
                if '!getinput!>!vars/' in b:
                    var = b.split('!getinput!>!vars/',1)[1].rstrip('!')
            user_input = input(prompt + ' ')
            if var:
                self.variables[var] = user_input
            self.current_line = i
            return
        # repeat
        if line.startswith('repeat '):
            amt = line[7:].strip().split(' ',1)[0]
            block_start = self.current_line + 1
            block = []
            i = block_start
            while i < len(self.lines) and not self.lines[i].strip().startswith('}'): 
                block.append(self.lines[i].strip())
                i += 1
            if amt == '~':
                while True:
                    for b in block:
                        self.execute_line(b)
                        if not self.running:
                            break
                    if not self.running:
                        break
                self.current_line = i
                return
            else:
                # Variable or int
                if amt.startswith('!vars/') and amt.endswith('!'):
                    amt = self.variables.get(amt[6:-1], 0)
                try:
                    amt = int(amt)
                except:
                    amt = 0
                for _ in range(amt):
                    for b in block:
                        self.execute_line(b)
                        if not self.running:
                            break
                    if not self.running:
                        break
                self.current_line = i
                return
        # exit loop
        if line == 'exit loop':
            self.running = False
            return
        # keypress (not implemented in CLI)
        if line.startswith('keypress = '):
            print('[Keypress blocks are not supported in CLI version]')
            return

    @staticmethod
    def main():
        if len(sys.argv) < 2:
            print('Usage: nefu <file.nfu>')
            sys.exit(1)
        filename = sys.argv[1]
        interpreter = NefuInterpreter(filename)
        interpreter.run()

if __name__ == '__main__':
    NefuInterpreter.main()
