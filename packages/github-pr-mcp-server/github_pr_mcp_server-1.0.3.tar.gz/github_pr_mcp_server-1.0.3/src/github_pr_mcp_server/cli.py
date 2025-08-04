"""
GitHub PR MCP Server 命令行接口
"""

import os
import sys
from typing import Optional

from .server import GradioMCPServer, FlaskMCPServer


def main():
    """主函数"""
    print("🚀 GitHub PR MCP Server - MCP&Agent Challenge")
    print("=" * 50)
    
    # 获取服务器类型
    server_type = os.getenv('MCP_SERVER_TYPE', 'gradio').lower()
    
    # 获取端口配置
    webhook_port = int(os.getenv('WEBHOOK_PORT', 5000))
    gradio_port = int(os.getenv('GRADIO_PORT', 8080))
    
    print(f"🔧 服务器类型: {server_type}")
    print(f"📡 Webhook 端口: {webhook_port}")
    print(f"🌐 Gradio 端口: {gradio_port}")
    print("=" * 50)
    
    # 验证环境变量
    validate_environment()
    
    try:
        if server_type == 'flask':
            # 启动 Flask MCP 服务器
            server = FlaskMCPServer()
            server.run(port=webhook_port)
        else:
            # 启动 Gradio MCP 服务器
            server = GradioMCPServer()
            server.launch(port=gradio_port)
            
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")
        sys.exit(1)


def validate_environment():
    """验证环境变量配置"""
    print("🔍 验证环境配置...")
    
    # 检查必需的环境变量
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API 密钥',
        'WEBHOOK_SECRET': 'GitHub Webhook 密钥',
        'FEISHU_WEBHOOK_URL': '飞书 Webhook URL',
        'GITHUB_TOKEN': 'GitHub 令牌'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        print("⚠️ 以下环境变量未设置（可选）:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 这些变量是可选的，可以在运行时通过参数提供")
    else:
        print("✅ 所有环境变量已配置")
    
    print()


def show_help():
    """显示帮助信息"""
    print("GitHub PR MCP Server - 使用说明")
    print("=" * 50)
    print()
    print("环境变量配置:")
    print("  OPENAI_API_KEY     - OpenAI API 密钥")
    print("  WEBHOOK_SECRET     - GitHub Webhook 密钥")
    print("  FEISHU_WEBHOOK_URL - 飞书 Webhook URL")
    print("  GITHUB_TOKEN       - GitHub 令牌")
    print("  MCP_SERVER_TYPE    - 服务器类型 (gradio/flask)")
    print("  WEBHOOK_PORT       - Webhook 端口 (默认: 5000)")
    print("  GRADIO_PORT        - Gradio 端口 (默认: 8080)")
    print()
    print("使用方法:")
    print("  python -m github_pr_mcp_server")
    print("  github-pr-mcp-server")
    print()
    print("MCP 客户端配置:")
    print("  {")
    print('    "mcpServers": {')
    print('      "github-pr-mcp-server": {')
    print('        "command": "uvx",')
    print('        "args": ["github-pr-mcp-server@latest"],')
    print('        "env": {')
    print('          "OPENAI_API_KEY": "YOUR_OPENAI_API_KEY",')
    print('          "WEBHOOK_SECRET": "YOUR_WEBHOOK_SECRET",')
    print('          "FEISHU_WEBHOOK_URL": "YOUR_FEISHU_WEBHOOK_URL",')
    print('          "GITHUB_TOKEN": "YOUR_GITHUB_TOKEN"')
    print('        }')
    print('      }')
    print('    }')
    print('  }')


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
    else:
        main() 