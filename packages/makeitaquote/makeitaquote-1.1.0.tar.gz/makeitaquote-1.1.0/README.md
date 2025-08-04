# makeitaquote
Discord用Make it a Quote生成パッケージです。
使用しているAPIが死んだら終わりです()

## Installation

```bash
pip install makeitaquote
```

## 使い方
```python
from makeitaquote import MiQ
# ...
miq = (
    MiQ()
    .set_from_message(referenced_message, format_text=True)
    .set_color(True)
    .set_watermark(bot.user.name)
)
image_bytes = miq.generate_beta()
file = discord.File(io.BytesIO(image_bytes), filename="quote.png")
```