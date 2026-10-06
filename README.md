# youtube-video-download

YouTube 재생목록의 영상을 영상 방향에 맞는 해상도로 다운로드합니다.

| 영상 방향 | 다운로드 해상도 |
|---|---|
| 세로 (높이 > 너비, 예: Shorts) | 4K (2160x3840) |
| 가로 (너비 ≥ 높이) | 4K (3840x2160) |

원본에 해당 해상도가 없으면 그 이하에서 가장 높은 화질로 받습니다.

## 준비

- Python 3.9 이상
- [ffmpeg](https://ffmpeg.org/) (영상/음성 병합에 필요, PATH에 등록)
- [Deno](https://deno.com/) (YouTube 4K 등 전체 포맷 추출에 필요)

```powershell
pip install -r requirements.txt
winget install Gyan.FFmpeg
winget install DenoLand.Deno
```

## 사용법

```powershell
python download_playlist.py "https://www.youtube.com/playlist?list=PLxxxxxxxx"
```

- 기본 저장 경로: `D:\youtube_video\<재생목록 이름>\`
- 다른 경로로 저장: `-o E:\videos`
- 이미 받은 영상은 `downloaded.txt`에 기록되어 다시 실행하면 건너뜁니다.
