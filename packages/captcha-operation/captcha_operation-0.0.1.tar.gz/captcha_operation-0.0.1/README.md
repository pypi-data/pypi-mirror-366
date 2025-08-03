# captcha_operation
数字运算验证码

# Install

```
pip install captcha_operation
```

# Test

```
from captcha_operation.operation import operation

filepath = os.path.join(os.path.dirname(__file__), 'captcha.png')
result = operation(filepath)
```