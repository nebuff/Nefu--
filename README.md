# Nefu Basic Commands
## If you are looking for more Documentation, Look into the Wiki on our Github!
This document covers **basic, foundational commands** in Nefu that are simple to use and appear in almost every program. These are the building blocks for interactivity, output, and control flow, without including more complex features like packages.

---

## 1. `wait`

Pauses program execution for a specified amount of time.

**Syntax:**

```nefu
wait <time>
```

**Parameters:**

- `<time>`: Duration to wait. Examples: `1s` for 1 second, `500ms` for half a second.
    

**Examples:**

```nefu
wait 2s      # Waits for 2 seconds
wait 500ms   # Waits for 0.5 seconds
```

---

## 2. `dsp clear`

Clears the current display or console output.

**Syntax:**

```nefu
dsp clear
```

**Example:**

```nefu
dsp clear
```

---

## 3. `goto`

Jumps to a **label** elsewhere in the program.

**Syntax:**

```nefu
goto <label_name>
```

**Example:**

```nefu
lbl start
# ...some code...
goto start  # jumps back to the 'start' label
```

---

## 4. `lbl`

Defines a **label** to mark a location in the program.

**Syntax:**

```nefu
lbl <label_name>
```

**Example:**

```nefu
lbl math  # creates a label called 'math'
```

---

## 5. `keypress`

Checks if a certain key is pressed. Usually used inside a repeat or input block.

**Syntax:**

```nefu
keypress = <key> {
    # code to run when key is pressed
}
```

**Example:**

```nefu
keypress = enter {
    dsp {"You pressed Enter"}
}
```

---

## 6. `getinput`

Prompts the user for input.

**Syntax:**

```nefu
getinput {
    dsp {"Prompt text"}
    !getinput!>!vars/var_name!
}
```

**Example:**

```nefu
getinput {
    dsp {"Enter your name:"}
    !getinput!>!vars/name!
}
```

---

## 7. Inline commands in `dsp`

Inside a `dsp` block, simple commands like `*wait1s*` can be used to pause or control timing.

**Example:**

```nefu
dsp {
    "Bum"
    *wait1s*
    "Bum"
    *wait1s*
    "Bum"
}
```

---

## 8. `repeat`

Runs a block of code multiple times. The repeat count can be a number, a variable, or infinite.

**Syntax:**

```nefu
repeat <amount> {
    # code to run
}
```

**Examples:**

Repeat 5 times:

```nefu
repeat 5 {
    dsp {"Hello!"}
}
```

Using a variable:

```nefu
!vars/n!>3

repeat !vars/n! {
    dsp {"Looped!"}
}
```

Infinite loop using `~`:

```nefu
repeat ~ {
    dsp {"Running..."}
    wait 1s
}
```

### Exiting Loops

You can exit a loop early using the `exit loop` command. This is useful for keypress handling or conditional breaks.

**Example:**

```nefu
repeat ~ {
    keypress = esc {
        exit loop
    }
    dsp {"Press ESC to exit"}
    wait 500ms
}
```

---

These basic commands form the core of most Nefu programs and allow for simple input, output, pauses, repetition, and program flow control.
