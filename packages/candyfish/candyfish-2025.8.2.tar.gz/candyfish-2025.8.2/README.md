# CandyFish - 简单文本训练器

CandyFish 是一个轻量级的文本生成与训练工具库，旨在为开发者和研究者提供简单易用的文本生成模型训练和推理接口。

## 特性

- 🚀 **简单易用**：简洁的API设计，几行代码即可开始训练或生成文本
- 🏗️ **模块化设计**：轻松加载、保存和复用模型
- 🔥 **高效训练**：支持自定义学习率和训练轮次
- 🎯 **灵活生成**：可调节生成温度和长度，满足不同需求
- 📚 **兼容多种格式**：支持标准文本对训练数据

## 安装

```bash
pip install candyfish
```

## 快速开始

### 1. 基本使用

```python
from candyfish import Model

# 加载模型
model = Model()
model.load('pretrained_model.spt')

# 文本生成
response = model.generate(
    prompt='<|user|>你好<|assistant|>',
    temperature=0.7,
    max_length=100
)
print(response)
```

### 2. 模型训练

```python
from candyfish import Model

# 初始化模型
model = Model()

# 准备训练数据
training_data = [
    ('输入文本1', '目标输出1'),
    ('输入文本2', '目标输出2'),
    # 更多训练样本...
]

# 开始训练
model.train(
    sample=training_data,
    study_lr=0.001,
    epochs=20
)

# 保存模型
model.save('my_trained_model.spt')
```

## API参考

### `Model` 类

#### `load(path)`
- 从指定路径加载预训练模型
- 参数：
  - `path`: 模型文件路径

#### `save(path)`
- 将模型保存到指定路径
- 参数：
  - `path`: 保存路径

#### `train(sample, study_lr, epochs)`
- 训练模型
- 参数：
  - `sample`: 训练样本列表，格式为[(输入文本, 目标文本), ...]
  - `study_lr`: 学习率 (默认: 0.001)
  - `epochs`: 训练轮次 (默认: 20)

#### `generate(prompt, temperature, max_length)`
- 根据提示生成文本
- 参数：
  - `prompt`: 输入提示文本
  - `temperature`: 生成温度 (默认: 0.7)
  - `max_length`: 生成最大长度 (默认: 100)
- 返回：生成的文本

## 应用场景

- 聊天机器人开发
- 文本自动补全
- 创意写作辅助
- 对话系统原型开发
- 教育领域的问答系统

## 贡献

欢迎提交issue和pull request！请确保您的代码符合PEP8规范并通过所有测试。

## 许可证

MIT License