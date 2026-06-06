# MIMO Vision

基于小米 MiMo 多模态大模型的视觉识别工具，支持图片和视频理解。

## 功能

- **图片理解**：本地图片内容描述、文字提取、场景分析
- **视频理解**：本地视频或视频URL内容总结
- OpenAI 兼容接口，可轻松集成到其他工具链

## 安装

```bash
pip install openai python-dotenv
```

## 配置

```bash
cp .env.example .env
# 编辑 .env，填入你的 MIMO API Key
```

`.env` 配置项：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MIMO_API_KEY` | 小米 MiMo API Key（必填） | - |
| `MIMO_BASE_URL` | API 地址 | `https://api.xiaomimimo.com/v1` |
| `MIMO_MODEL` | 模型名称 | `mimo-v2-omni` |

## 使用

```bash
# 图片识别
python mimo_vision.py photo.jpg
python mimo_vision.py photo.jpg -p "提取图中所有文字"

# 视频分析
python mimo_vision.py --video demo.mp4
python mimo_vision.py --video https://example.com/video.mp4 -p "总结视频内容"
```

## API Key 获取

前往 [platform.xiaomimimo.com](https://platform.xiaomimimo.com) 注册并获取 API Key。

## License

MIT
