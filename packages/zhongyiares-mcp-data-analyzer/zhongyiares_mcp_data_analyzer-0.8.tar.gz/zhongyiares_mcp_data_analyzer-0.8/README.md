# 数据分析助手

## 本地调试
```
uv --directory /Users/morris/Desktop/coding/mcp-data-analzyer run main.py
```
## 提示词
分析{需要分析的文件路径}的各个方面，包含文字和图表，将分析结果保存为markdown格式的分析报告，
分析报告保存到{文件保存路径}目录下

## MCP 配置
```
{
   "mcp-data-analyzer":{
       "command": "uvx",
      "args": ["mcp-data-analyzer"]
   }
}

```

## 对外分享
三步：  
[01 账号申请](./pypi包上传/01%20账号申请.md)  
[02 上传压缩包到pypi](./pypi包上传/03%20上传压缩包到pypi.md)  
03 测试效果