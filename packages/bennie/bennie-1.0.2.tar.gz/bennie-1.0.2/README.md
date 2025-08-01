# Bennie

*A Python module for detecting dangling prepositions and other grammatical constructs that your English teacher warned you about.*

## Motivation

This module is dedicated to my mom, an English teacher of 30 years, who would always catch me when I'd end a sentence with a preposition. Bennie helps you identify these constructions - not to judge, but to give you the tools to make informed decisions about what you want to end your sentences with.

## What is it?

Bennie is a modular Python package designed to detect various "dangling" grammatical elements in English text. Currently, it focuses on dangling prepositions, but it's built to expand to other constructs like dangling participles and modifiers.

**Note:** We don't judge here! Sometimes ending with a preposition is perfectly fine and more natural. This tool simply helps you identify these patterns so you can decide what to do about them.

## Installation

```bash
# Install from PyPI
pip install bennie

# Install the required spaCy language model
python -m spacy download en_core_web_sm
```

**Development Installation:**
```bash
# Clone the repository
git clone https://github.com/willwillis/bennie.git
cd bennie

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .

# Install the spaCy model
python -m spacy download en_core_web_sm
```

## Quick Start

```python
from bennie import find_dangling_prepositions

# Test some sentences (with intentional dangling prepositions for irony)
text = "What are you looking at?"
found, sentences = find_dangling_prepositions(text)

if found:
    print("Found dangling prepositions in:")
    for sentence in sentences:
        print(f"  - {sentence}")
```

## Examples

Here are some examples of what Bennie can help you identify:

```python
from bennie import find_dangling_prepositions

test_cases = [
    "What are you looking at?",           # ✓ Dangling preposition detected
    "This is what I was talking about.",  # ✓ Dangling preposition detected  
    "Where did you come from?",           # ✓ Dangling preposition detected
    "She gave the book to him.",          # ✗ No dangling preposition
    "The house that Jack built.",         # ✗ No dangling preposition
]

for text in test_cases:
    found, _ = find_dangling_prepositions(text)
    status = "🔍 Found" if found else "✅ Clean"
    print(f"{status}: {text}")
```

## Testing

Run the test suite to see Bennie in action:

```bash
uv run python run_tests.py
```

## Architecture

Bennie is designed with modularity in mind, making it easy to add new detectors for different grammatical constructs:

```
bennie/
├── __init__.py              # Public interface
├── core.py                  # Shared utilities (spaCy model loading)
└── detectors/
    ├── __init__.py
    ├── prepositions.py      # Dangling preposition detection
    └── (future detectors)   # participles.py, modifiers.py, etc.
```

## Future Plans

- **Dangling Participles**: "Walking down the street, the trees looked beautiful."
- **Dangling Modifiers**: "After eating the sandwich, the park was lovely."
- **Split Infinitives**: "To boldly go where no one has gone before."
- **Custom Rules**: Add your own grammatical pet peeves to catch.

## Technical Details

Bennie uses spaCy's `en_core_web_sm` model for natural language processing. The detection algorithm identifies prepositions (POS tag "ADP") that appear at the end of sentences or clauses without a clear object.

## Contributing

Got a grammatical construct you'd like Bennie to help identify? Contributions are welcome! The modular architecture makes it easy to add new detectors without breaking existing functionality.

## A Note on Prescriptivism vs. Descriptivism

While some grammar rules are more guidelines than absolute laws, this tool exists to help you write with intention. Sometimes ending with a preposition is exactly what you want to do - and that's something this tool won't argue with.

---

*"This is the sort of English up with which I will not put."* - Often attributed to Winston Churchill (though he probably never said it)

Remember: Good writing is about clarity and communication, not following every rule you were taught in school. Use Bennie as a guide, not a judge! 🎓