# jimmy_utils

一个简单的Python工具包，目前包含以下功能：

## 功能列表

### kimi函数
将字符串数据编码为十六进制格式

```python
from jimmy_utils.jimmyencode import kimi

encoded = kimi("hello world")
print(encoded)  # 输出: 68656c6c6f20776f726c64
```

## 安装

```bash
pip install jimmy_utils
```

## 版本历史

- 0.2.1: 更新版本以解决PyPI上传问题
- 0.2.0: 初始版本