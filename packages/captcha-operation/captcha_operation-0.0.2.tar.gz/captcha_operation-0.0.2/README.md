# captcha_operation
数字运算验证码

# Install

```
pip install captcha-operation
```

# Test

```python
from captcha_operation.operation import operation
```

## bytes

```python
filepath = os.path.join(os.path.dirname(__file__), 'captcha.png')
result = operation(filepath)
```

## Image

```python
filepath = os.path.join(os.path.dirname(__file__), 'captcha.png')
result = operation(Image.open(filepath))
```

## base64 str

```python
result = operation('iVBORw0KGgoAAAANSUhEUgAAAIcAAAAoCAIAAxxx')
```

