import sys
from pathlib import Path

from dhh import fsz, gsz, run_command


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} input.pdf")
        sys.exit(1)
    input_path = Path(sys.argv[1]).resolve()
    if not input_path.exists():
        print(
            "Input file not found.",
            file=sys.stderr,
        )
        sys.exit(1)
    if input_path.suffix.lower() != ".pdf":
        print(
            "Input must be a PDF file.",
            file=sys.stderr,
        )
        sys.exit(1)
    temp_gs = input_path.with_name(f"temp_gs_{input_path.name}")
    size_before = input_path.stat().st_size
    print(f"Before : {fsz(size_before)}")
    gs_cmd = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dDownsampleColorImages=true",
        "-dDownsampleGrayImages=true",
        "-dDownsampleMonoImages=true",
        "-dColorImageResolution=50",
        "-dGrayImageResolution=50",
        "-dMonoImageResolution=50",
        "-dColorImageDownsampleType=/Bicubic",
        "-dGrayImageDownsampleType=/Bicubic",
        "-dMonoImageDownsampleType=/Subsample",
        "-dNOPAUSE",
        "-dBATCH",
        "-dQUIET",
        f"-sOutputFile={temp_gs}",
        str(input_path),
    ]
    run_command(gs_cmd)
    size_after = temp_gs.stat().st_size
    print(f"After  : {fsz(size_after)}")
    diff = size_before - size_after
    sign = "-" if diff >= 0 else "+"
    if size_after < size_before:
        temp_gs.replace(input_path)
        print(f"Saved  : {sign}{fsz(diff)}")
    else:
        print("original file is smaller")
        temp_gs.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
