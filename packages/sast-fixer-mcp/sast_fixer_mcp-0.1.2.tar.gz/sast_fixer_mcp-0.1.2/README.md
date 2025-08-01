# SAST 漏洞修复 MCP 服务

本项目提供一个专用于处理静态应用安全测试（SAST）报告的 MCP 服务器，具备SAST报告的Docx文档解析、漏洞修复状态跟踪及修复报告导出等核心功能。本MCP server支持湛卢AI程序员中`漏洞修复`进行SAST相关漏洞的下修复，参见[静态应用安全测试（SAST）修复流程](docs/SAST_FIXER_WORKFLOW.md)。



## 功能概述

* **Docx转JSON**：将SAST报告的Word文档解析转换为结构化JSON格式
* **漏洞状态管理**：自动检测待处理的漏洞JSON文件，支持状态查询与更新
* **报告导出**：基于已修复漏洞数据生成标准CSV格式的修复报告



## 可用工具



- convert_sast_docx_to_json - 将SAST报告的docx文档转换为JSON格式
    - file_path (string, 必填): SAST报告docx文件路径

- get_pending_vulnerability_json_files - 获取.scanissuefix目录中所有待处理的漏洞JSON文件(_new.json)

- generate_csv_report - 从所有已完成的漏洞JSON文件(_finished.json)生成CSV报告


## 安装指南

### Python环境要求
* 本项目需要Python 3.10及以上版本，可通过官网安装https://www.python.org/downloads


### 方式一：pip安装（推荐）


获取并安装MCP服务[安装包](dist/sast_fixer_mcp-0.1.0-py3-none-any.whl)：

```bash
pip install sast_fixer_mcp-0.1.0-py3-none-any.whl
```

### 方式二：源码构建安装

```bash
git clone http://gitlab.cmss.com/paas-aipt/ai/zhanlu-agent.git
cd mcp-servers/servers/sast_fixer_mcp
uv build
uv pip install .
```

安装完成后，启动服务验证MCP服务可运行：
```bash
python -m sast_fixer_mcp
```


## 湛卢AI程序员集成配置
### 配置为湛卢AI程序员MCP服务器使用

在湛卢AI程序员MCP服务管理中添加如下全局配置：

```json
{
  "mcpServers": {
    "SAST_FIXER_MCP": {
      "command": "python",
      "args": ["-m", "sast_fixer_mcp"],
      "enabled": true,
      "alwaysAllow": [
        "add_paragraph",
        "open_document",
        "get_document_info",
        "search_text",
        "convert_sast_docx_to_json",
        "get_pending_vulnerability_json_files",
        "generate_csv_report"
      ],
      "timeout": 1800
    }
  }
}
```

> **备注**：
>
> * 如使用特定Python环境，建议使用`which python`命令获取完整路径，如果使用venv获得conda环境，请指定python运行文件的绝对路径。
> * 处理较大SAST报告时，请适当调高`timeout`以避免超时。



## 全局设置

进入右上角设置，调整以下选项以获得最佳体验：

* **模型选择**：deepseek-v3（当前仅支持该模型进行漏洞修复）
* **自动批准权限**：启用读取、写入、重试、MCP及命令执行权限
* **执行命令白名单**：建议添加以下命令，避免频繁询问权限

  ```text
  rm -rf .scanissuefix
  mv .scanissuefix
  mkdir -p .scanissuefix
  ren .scanissuefix
  del .scanissuefix
  del ".scanissuefix"
  dir .scanissuefix
  ren ".scanissuefix"
  move .scanissuefix
  ```



## 使用流程

1. 获取目标代码库对应的SAST报告Word文档。
2. 将代码库克隆到VSCode中并切换至对应分支。
3. 打开湛卢AI程序员对话框，选择“代码安全漏洞修复”功能。
4. 将SAST报告的文件路径（相对或绝对）粘贴至对话框，提交后按提示完成漏洞修复。

> **注意**：修复过程中涉及系统命令操作文件目录，请确保VSCode的终端当前路径定位于项目根目录。当出现修复流程不符合预期的情况可尝试使用自然语言和AI程序员对话，如: `继续修复`，`生成csv报告`，`自动修复`等。