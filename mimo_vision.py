#!/usr/bin/env python3
"""小米MIMO视觉识别工具 - 图片/视频理解
用法:
  python mimo_vision.py image.jpg                        # 默认描述图片
  python mimo_vision.py image.jpg -p "提取图中文字"      # 自定义提问
  python mimo_vision.py --video video.mp4                # 分析视频
  python mimo_vision.py --video https://example.com/v.mp4 # 视频URL
"""

import argparse
import base64
import mimetypes
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


def load_config():
    """加载 .env 配置"""
    script_dir = Path(__file__).resolve().parent
    for env_path in [Path.cwd() / ".env", script_dir / ".env"]:
        if env_path.exists():
            load_dotenv(env_path, override=True)

    api_key = os.getenv("MIMO_API_KEY")
    if not api_key:
        print("❌ 未设置 MIMO_API_KEY，请在 .env 文件中配置", file=sys.stderr)
        sys.exit(1)

    return {
        "api_key": api_key,
        "base_url": os.getenv("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1"),
        "model": os.getenv("MIMO_MODEL", "mimo-v2-omni"),
    }


def encode_file_to_base64(file_path: str) -> tuple[str, str]:
    """将本地文件编码为 base64 data URL"""
    path = Path(file_path)
    if not path.exists():
        print(f"❌ 文件不存在: {file_path}", file=sys.stderr)
        sys.exit(1)

    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type is None:
        ext = path.suffix.lower()
        mime_map = {
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png", ".gif": "image/gif",
            ".webp": "image/webp", ".bmp": "image/bmp",
            ".mp4": "video/mp4", ".avi": "video/x-msvideo",
            ".mov": "video/quicktime", ".mkv": "video/x-matroska",
        }
        mime_type = mime_map.get(ext, "image/png")

    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{data}", mime_type


def analyze_image(client: OpenAI, model: str, image_path: str, prompt: str) -> str:
    """分析本地图片"""
    data_url, _ = encode_file_to_base64(image_path)

    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }],
        max_tokens=4096,
    )

    return response.choices[0].message.content or "(无返回内容)"


def analyze_video(client: OpenAI, model: str, video_input: str, prompt: str) -> str:
    """分析视频（本地文件或URL）"""
    if video_input.startswith(("http://", "https://")):
        video_content = {"type": "video_url", "video_url": {"url": video_input}}
    else:
        data_url, _ = encode_file_to_base64(video_input)
        video_content = {"type": "video_url", "video_url": {"url": data_url}}

    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                video_content,
            ],
        }],
        max_tokens=4096,
    )

    return response.choices[0].message.content or "(无返回内容)"


def main():
    parser = argparse.ArgumentParser(description="小米MIMO视觉识别工具")
    parser.add_argument("image", nargs="?", help="图片文件路径")
    parser.add_argument("-p", "--prompt",
                        default="请详细描述这张图片/视频的内容，包括所有关键信息和细节。",
                        help="自定义提问")
    parser.add_argument("--video", help="视频文件路径或URL")
    parser.add_argument("--model", help="覆盖默认模型")

    args = parser.parse_args()
    config = load_config()
    model = args.model or config["model"]

    client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])

    print(f"🔍 正在分析{'视频' if args.video else '图片'}...", file=sys.stderr)
    print(f"   模型: {model}", file=sys.stderr)

    try:
        if args.video:
            result = analyze_video(client, model, args.video, args.prompt)
        elif args.image:
            result = analyze_image(client, model, args.image, args.prompt)
        else:
            parser.print_help()
            sys.exit(1)

        print(result)

    except Exception as e:
        print(f"❌ API调用失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
