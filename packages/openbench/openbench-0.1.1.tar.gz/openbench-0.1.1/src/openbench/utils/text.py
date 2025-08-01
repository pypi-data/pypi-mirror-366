"""Text processing utilities for openbench.

This module contains helper functions for processing and normalizing text in various
benchmarking contexts, such as cleaning model outputs and standardizing answer formats.
"""


# Adapted from https://github.com/openai/simple-evals
def strip_md_latex(response: str) -> str:
    """
    Strip Markdown and LaTeX formatting artifacts from a model response.

    This is useful when evaluating generated text where visual formatting
    may interfere with exact string matching or scoring logic.

    Parameters:
        response (str): The raw response string potentially containing Markdown or LaTeX syntax.

    Returns:
        str: A cleaned string with Markdown and LaTeX formatting removed.
    """
    return (
        response.replace("**", "")
        .replace("$\\boxed{", "")
        .replace("}$", "")
        .replace("\\$", "")
        .replace("$\\text{", "")
        .replace("$", "")
        .replace("\\mathrm{", "")
        .replace("\\{", "")
        .replace("\\text", "")
        .replace("\\(", "")
        .replace("\\mathbf{", "")
        .replace("{", "")
        .replace("\\boxed", "")
    )


# Adapted from https://github.com/openai/simple-evals
def normalize_mcq_answer(extracted_answer: str) -> str:
    """
    Normalize multiple-choice answer letters to standard Latin A-D format.

    Converts commonly used localized characters (Arabic, Bengali, Japanese)
    representing multiple-choice options to their A-D equivalents. Useful for
    consistent scoring across multilingual datasets.

    Parameters:
        extracted_answer (str): A raw answer string with potential localized MCQ letters.

    Returns:
        str: A normalized answer string using A, B, C, or D.
    """
    return (
        # In Arabic these are the letters used for A-D in multiple choice questions
        extracted_answer.replace("أ", " A")
        .replace("ب", " B")
        .replace("ج", " C")
        .replace("د", " D")
        # In Bengali these are the letters used for A-D in multiple choice questions
        .replace("অ", " A")
        .replace("ব", " B")
        .replace("ড", " C")
        .replace("ঢ", " D")
        # In Japanese these are the letters sometimes used for A-D in multiple choice questions
        .replace("Ａ", " A")
        .replace("Ｂ", " B")
        .replace("Ｃ", " C")
        .replace("Ｄ", " D")
        .strip()
    )


# Adapted from https://github.com/openai/simple-evals
SIMPLE_EVALS_SYSTEM_MESSAGE = "You are a helpful assistant."

# Adapted from https://github.com/openai/simple-evals. Removed the "Think step by step before answering." to make it faster and less leading.
MULTIPLE_CHOICE_PROMPT_TEMPLATE = """
Answer the following multiple choice question. The last line of your response should be of the following format: 'Answer: $LETTER' (without quotes) where LETTER is one of ABCD.

{prompt}

A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}
""".strip()

# Adapted from https://github.com/openai/simple-evals
MULTILINGUAL_ANSWER_PATTERN_TEMPLATE = (
    "(?i){}[ \t]*([A-D]|[أ-د]|[অ]|[ব]|[ড]|[ঢ]|[Ａ]|[Ｂ]|[Ｃ]|[Ｄ])"
)

# All the different ways "Answer" is written in different languages.
# Adapted from https://github.com/openai/simple-evals
MULTILINGUAL_ANSWER_REGEXES = [
    r"Answer\s*:",
    r"Answer\s*:​​​​​​",  # Korean invisible character
    r"উত্তর\s*:",
    r"उत्तर\s*:",
    r"উত্তরঃ",
    r"উত্তর\s*:",
    r"Antwort\s*:",
    r"답변\s*:",
    r"정답\s*:",
    r"답\s*:",
    r"答案\s*：",
    r"答案\s*:",
    r"答\s*：",
    r"答\s*:",
    r"答复\s*：",
    r"答曰\s*：",
    r"الإجابة:",
    r"الجواب:",
    r"إجابة:",
    r"الإجابة النهائية:",
    r"الإجابة الصحيحة:",
    r"الإجابة الصحيحة هي:",
    r"الإجابة هي:",
    r"الجواب النهائي:",
    r"Respuesta\s*:",
    r"Risposta\s*:",
    r"答え\s*:",
    r"答え\s*：",
    r"回答\s*:",
    r"回答\s*：",
    r"解答\s*:",
    r"Jawaban\s*:",
    r"Réponse\s*:",
    r"Resposta\s*:",
    r"Jibu\s*:",
    r"Idahun\s*:",
    r"Ìdáhùn\s*:",
    r"Idáhùn\s*:",
    r"Àmọ̀nà\s*:",
    r"Àdáhùn\s*:",
    r"Ànúgọ\s*:",
    r"Àṣàyàn\s*:",
]

# Adapted from https://github.com/openai/simple-evals
ANSWER_PATTERN_MULTIPLE_CHOICE = r"(?i)Answer[ \t]*:[ \t]*\$?([A-D])\$?"
