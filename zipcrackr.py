#!/data/data/com.termux/files/usr/bin/python
import zipfile
import os
import time
import sys
from pathlib import Path


def crack_zip_wordlist(zip_file_path, wordlist_path, extract_dir="extracted_files"):
    if not os.path.exists(zip_file_path):
        print(f"خطا: فایل ZIP یافت نشد: {zip_file_path}")
        return None
    if not os.path.exists(wordlist_path):
        print(f"خطا: فایل لیست رمز عبور یافت نشد: {wordlist_path}")
        return None
    try:
        with zipfile.ZipFile(zip_file_path, "r") as zf:
            print(f"شروع تلاش برای کرک فایل: {zip_file_path}")
            print(f"با استفاده از لیست رمز عبور: {wordlist_path}")
            with open(wordlist_path, encoding="utf-8", errors="ignore") as p_list:
                wordlists = p_list.readlines()
            total_wordlists = len(wordlists)
            start_time = time.time()
            for i, wordlist_candidate in enumerate(wordlists):
                wordlist_candidate = wordlist_candidate.strip()  # حذف فاصله و خط جدید
                if not wordlist_candidate:  # نادیده گرفتن خطوط خالی
                    continue
                try:
                    zf.extractall(path=extract_dir, pwd=wordlist_candidate.encode("utf-8"))
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    print(f"\n[+] رمز عبور پیدا شد: '{wordlist_candidate}'")
                    print(f"[+] فایل‌ها در مسیر '{extract_dir}' استخراج شدند.")
                    print(f"[+] زمان سپری شده: {elapsed_time:.2f} ثانیه")
                    print(f"[+] تعداد رمزهای امتحان شده: {i + 1} از {total_wordlists}")
                    return wordlist_candidate
                except RuntimeError as e:
                    # این خطا معمولاً برای رمز عبور اشتباه رخ می‌دهد
                    if "Bad wordlist" in str(e) or "Incorrect wordlist" in str(e):
                        if (i + 1) % 100 == 0 or (i + 1) == total_wordlists:
                            print(
                                f"[-] تلاش {i + 1}/{total_wordlists}: '{wordlist_candidate}' (زمان سپری شده: {(time.time() - start_time):.2f} ثانیه)",
                                end="\r",
                            )
                    else:
                        print(f"\nخطای ناشناخته در حین تلاش با '{wordlist_candidate}': {e}")
                except Exception as e:
                    print(f"\nخطای کلی در حین تلاش با '{wordlist_candidate}': {e}")
            end_time = time.time()
            elapsed_time = end_time - start_time
            print("\n[-] متاسفانه، رمز عبور در لیست پیدا نشد.")
            print(f"[-] زمان سپری شده: {elapsed_time:.2f} ثانیه")
            print(f"[-] تعداد رمزهای امتحان شده: {total_wordlists}")
            return None
    except zipfile.BadZipFile:
        print(f"��طا: فایل '{zip_file_path}' یک فایل ZIP معتبر نیست یا خراب است.")
        return None
    except Exception as e:
        print(f"خطای کلی در حین باز کردن فایل ZIP: {e}")
        return None


if __name__ == "__main__":
    zip_file = sys.argv[1]
    wordlist_file = Path.home() / "isaac" / "wordlist.txt"
    found_wordlist = crack_zip_wordlist(zip_file, wordlist_file)
    if found_wordlist:
        print(f"\nرمز عبور کشف شده: {found_wordlist}")
    else:
        print("\nرمز عبور در لیست ارائه شده پیدا نشد.")
