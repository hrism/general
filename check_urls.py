#!/usr/bin/env python3
"""URL死活確認スクリプト

urls.txt（1行1URL）を読み込み、各URLにGETリクエストを送って
ステータスコードと応答時間を表示する。
"""

import argparse
import csv
import sys
import time

import requests


def check_url(url, timeout=5):
    """URLにGETリクエストを送り、ステータスコードと応答時間を返す。"""
    try:
        start = time.time()
        resp = requests.get(url, timeout=timeout)
        elapsed_ms = (time.time() - start) * 1000
        return resp.status_code, round(elapsed_ms, 1), None
    except requests.exceptions.Timeout:
        return None, None, "Timeout"
    except requests.exceptions.ConnectionError:
        return None, None, "ConnectionError"
    except requests.exceptions.RequestException as e:
        return None, None, str(e)


def load_urls(filepath):
    """ファイルからURLリストを読み込む。空行・コメント行はスキップ。"""
    urls = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def main():
    parser = argparse.ArgumentParser(description="URL死活確認スクリプト")
    parser.add_argument(
        "file",
        nargs="?",
        default="urls.txt",
        help="URLリストファイル（デフォルト: urls.txt）",
    )
    parser.add_argument(
        "--csv",
        dest="csv_file",
        metavar="FILE",
        help="結果をCSVファイルに出力する",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="タイムアウト秒数（デフォルト: 5）",
    )
    args = parser.parse_args()

    try:
        urls = load_urls(args.file)
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {args.file}", file=sys.stderr)
        sys.exit(1)

    if not urls:
        print("URLが見つかりませんでした。", file=sys.stderr)
        sys.exit(1)

    results = []
    print(f"{'URL':<50} {'Status':<10} {'Time(ms)':<10} {'Error'}")
    print("-" * 90)

    for url in urls:
        status, elapsed, error = check_url(url, timeout=args.timeout)
        results.append((url, status, elapsed, error))
        if error:
            print(f"{url:<50} {'---':<10} {'---':<10} {error}")
        else:
            print(f"{url:<50} {status:<10} {elapsed:<10} ")

    if args.csv_file:
        with open(args.csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["url", "status_code", "response_time_ms", "error"])
            for url, status, elapsed, error in results:
                writer.writerow([url, status or "", elapsed or "", error or ""])
        print(f"\nCSV出力: {args.csv_file}")


if __name__ == "__main__":
    main()
