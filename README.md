# Nefu Scripting Basics

If you are Interested in more In-Depth Guides go to our Wiki in our Github!

### Install Nefu

If you are on Mac or Debian Linux, Please use Unix 1-Liner

```unix
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/nebuff/Nefu--/main/install.sh)
```
```windows
iex (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/nebuff/Nefu--/main/install.sh')
```

> [!IMPORTANT]
> The script will still prompt the user for installation confirmation, Python installation, and updates.

---

## To-Do
- [x] Create Installer SH
- [ ] Complete Wiki
- [ ] Complete If Statements
- [ ] Add Color Support
- [ ] TUI?
- [ ] Packages (Community can Add Features to Nefu ネフ

---

## Basic Commands

### 1. `dsp` — Display text

The `dsp` command shows text on the screen.

```nefu
# Single line
dsp "Hello, world!"

# Multiple lines
dsp {
    "Welcome to Nefu!"
    "This is version 1.2."
    "Have fun scripting!"
}
```

- Quotes `""` are required around text.
    
- Multiline `dsp { ... }` prints each line separately.
    
- `dsp clear` clears the screen:
    

```nefu
dsp clear
dsp "Screen cleared!"
```

---

### 2. `getinput` — Ask for input

The `getinput` block asks the user to type something.

```nefu
getinput {
    dsp "Enter your name:"
    input
    !getinput!>!vars/name!
}

dsp "Hello!" !vars/name!
```

- `input` indicates where the text will be typed.
    
- `!getinput!>!vars/name!` saves the input into a variable called `name`.
    

You can also put input inline:

```nefu
getinput {
    dsp "Enter your age:" input
    !getinput!>!vars/age!
}
```

---

### 3. Variables

Variables are boxes that hold information.

```nefu
!vars/name! = "Nefu"
dsp "Your name is" !vars/name!
```

- Use `!vars/...!` to access variables.
    
- Variables can be set with `= "value"` or via `getinput`.
    

---

### 4. `wait` — Pause the program

The `wait` command pauses execution for a set time.

```nefu
dsp "Please wait..."
wait 2s
dsp "Done!"
```

- Use `s` for seconds or `ms` for milliseconds.
    

---

### 5. Conditional Statements (`if` / `else`)

You can run code based on conditions:

```nefu
if !vars/age! > 18 {
    dsp "You are an adult."
} else {
    dsp "You are under 18."
}
```

- Supports `=`, `==`, `!=`, `<`, `>`, `<=`, `>=`.
    
- The `else` block is optional.
    
- Conditions can include variables and numbers.
    

---

### 6. Loops (`repeat`)

Run a block of code multiple times.

```nefu
repeat 3 {
    dsp "This runs 3 times"
}
```

- You can also repeat infinitely with `~`:
    

```nefu
repeat ~ {
    dsp "Press Enter to stop"
    keypress = enter
    exit loop
}
```

- Use `exit loop` to break out of an infinite loop.
    

---

### 7. `exit` — Stop the program

```nefu
dsp "Goodbye!"
exit
dsp "This line will not run"
```

- Stops the script immediately.
    

---

### 8. Keypress (`keypress`)

Detect simple key input:

```nefu
keypress = enter   # Waits for Enter
keypress = esc     # Waits for ESC
```

- Only basic keys are supported.
    
- Pressing the required key continues the script.
    

---

## Example Program

This program demonstrates input, variables, conditions, loops, and display:

```nefu
dsp clear
getinput {
    dsp "Enter your name:" input
    !getinput!>!vars/name!
}

dsp "Hello!" !vars/name!

getinput {
    dsp "Enter your age:" input
    !getinput!>!vars/age!
}

if !vars/age! > 18 {
    dsp "You are an adult."
} else {
    dsp "You are under 18."
}

repeat 3 {
    dsp "Counting..." !vars/name!
    wait 1s
}

dsp "End of program."
exit
```

---

### Summary of Features

- `dsp` / `dsp clear` — display text or clear screen
    
- `getinput` — prompt user and store in variable
    
- Variables `!vars/...!` — store and retrieve data
    
- `wait` — pause execution
    
- `if` / `else` — conditional branching
    
- `repeat` — loops (fixed count or infinite)
    
- `exit loop` — break infinite loops
    
- `keypress` — detect Enter or ESC
    
- `exit` — terminate the program
    

This guide covers all the core features of Nefu to build small scripts qui
