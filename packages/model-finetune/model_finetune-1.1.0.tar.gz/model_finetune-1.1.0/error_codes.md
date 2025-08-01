# 错误状态码参考表

本文档列出了 Model Finetune 项目中所有错误状态码及其对应的错误信息。

## 错误状态码列表

| 状态码 | 错误信息 | 描述 |
|--------|----------|------|
| 10001 | The matched drone data are exactly the same, which may be because the measured data is matched to the same drone point. | 匹配的无人机数据完全相同，可能是因为测量数据匹配到了同一个无人机点 |
| 10002 | The measured data are exactly the same, please check the measured data provided. | 测量数据完全相同，请检查提供的测量数据 |
| 10003 | Unable to read artificially sampled data files using any encoding. | 无法使用任何编码读取人工采样数据文件 |
| 10004 | The artificially sampled data file is empty. | 人工采样数据文件为空 |
| 10005 | The artificially sampled data processing failed. | 人工采样数据处理失败 |
| 10006 | The artificially sampled data file is empty or the format is incorrect. | 人工采样数据文件为空或格式错误 |
| 10007 | The artificially sampled data file parsing failed. | 人工采样数据文件解析失败 |
| 10008 | The artificially sampled data file does not exist. | 人工采样数据文件不存在 |
| 10009 | The artificially sampled data file does not have permission to read. | 没有权限读取人工采样数据文件 |
| 10010 | The artificially sampled data file reading failed: {error_details} | 人工采样数据文件读取失败（包含具体错误信息） |
| 10011 | The data merging failed. | 数据合并失败 |
| 10012 | The data processing failed. | 数据处理失败 |
| 10013 | The INDEXS.CSV or POS.TXT file is not found. | 未找到INDEXS.CSV或POS.TXT文件 |
| 10014 | Unable to parse JSON data | 无法解析JSON数据 |
| 10015 | Error processing pipeline input: {error_details} | 处理管道输入时出错（包含具体错误信息） |
| 10016 | File does not exist: {file_path} | 文件不存在（包含文件路径） |
| 10017 | Model data validation failed: data is not in valid key-value pair format | 模型数据验证失败：数据不是有效的键值对格式 |

## 错误分类

### 数据文件相关错误 (10003-10010, 10013, 10016)
- 文件不存在、为空、格式错误
- 编码问题、权限问题
- 读取和解析失败

### 数据处理相关错误 (10001-10002, 10011-10012, 10017)
- 数据合并失败
- 数据处理失败
- 数据验证失败
- 匹配数据异常

### 输入处理相关错误 (10014-10015)
- JSON解析错误
- 管道输入处理错误

## 使用说明

当程序遇到错误时，会按以下格式输出错误信息：

```json
{
    "status": 错误状态码,
    "data": "错误描述信息"
}
```

然后调用 `sys.exit(1)` 终止程序运行。

## 更新历史

- **2025-08-01**: 初始版本，包含所有17个错误状态码
- 状态码范围：10001-10017
- 所有错误信息均使用英文描述，保持国际化一致性