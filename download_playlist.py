"""YouTube 재생목록 다운로더.

영상 방향에 따라 해상도를 다르게 선택한다.
  - 세로 영상 (높이 > 너비): 4K (짧은 변 기준 2160, 예: 2160x3840)
  - 가로 영상 (너비 >= 높이): 4K   (짧은 변 기준 2160, 예: 3840x2160)
해당 해상도가 없으면 그 이하에서 가장 좋은 화질로 받는다.

사용법:
    python download_playlist.py <재생목록 URL> [-o 저장경로]
"""

import argparse
import os
import sys

import yt_dlp

DEFAULT_OUTPUT_DIR = r"D:\youtube_video"

# 세로 영상은 너비(짧은 변), 가로 영상은 높이(짧은 변) 기준 2160 이하 (4K)
VERTICAL_FORMAT = "bv*[width<=2160]+ba/b[width<=2160]/bv*+ba/b"
HORIZONTAL_FORMAT = "bv*[height<=2160]+ba/b[height<=2160]/bv*+ba/b"


def get_dimensions(info):
    """영상의 원본 (너비, 높이)를 구한다. 알 수 없으면 (None, None)."""
    video_formats = [
        f for f in info.get("formats") or []
        if f.get("vcodec") not in (None, "none") and f.get("width") and f.get("height")
    ]
    if video_formats:
        best = max(video_formats, key=lambda f: f["width"] * f["height"])
        return best["width"], best["height"]
    return info.get("width"), info.get("height")


def is_vertical(info):
    width, height = get_dimensions(info)
    if not width or not height:
        return False
    return height > width


def download_playlist(url, output_dir, archive_file):
    os.makedirs(output_dir, exist_ok=True)

    # 1단계: 재생목록 항목 목록만 빠르게 가져온다
    with yt_dlp.YoutubeDL({"extract_flat": "in_playlist", "quiet": True}) as ydl:
        playlist = ydl.extract_info(url, download=False)

    entries = [e for e in playlist.get("entries") or [] if e]
    playlist_title = playlist.get("title") or "playlist"
    print(f"재생목록: {playlist_title} ({len(entries)}개)")

    base_opts = {
        "paths": {"home": output_dir},
        "download_archive": archive_file,
        "merge_output_format": "mp4",
        "ignoreerrors": True,
        "noplaylist": True,
    }

    failed = []
    for index, entry in enumerate(entries, start=1):
        video_url = entry.get("url") or entry.get("webpage_url")
        if video_url and not video_url.startswith("http"):
            video_url = f"https://www.youtube.com/watch?v={entry['id']}"
        print(f"\n[{index}/{len(entries)}] {entry.get('title') or video_url}")

        # 2단계: 영상별 상세 정보로 방향을 판단한다
        try:
            with yt_dlp.YoutubeDL({"quiet": True, "noplaylist": True}) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except yt_dlp.utils.DownloadError as e:
            print(f"  정보를 가져오지 못했습니다: {e}")
            failed.append(video_url)
            continue

        vertical = is_vertical(info)
        width, height = get_dimensions(info)
        print(f"  원본 {width}x{height} -> {'세로' if vertical else '가로'} 영상, 4K로 다운로드")

        opts = dict(base_opts)
        opts["format"] = VERTICAL_FORMAT if vertical else HORIZONTAL_FORMAT
        opts["outtmpl"] = os.path.join(
            playlist_title.replace("/", "_").replace("\\", "_"),
            f"{index:03d} - %(title)s [%(id)s].%(ext)s",
        )

        with yt_dlp.YoutubeDL(opts) as ydl:
            if ydl.download([video_url]) != 0:
                failed.append(video_url)

    print(f"\n완료: {len(entries) - len(failed)}개 성공, {len(failed)}개 실패")
    for u in failed:
        print(f"  실패: {u}")
    return 1 if failed else 0


def main():
    parser = argparse.ArgumentParser(description="YouTube 재생목록을 방향에 맞는 해상도로 다운로드")
    parser.add_argument("url", help="YouTube 재생목록 URL")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT_DIR,
                        help=f"저장 경로 (기본값: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--archive", default=None,
                        help="이미 받은 영상 기록 파일 (기본값: <저장경로>/downloaded.txt)")
    args = parser.parse_args()

    archive = args.archive or os.path.join(args.output, "downloaded.txt")
    sys.exit(download_playlist(args.url, args.output, archive))


if __name__ == "__main__":
    main()
