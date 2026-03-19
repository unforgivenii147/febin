#!/data/data/com.termux/files/usr/bin/python
import ast
import io
import shutil
import tempfile
import tokenize
from multiprocessing import Pool
from pathlib import Path

import regex as re
from deep_translator import GoogleTranslator
from fastwalk import walk_files

DIRECTORY = "."
non_english_pattern = re.compile(r"[^\x00-\x7F]")


def is_english(text: str) -> bool:
    return not non_english_pattern.search(text)


def chunk_text(text: str, size: int = 800) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size)]


def translate_chunk(chunk: str) -> str:
    try:
        result = GoogleTranslator(source="auto", target="en").translate(chunk)
        return result if result else chunk
    except Exception as e:
        print(f"  Translation error for chunk: {e}")
        return chunk


def translate_text(text: str) -> str:
    chunks = chunk_text(text)
    with Pool(8) as pool:
        translated = list(pool.imap(translate_chunk, chunks))
    return "".join(translated)


def safe_overwrite(filepath: Path, content: str) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        delete=False,
        dir=filepath.parent,
    ) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    shutil.move(tmp_path, filepath)


def extract_docstrings(
    tree: ast.AST,
) -> dict[int, str]:
    docstrings = {}
    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.Module,
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):
            doc = ast.get_docstring(node, clean=False)
            if doc and not is_english(doc):
                docstrings[id(node)] = doc
    return docstrings


def translate_python_file(source: str, filepath: Path) -> str:
    print("  Analyzing Python structure...")
    tree = ast.parse(source)
    docstrings = extract_docstrings(tree)
    if docstrings:
        print(f"  Found {len(docstrings)} non-English docstrings")
    tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    result = []
    prev_end = (1, 0)
    translated_count = 0
    for i, token in enumerate(tokens):
        tok_type, tok_str, start, end, _line = token
        if start > prev_end:
            lines_between = source.splitlines()[prev_end[0] - 1 : start[0]]
            if len(lines_between) > 1:
                for line_content in lines_between[:-1]:
                    result.append(line_content + "\n")
                result.append(lines_between[-1][: start[1]])
            elif lines_between:
                result.append(lines_between[0][prev_end[1] : start[1]])
        if tok_type == tokenize.COMMENT and not is_english(tok_str):
            comment_text = tok_str[1:].strip()
            print(f"  Translating comment: {comment_text[:50]}...")
            translated = translate_text(comment_text)
            result.append(f"# {translated}")
            translated_count += 1
        elif tok_type == tokenize.STRING:
            stripped = tok_str.strip("'\"")
            if stripped and not is_english(stripped) and len(stripped) > 10:
                try:
                    print(f"  Translating string: {stripped[:50]}...")
                    translated = translate_text(stripped)
                    if tok_str.startswith('"""') or tok_str.startswith("'''"):
                        quote_char = tok_str[:3]
                        tok_str = f"{quote_char}{translated}{quote_char}"
                    else:
                        quote_char = tok_str[0]
                        tok_str = f"{quote_char}{translated}{quote_char}"
                    translated_count += 1
                except Exception as e:
                    print(f"  Error translating string: {e}")
            result.append(tok_str)
        else:
            result.append(tok_str)
        prev_end = end
        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1} tokens...")
    print(f"  Translated {translated_count} items")
    return "".join(result)


def process_files(directory: str) -> None:
    print(f"Scanning directory: {directory}")
    paths = [Path(p) for p in walk_files(directory)]
    files = [p for p in paths if p.is_file()]
    supported_extensions = {
        ".txt",
        ".md",
        ".srt",
        ".json",
        ".html",
        ".py",
    }
    target_files = [f for f in files if f.suffix.lower() in supported_extensions]
    print(f"Found {len(target_files)} supported files out of {len(files)} total files")
    print("-" * 50)
    translated_count = 0
    skipped_count = 0
    error_count = 0
    for i, fp in enumerate(target_files, 1):
        suffix = fp.suffix.lower()
        print(f"[{i}/{len(target_files)}] Processing: {fp}")
        try:
            original = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"  Error reading file: {e}")
            error_count += 1
            continue
        if is_english(original.strip()):
            print("  File is already in English, skipping")
            skipped_count += 1
            continue
        print("  Translating content...")
        try:
            translated = translate_python_file(original, fp) if suffix == ".py" else translate_text(original)
            if translated.strip() != original.strip():
                safe_overwrite(fp, translated)
                print("  ✓ Successfully translated and saved")
                translated_count += 1
            else:
                print("  Translation produced same content, skipping")
                skipped_count += 1
        except Exception as e:
            print(f"  ✗ Error processing file: {e}")
            error_count += 1
        print("-" * 30)
    print("TRANSLATION SUMMARY")
    print("=" * 50)
    print(f"Total files processed: {len(target_files)}")
    print(f"Successfully translated: {translated_count}")
    print(f"Skipped (already English): {skipped_count}")
    print(f"Errors: {error_count}")
    print("=" * 50)


if __name__ == "__main__":
    process_files(DIRECTORY)
