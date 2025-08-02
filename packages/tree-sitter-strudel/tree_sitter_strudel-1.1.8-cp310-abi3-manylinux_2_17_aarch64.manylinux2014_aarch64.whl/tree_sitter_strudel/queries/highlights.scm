; ---------------------------------------------------------------------------
;  Strudel syntax-highlighting rules
; ---------------------------------------------------------------------------
;  CAPTURE NAMING
;  1.  Specific > generic – put the most specific patterns first.
;  2.  Use the standard highlight names recognised by tree-sitter-highlight[10].
; ---------------------------------------------------------------------------

; ──────────────────────────────────────────────────────────────────────────
; Keywords
; ──────────────────────────────────────────────────────────────────────────
(identifier)  @variable

((identifier) @function.method
  (#is-not? local)
)

[
  "$:"           ; default assignment prefix
  "var"          ; variable declaration
  "let"
  "const"
] @keyword

; ──────────────────────────────────────────────────────────────────────────
; Punctuation & Delimiters
; ──────────────────────────────────────────────────────────────────────────
[
  "."
  ","
  ":"
  ";"
] @punctuation.delimiter

; Brackets
[
  "("
  ")"
] @punctuation.bracket

[
  "["
  "]"
] @punctuation.bracket

[
  "{"
  "}"
] @punctuation.bracket

; ──────────────────────────────────────────────────────────────────────────
; Arithmetic Operators (Binary Expressions)
; ──────────────────────────────────────────────────────────────────────────
; Capture arithmetic operators from binary expressions
(additive_expression
  operator: _ @operator)

(multiplicative_expression
  operator: _ @operator)

; Alternative approach - directly capture operator literals
"+"              @operator
"-"              @operator
"*"              @operator
"/"              @operator

; ──────────────────────────────────────────────────────────────────────────
; Literals
; ──────────────────────────────────────────────────────────────────────────
(string)         @string
(number)         @number
(comment)        @comment

; ──────────────────────────────────────────────────────────────────────────
; Identifiers (Functions & Vars)
; ──────────────────────────────────────────────────────────────────────────
; 1. Function call identifiers
(function_call
  (identifier)   @function.call)

; 2. Method call identifiers (after the dot)
(method_call
  (identifier)   @function.method)

; 3. Variable declarations: names on the LHS
(variable_declarator
  name: (identifier) @variable)

; 4. Special Strudel function calls
; Core control functions
(function_call
  (identifier) @function.control
  (#any-of? @function.control "setCps" "setCpm" "setTempo" "setBpm"))

; Audio functions (samples and sounds)
(function_call
  (identifier) @function.audio
  (#any-of? @function.audio "samples" "sound" "s" "note" "n" "freq"))

; Pattern generation functions
(function_call
  (identifier) @function.pattern
  (#any-of? @function.pattern "scale" "chord" "pattern" "seq" "sequence" "stack"
    "layer" "cat" "append" "add" "mul" "div" "sub" "fast" "slow" "speed" "iter"
    "every" "sometimes" "rarely" "often" "jux" "juxBy" "rev" "palindrome" "shuffle")
  )

; Effects functions (filters and audio effects)
(function_call
  (identifier) @function.effect
  (#any-of? @function.effect "lpf" "hpf" "bpf" "lpq" "hpq" "bpq" "cutoff" "resonance"
    "filter" "reverb" "rev" "delay" "room" "size" "echo" "phaser" "crush" "coarse"
    "distort" "dist" "vowel" "pan" "gain" "velocity" "attack" "decay" "sustain"
    "release" "adsr")
  )

; Amplitude and envelope functions
(function_call
  (identifier) @function.envelope
  (#any-of? @function.envelope "att" "dec" "sus" "rel" "penv" "lpenv" "hpenv" 
    "bpenv" "tremolo" "am" "compressor"))

; Time manipulation functions
(function_call
  (identifier) @function.time
  (#any-of? @function.time "fast" "slow" "hurry" "linger" "trunc" "mask" "struct" 
    "euclidean" "swing" "late" "early")
  )

; Utility and special functions
(function_call
  (identifier) @function.utility
  (#any-of? @function.utility "silence" "rest" "_" "choose" "choose" "chooseInWith" 
    "range" "run" "scan" "sine" "cosine" "saw" "square" "rand" "perlin")
  )

; MIDI and control functions
(function_call
  (identifier) @function.midi
  (#any-of? @function.midi "midi" "ccv" "ccn" "bend" "program" "bank" "ch" 
    "channel" "polyTouch" "polyAftertouch")
  )

; Sample manipulation functions
(function_call
  (identifier) @function.sample
  (#any-of? @function.sample "begin" "end" "loop" "chop" "striate" "slice" 
    "splice" "speed" "unit" "coarse")
  )

; 5. All remaining identifiers default to variable
(identifier)     @variable

; ──────────────────────────────────────────────────────────────────────────
; Expressions & Chains
; ──────────────────────────────────────────────────────────────────────────
; Highlight the leading identifier of a chained method sequence
(chained_method
  (_
    .
    (identifier) @function.method))

(arrow_function
  parameter: (identifier) @variable.parameter
  body: (expression))

; ──────────────────────────────────────────────────────────────────────────
; Variable Declarations & Assignments
; ──────────────────────────────────────────────────────────────────────────

; Variable declarations: names on the LHS
(variable_declarator
  name: (identifier) @variable)

; Assignment expressions
(assignment
  (identifier) @variable)

; Object property keys
(pair
  key: (identifier) @property)

(pair
  key: (string) @property)

(pair
  key: (number) @property)

; ──────────────────────────────────────────────────────────────────────────
; Expression Context Highlighting
; ──────────────────────────────────────────────────────────────────────────

; Highlight binary expressions for structural context
(binary_expression) @expression

; Specific highlighting for arithmetic expressions
(additive_expression) @expression.arithmetic
(multiplicative_expression) @expression.arithmetic

; ──────────────────────────────────────────────────────────────────────────
; Object and Array Literals
; ──────────────────────────────────────────────────────────────────────────

; Object literals
(object) @constructor

; Array literals
(array) @constructor
