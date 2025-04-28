import sys
import os
from pathlib import Path
from dotenv import load_dotenv

from llm_client import LLMClient
from compiler import P4Compiler
from logic import check_security

from db import SessionLocal, init_db, Program

load_dotenv()

MAX_RETRIES = os.getenv("MAX_RETRIES", 3)
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
    intent_tag = user_intent.replace(" ", "_")

    prompt_files = [
        "instructions.txt",
        "example1.txt",
        "example2.txt",
        "example3.txt",
        # "final.txt"
    ]

    template = load_prompt_pieces(prompt_files)
    prompt = template.replace("{USER_INTENT}", user_intent)

    llm = LLMClient()
    p4c = P4Compiler()

    compile_failures = 0
    logic_failures = 0
    success = False
    p4_code = ""

    out_dir = Path(__file__).parent.parent / "out"
    out_dir.mkdir(exist_ok=True)

    init_db()
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
            compile_failures += 1

            print("Compile failed with p4c errors:")
            print(compile_feedback)
            print("Looping back with errors…")
            fdbck = template.replace("{USER_INTENT}", user_intent)
            prompt = f"{fdbck}\n# Feedback:\n{compile_feedback}"
            continue

        # second verifier: logic checks
        ok2, logic_feedback = check_security(p4_code)
        if not ok2:
            logic_failures += 1

            print(f"Logic check failed: {logic_feedback}")
            fdbck = template.replace("{USER_INTENT}", user_intent)
            prompt = f"{fdbck}\n# Feedback:\n{logic_feedback}"
            continue

        success=True
        print("PASS: All checks passed")
        return

    session = SessionLocal()
    tags = ["pass"] if success else [f"failed_compile_{compile_failures}", f"failed_logic_{logic_failures}"]
    record = Program(
        intent=intent_tag,
        code=p4_code,
        compile_attempts=compile_failures,
        logic_failures=logic_failures,
        tags=tags
    )
    session.add(record)
    session.commit()
    session.close()

    if not success:
        print("FAIL: Reached max retries without valid P4")


if __name__ == "__main__":
    main()
