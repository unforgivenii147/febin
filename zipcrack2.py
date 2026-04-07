#!/data/data/com.termux/files/usr/bin/python
import multiprocessing as mp
import os
import sys
import time
import zipfile
from pathlib import Path

from print_persian import print_persian as _print

"""
def attempt_password2(args):
    zip_file_path, password_candidate = args
    try:
        with AESZipFile(zip_file_path, "r") as zf:
            zf.setpassword(password_candidate.encode("utf-8"))
            zf.testzip()
            return password_candidate
    except RuntimeError as e:
        if "Bad password" in str(e) or "Incorrect password" in str(e):
            return None
        _print(f"خطای ناشناخته در حین تلاش با '{password_candidate}': {e}")
        return None
    except Exception as e:
        _print(f"خطای کلی در حین تلاش با '{password_candidate}': {e}")
        return None
"""


def attempt_password(args):
    zip_file_path, password_candidate = args
    zip_file_path = Path(zip_file_path)
    try:
        with zipfile.ZipFile(zip_file_path, "r") as zf:
            zf.testzip()  # این تابع صحت ZIP و رمز عبور را چک می‌کند
            return password_candidate
    except RuntimeError as e:
        if "Incorrect password" in str(e):
            return None  # رمز عبور اشتباه است
        _print(f"خطای ناشناخته در حین تلاش با '{password_candidate}': {e}")
        return None
    except Exception as e:
        _print(f"خطای کلی در حین تلاش با '{password_candidate}': {e}")
        return None


def crack_zip_password_multiprocess(zip_file_path, password_list_path, extract_dir="extracted_files"):
    if not os.path.exists(zip_file_path):
        _print(f"خطا: فایل ZIP یافت نشد: {zip_file_path}")
        return None
    if not os.path.exists(password_list_path):
        _print(f"خطا: فایل لیست رمز عبور یافت نشد: {password_list_path}")
        return None
    try:
        with open(password_list_path, encoding="utf-8", errors="ignore") as p_list:
            passwords = [p.strip() for p in p_list if p.strip()]
        total_passwords = len(passwords)
        _print(f"شروع تلاش برای کرک فایل: {zip_file_path}")
        _print(f"با استفاده از لیست رمز عبور: {password_list_path}")
        _print(f"تعداد رمزهای عبور در لیست: {total_passwords}")
        start_time = time.time()
        tasks = [(zip_file_path, p) for p in passwords]
        num_processes = mp.cpu_count()
        _print(f"استفاده از {num_processes} هسته CPU برای پردازش موازی.")
        with mp.Pool(num_processes) as pool:
            results = pool.imap_unordered(attempt_password, tasks, chunksize=100)
            found_password = None
            for i, result in enumerate(results):
                if result:
                    found_password = result
                    break  # رمز عبور پیدا شد، از حلقه خارج می‌شویم
                if (i + 1) % 1000 == 0 or (i + 1) == total_passwords:
                    _print(
                        f"[-] تلاش {i + 1}/{total_passwords} (زمان سپری شده: {(time.time() - start_time):.2f} ثانیه)",
                        end="\r",
                    )
            pool.terminate()  # توقف تمام پروسه‌های کارگر
            pool.join()  # منتظر می‌مانیم تا همه پروسه‌ها واقعا بسته شوند
        end_time = time.time()
        elapsed_time = end_time - start_time
        if found_password:
            _print(f"\n[+] رمز عبور پیدا شد: '{found_password}'")
            _print(f"[+] زمان سپری شده: {elapsed_time:.2f} ثانیه")
            _print(f"[+] تعداد رمزهای امتحان شده: {i + 1} از {total_passwords}")
            try:
                os.makedirs(extract_dir, exist_ok=True)
                with zipfile.ZipFile(zip_file_path, "r") as zf_final:
                    zf_final.extractall(path=extract_dir, pwd=found_password.encode("utf-8"))
                _print(f"[+] فایل‌ها در مسیر '{extract_dir}' استخراج شدند.")
            except Exception as e:
                _print(f"خطا در استخراج فایل‌ها پس از پیدا شدن رمز: {e}")
            return found_password
        _print("\n[-] متاسفانه، رمز عبور در لیست پیدا نشد.")
        _print(f"[-] زمان سپری شده: {elapsed_time:.2f} ثانیه")
        _print(f"[-] تعداد رمزهای امتحان شده: {total_passwords}")
        return None
    except Exception as e:
        _print(f"خطای کلی در حین باز کردن فایل ZIP: {e}")
        return None


if __name__ == "__main__":
    zipfile = Path(sys.argv[1])
    passfile = Path.home() / "isaac" / "wordlist.txt"
    found_password_mp = crack_zip_password_multiprocess(zipfile, passfile)
    if found_password_mp:
        _print(f"\nرمز عبور کشف شده با Multiprocessing: {found_password_mp}")
    else:
        _print("\nرمز عبور در لیست ارائه شده پیدا نشد با Multiprocessing.")
