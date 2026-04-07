#!/data/data/com.termux/files/usr/bin/python
import os
import sys
from pathlib import Path


def fix_python_indentation(input_file_path, output_file_path=None, indent_size=4):
    if not os.path.exists(input_file_path):
        print(f"خطا: فایل ورودی یافت نشد: {input_file_path}")
        return False
    fixed_lines = []
    current_indent_level = 0
    # لیست کلماتی که شروع یک بلوک جدید را نشان می‌دهند و به تورفتگی نیاز دارند
    block_starters = ["def", "class", "if", "for", "while", "with", "try", "except", "finally", "elif", "else"]
    block_enders = ["return", "break", "continue", "pass", "raise"]
    with open(input_file_path, encoding="utf-8") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if not stripped_line:
            fixed_lines.append("\n")
            continue
        if any(stripped_line.startswith(end_word) for end_word in block_enders) and current_indent_level > 0:
            if i > 0 and not lines[i - 1].strip().endswith(":"):  # اگر خط قبلی پایان بلوک نباشد
                current_indent_level = max(0, current_indent_level - 1)
        fixed_lines.append(" " * (current_indent_level * indent_size) + stripped_line + "\n")
        if stripped_line.endswith(":"):
            first_word = stripped_line.split(" ")[0]
            if first_word in block_starters or (first_word == "lambda" and ":" in stripped_line):  # برای lambda
                current_indent_level += 1
        if stripped_line.startswith(("elif", "else")):
            pass
    final_output_path = output_file_path or input_file_path
    try:
        with open(final_output_path, "w", encoding="utf-8") as f:
            f.writelines(fixed_lines)
        print(f"فایل با موفقیت اصلاح شد: {final_output_path}")
        return True
    except OSError as e:
        print(f"خطا در نوشتن فایل خروجی: {e}")
        return False


if __name__ == "__main__":
    inf = Path(sys.argv[1])
    outf = inf.with_stem(inf.stem + "_fixed")
    if not fix_python_indentation(inf, outf):
        print("اصلاح فایل با خطا مواجه شد.")
