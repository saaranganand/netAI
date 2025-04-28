import sys
from pathlib import Path
from dotenv import load_dotenv

from llm_client import LLMClient
from compiler import P4Compiler
from logic import check_security

load_dotenv()

MAX_RETRIES = 3
PROMPT_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt_pieces(filenames):
    texts = []
    for fname in filenames:
        path = PROMPT_DIR / fname
        if path.exists():
            texts.append(path.read_text())
        else:
            print(f"Prompt file not found: {fname}")
    return "\n\n".join(texts)


def main():
    user_intent = input("Enter your network intent: ").strip().lower()
    if not user_intent:
        print("must type non-empty intent. Exiting")
        sys.exit(1)

    prompt_files = [
        "instructions.txt",
        "example1.txt",
        "example2.txt",
        "example3.txt",
        "final.txt"
    ]

    template = load_prompt_pieces(prompt_files)
    prompt = template.replace("{USER_INTENT}", user_intent)

    llm = LLMClient()
    p4c = P4Compiler()

    out_dir = Path(__file__).parent.parent / "out"
    out_dir.mkdir(exist_ok=True)

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n--- Attempt {attempt}: asking LLM… ---")
        try:
            p4_code = llm.generate(prompt)

            p4_code = (
                p4_code
                .replace("{{", "{")
                .replace("}}", "}")
            )
        except Exception as e:
            print(f"LLM generation error: {e}")
            break

        # write P4 code to file
        p4_file = out_dir / "program.p4"
        p4_file.write_text(p4_code)

        # first verifier: compilation
        ok, compile_feedback = p4c.compile(str(p4_file))
        if not ok:
            print("Compile failed, looping back with errors…")
            fdbck = template.replace("{USER_INTENT}", user_intent)
            prompt = f"{fdbck}\n# Feedback:\n{compile_feedback}"
            continue

        # second verifier: logic checks
        ok2, logic_feedback = check_security(p4_code)
        if not ok2:
            print(f"Logic check failed: {logic_feedback}")
            fdbck = template.replace("{USER_INTENT}", user_intent)
            prompt = f"{fdbck}\n# Feedback:\n{logic_feedback}"
            continue

        print("PASS: All checks passed")
        return

    print("FAIL: Reached max retries without valid P4")


if __name__ == "__main__":
    main()
