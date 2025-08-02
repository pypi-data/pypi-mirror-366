# zenofai/verbose.py

VERBOSE_ZEN = """\
The Zen of GenAI (Verbose Edition)
by Anuj Sadani

1. Clarity of intent is better than volume of output.
   — Define your goal precisely; a targeted, concise result is more valuable than pages of unfocused code.

2. Prompt with purpose—lazy prompting leads to lazy outcome.
   — Thoughtful, well-structured prompts guide the AI to generate meaningful solutions; vague or hasty prompts produce shallow or irrelevant results.

3. Verify relentlessly—AI can hallucinate; your tests should not.
   — Always write and run tests, review edge cases, and validate assumptions. Don’t accept AI output at face value.

4. Human judgment is irreplaceable.
   — AI can suggest options, but decisions about design, security, ethics, and fit must remain with you.

5. Transparency is a powerful ally.
   — Use tools or techniques that expose how the AI reached its suggestions. Understanding the rationale helps debug, improve, and trust the code.

6. Readability counts, especially in generated code.
   — Prioritize clear naming, consistent style, and simple structure so that anyone (including future you) can understand and maintain the AI’s output.

7. Refactor good ideas rather than reinventing vague ones.
   — When AI offers improvements or cleanups, integrate them into existing code; avoid generating entirely new, unvetted implementations.

8. Reuse wisdom, not just code.
   — Learn patterns, idioms, and best practices from AI suggestions. Don’t copy blindly—understand and adapt.

9. Every suggestion deserves scrutiny—trust is earned, even by models.
   — Critically review each line of AI-generated code for correctness, performance implications, and security risks.

10. Errors should never be silently ignored unless explicitly understood and accepted.
    — Log, handle, or escalate exceptions. If you suppress an error, document why doing so is safe.

11. If code is hard for a human to explain, it’s a bad idea.
    — Maintain the ability to articulate what each function and module does. Complex or opaque AI output often hides brittle logic.

12. If code is easy for a human to explain, it may be a good idea.
    — Favor straightforward implementations where the rationale and flow are clear, even if they’re more verbose.

13. In deterministic tasks, keep the temperature zero.
    — For reproducible results—such as SQL generation, configuration files, or critical algorithms—configure the AI to produce consistent outputs.

14. Let code be the documentation.
    — Strive for self-explanatory code with meaningful names and structure. Avoid comments that merely restate the code or bloat the implementation.

15. Bias compounds—challenge familiar patterns.
    — Detect and question repetitive or biased suggestions inherited from training data. Ensure your code reflects your domain needs, not AI defaults.

16. The best output is the one you truly understand.
    — Only integrate AI-generated code after you can trace its logic, justify its existence, and foresee its behavior under different conditions.
"""

print(VERBOSE_ZEN)
