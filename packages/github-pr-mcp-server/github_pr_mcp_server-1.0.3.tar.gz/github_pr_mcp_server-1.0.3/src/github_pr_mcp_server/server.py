"""
GitHub PR MCP Server 服务器模块
"""

import os
import json
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
import gradio as gr

from .core import (
    verify_webhook_signature,
    extract_pr_info,
    get_pr_diff,
    analyze_code_changes,
    process_github_pr
)


class GradioMCPServer:
    """Gradio MCP 服务器"""
    
    def __init__(self):
        # 使用 get() 方法提供默認值，避免 KeyError
        self.webhook_secret = os.getenv('WEBHOOK_SECRET', '')
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.feishu_webhook_url = os.getenv('FEISHU_WEBHOOK_URL', '')
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        
        # 创建 Gradio 界面
        self.demo = self._create_gradio_interface()
    
    def list_tools(self) -> Dict[str, Any]:
        """
        MCP 必需方法：列出可用的工具
        
        Returns:
            包含可用工具信息的字典
        """
        return {
            "tools": [
                {
                    "name": "mcp_analyze_pr",
                    "description": "分析 GitHub PR 差异并生成摘要",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "diff_content": {
                                "type": "string",
                                "description": "GitHub PR 差异内容"
                            },
                            "openai_api_key": {
                                "type": "string",
                                "description": "OpenAI API 密钥（可选）"
                            },
                            "feishu_webhook_url": {
                                "type": "string",
                                "description": "飞书 Webhook URL（可选）"
                            },
                            "github_token": {
                                "type": "string",
                                "description": "GitHub 令牌（可选）"
                            }
                        },
                        "required": ["diff_content"]
                    }
                },
                {
                    "name": "mcp_process_webhook",
                    "description": "处理 GitHub Webhook 载荷并生成摘要",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "webhook_payload": {
                                "type": "string",
                                "description": "GitHub Webhook 载荷的 JSON 字符串"
                            },
                            "openai_api_key": {
                                "type": "string",
                                "description": "OpenAI API 密钥（可选）"
                            },
                            "feishu_webhook_url": {
                                "type": "string",
                                "description": "飞书 Webhook URL（可选）"
                            },
                            "github_token": {
                                "type": "string",
                                "description": "GitHub 令牌（可选）"
                            }
                        },
                        "required": ["webhook_payload"]
                    }
                },
                {
                    "name": "mcp_manual_analysis",
                    "description": "手动分析代码变更，支持可选的飞书集成",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "diff_content": {
                                "type": "string",
                                "description": "GitHub PR 差异内容"
                            },
                            "openai_api_key": {
                                "type": "string",
                                "description": "OpenAI API 密钥（可选）"
                            },
                            "feishu_webhook_url": {
                                "type": "string",
                                "description": "飞书 Webhook URL（可选）"
                            },
                            "github_token": {
                                "type": "string",
                                "description": "GitHub 令牌（可选）"
                            }
                        },
                        "required": ["diff_content"]
                    }
                }
            ]
        }
    
    def _create_gradio_interface(self):
        """创建 Gradio 界面"""
        
        def mcp_analyze_pr(diff_content: str, openai_api_key: str = "", 
                          feishu_webhook_url: str = "", github_token: str = "") -> str:
            """
            MCP 函数：分析 GitHub PR 差异并生成摘要
            
            Args:
                diff_content: GitHub PR 差异内容
                openai_api_key: OpenAI API 密钥
                feishu_webhook_url: 飞书 Webhook URL（可选）
                github_token: GitHub 令牌（可选）
                
            Returns:
                AI 生成的代码变更摘要
            """
            return analyze_code_changes(diff_content, openai_api_key or self.openai_api_key)
        
        def mcp_process_webhook(webhook_payload: str, openai_api_key: str = "",
                              feishu_webhook_url: str = "", github_token: str = "") -> Dict[str, Any]:
            """
            MCP 函数：处理 GitHub Webhook 载荷并生成摘要
            
            Args:
                webhook_payload: GitHub Webhook 载荷的 JSON 字符串
                openai_api_key: OpenAI API 密钥
                feishu_webhook_url: 飞书 Webhook URL（可选）
                github_token: GitHub 令牌（可选）
                
            Returns:
                处理结果，包含摘要和元数据
            """
            try:
                payload = json.loads(webhook_payload)
                event_type = payload.get('action', '')
                
                if event_type in ['opened', 'synchronize', 'reopened']:
                    pr_info = extract_pr_info(payload)
                    diff_content = get_pr_diff(pr_info['diff_url'], github_token or self.github_token)
                    
                    if diff_content:
                        return process_github_pr(
                            diff_content, 
                            pr_info, 
                            openai_api_key or self.openai_api_key,
                            feishu_webhook_url or self.feishu_webhook_url
                        )
                    else:
                        return {'error': '获取 PR 差异失败', 'status': 'error'}
                else:
                    return {'message': f'事件 {event_type} 被忽略', 'status': 'ignored'}
                    
            except Exception as e:
                return {'error': str(e), 'status': 'error'}
        
        def mcp_manual_analysis(diff_content: str, openai_api_key: str = "",
                              feishu_webhook_url: str = "", github_token: str = "") -> str:
            """
            MCP 函数：手动分析代码变更，支持可选的飞书集成
            
            Args:
                diff_content: GitHub PR 差异内容
                openai_api_key: OpenAI API 密钥
                feishu_webhook_url: 飞书 Webhook URL（可选）
                github_token: GitHub 令牌（可选）
                
            Returns:
                AI 生成的代码变更摘要
            """
            summary = analyze_code_changes(diff_content, openai_api_key or self.openai_api_key)
            
            if feishu_webhook_url or self.feishu_webhook_url:
                try:
                    mock_pr_info = {
                        'number': 'Manual',
                        'title': '手动代码分析',
                        'html_url': 'N/A',
                        'user': 'Manual User'
                    }
                    from .core import format_feishu_message, send_summary_to_feishu
                    feishu_message = format_feishu_message(mock_pr_info, summary)
                    webhook_url = feishu_webhook_url or self.feishu_webhook_url
                    if send_summary_to_feishu(feishu_message, webhook_url):
                        summary += "\n\n✅ 摘要已发送到飞书"
                    else:
                        summary += "\n\n❌ 发送到飞书失败"
                except Exception as e:
                    summary += f"\n\n❌ 发送到飞书失败: {str(e)}"
            
            return summary
        
        # 创建 Gradio 界面
        demo = gr.Interface(
            fn=mcp_manual_analysis,
            inputs=[
                gr.Textbox(lines=10, placeholder="输入 GitHub PR 差异内容", label="GitHub 差异内容"),
                gr.Textbox(placeholder="输入你的 OpenAI API 密钥", label="OpenAI API 密钥", type="password"),
                gr.Textbox(placeholder="输入飞书 Webhook URL（可选）", label="飞书 Webhook URL（可选）"),
                gr.Textbox(placeholder="输入 GitHub 令牌（可选）", label="GitHub 令牌（可选）", type="password")
            ],
            outputs=gr.Textbox(label="生成的摘要"),
            title="GitHub PR MCP Server - MCP&Agent Challenge",
            description="支持 MCP 协议的 AI 驱动 GitHub PR 分析，集成飞书功能",
            examples=[
                [
                    """diff --git a/example.py b/example.py
index 83db48f..f735c3e 100644
--- a/example.py
+++ b/example.py
@@ -1,3 +1,4 @@
+print('Hello World')
 print('This is an example file.')
 print('It has some changes.')""",
                    "",
                    "",
                    ""
                ]
            ]
        )
        
        return demo
    
    def launch(self, port: int = 8080):
        """启动 Gradio MCP 服务器"""
        print(f"🚀 GitHub PR Gradio MCP 服务器启动在端口 {port}")
        print(f"🌐 Web 界面: http://localhost:{port}")
        print(f"🔧 MCP 端点: http://localhost:{port}/gradio_api/mcp/sse")
        print(f"📡 Webhook URL: http://localhost:{port}/webhook/github")
        
        self.demo.launch(
            mcp_server=True,
            server_port=port,
            server_name="0.0.0.0",
            show_error=True,
            quiet=False,
            share=False,
            inbrowser=False
        )


class FlaskMCPServer:
    """Flask MCP 服务器"""
    
    def __init__(self):
        # 使用 get() 方法提供默認值，避免 KeyError
        self.webhook_secret = os.getenv('WEBHOOK_SECRET', '')
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.feishu_webhook_url = os.getenv('FEISHU_WEBHOOK_URL', '')
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        
        # 创建 Flask 应用
        self.app = Flask(__name__)
        self._setup_routes()
    
    def list_tools(self) -> Dict[str, Any]:
        """
        MCP 必需方法：列出可用的工具
        
        Returns:
            包含可用工具信息的字典
        """
        return {
            "tools": [
                {
                    "name": "mcp_analyze_pr",
                    "description": "分析 GitHub PR 差异并生成摘要",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "diff_content": {
                                "type": "string",
                                "description": "GitHub PR 差异内容"
                            },
                            "openai_api_key": {
                                "type": "string",
                                "description": "OpenAI API 密钥（可选）"
                            },
                            "feishu_webhook_url": {
                                "type": "string",
                                "description": "飞书 Webhook URL（可选）"
                            },
                            "github_token": {
                                "type": "string",
                                "description": "GitHub 令牌（可选）"
                            }
                        },
                        "required": ["diff_content"]
                    }
                },
                {
                    "name": "mcp_process_webhook",
                    "description": "处理 GitHub Webhook 载荷并生成摘要",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "webhook_payload": {
                                "type": "string",
                                "description": "GitHub Webhook 载荷的 JSON 字符串"
                            },
                            "openai_api_key": {
                                "type": "string",
                                "description": "OpenAI API 密钥（可选）"
                            },
                            "feishu_webhook_url": {
                                "type": "string",
                                "description": "飞书 Webhook URL（可选）"
                            },
                            "github_token": {
                                "type": "string",
                                "description": "GitHub 令牌（可选）"
                            }
                        },
                        "required": ["webhook_payload"]
                    }
                },
                {
                    "name": "mcp_manual_analysis",
                    "description": "手动分析代码变更，支持可选的飞书集成",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "diff_content": {
                                "type": "string",
                                "description": "GitHub PR 差异内容"
                            },
                            "openai_api_key": {
                                "type": "string",
                                "description": "OpenAI API 密钥（可选）"
                            },
                            "feishu_webhook_url": {
                                "type": "string",
                                "description": "飞书 Webhook URL（可选）"
                            },
                            "github_token": {
                                "type": "string",
                                "description": "GitHub 令牌（可选）"
                            }
                        },
                        "required": ["diff_content"]
                    }
                }
            ]
        }
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.route('/webhook/github', methods=['POST'])
        def github_webhook():
            """处理 GitHub Webhook 事件"""
            try:
                signature = request.headers.get('X-Hub-Signature-256', '')
                if not verify_webhook_signature(request.data, signature, self.webhook_secret):
                    return jsonify({'error': '无效签名'}), 401
                
                webhook_payload = request.get_data(as_text=True)
                result = self._mcp_process_webhook(webhook_payload)
                
                return jsonify(result)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/mcp/analyze', methods=['POST'])
        def mcp_analyze_endpoint():
            """MCP 分析端点"""
            try:
                data = request.json
                diff_content = data.get('diff_content', '')
                
                if not diff_content:
                    return jsonify({'error': 'diff_content 是必需的'}), 400
                
                summary = self._mcp_analyze_pr(diff_content)
                return jsonify({'summary': summary})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/mcp/process_webhook', methods=['POST'])
        def mcp_webhook_endpoint():
            """MCP Webhook 处理端点"""
            try:
                data = request.json
                webhook_payload = data.get('webhook_payload', '')
                
                if not webhook_payload:
                    return jsonify({'error': 'webhook_payload 是必需的'}), 400
                
                result = self._mcp_process_webhook(webhook_payload)
                return jsonify(result)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """健康检查端点"""
            return jsonify({
                'status': 'healthy',
                'service': 'GitHub PR MCP Server',
                'webhook_secret_configured': bool(self.webhook_secret),
                'openai_key_configured': bool(self.openai_api_key),
                'feishu_webhook_configured': bool(self.feishu_webhook_url),
                'mcp_functions': [
                    'mcp_analyze_pr',
                    'mcp_process_webhook'
                ]
            })
    
    def _mcp_analyze_pr(self, diff_content: str) -> str:
        """MCP 函数：分析 GitHub PR 差异"""
        return analyze_code_changes(diff_content, self.openai_api_key)
    
    def _mcp_process_webhook(self, webhook_payload: str) -> Dict[str, Any]:
        """MCP 函数：处理 GitHub Webhook 载荷"""
        try:
            payload = json.loads(webhook_payload)
            event_type = payload.get('action', '')
            
            if event_type in ['opened', 'synchronize', 'reopened']:
                pr_info = extract_pr_info(payload)
                diff_content = get_pr_diff(pr_info['diff_url'], self.github_token)
                
                if diff_content:
                    return process_github_pr(diff_content, pr_info, self.openai_api_key, self.feishu_webhook_url)
                else:
                    return {'error': '获取 PR 差异失败', 'status': 'error'}
            else:
                return {'message': f'事件 {event_type} 被忽略', 'status': 'ignored'}
                
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
    
    def run(self, port: int = 5000):
        """启动 Flask MCP 服务器"""
        print(f"🚀 GitHub PR Flask MCP 服务器启动在端口 {port}")
        print(f"📡 Webhook URL: http://localhost:{port}/webhook/github")
        print(f"🔧 MCP 端点:")
        print(f"   - POST /mcp/analyze")
        print(f"   - POST /mcp/process_webhook")
        print(f"💚 健康检查: http://localhost:{port}/health")
        
        self.app.run(host='0.0.0.0', port=port, debug=False) 