"""
GitHub PR MCP Server 核心功能模块
"""

import json
import hmac
import hashlib
import requests
import os
from datetime import datetime
from typing import Dict, Optional, Any
from openai import OpenAI


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """验证 GitHub Webhook 签名"""
    if not secret:
        return True  # 如果没有设置密钥，跳过验证
    
    expected_signature = f"sha256={hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()}"
    return hmac.compare_digest(signature, expected_signature)


def extract_pr_info(payload: Dict[str, Any]) -> Dict[str, str]:
    """从 GitHub Webhook 载荷中提取 PR 信息"""
    pr = payload.get('pull_request', {})
    return {
        'number': str(pr.get('number', '')),
        'title': pr.get('title', ''),
        'html_url': pr.get('html_url', ''),
        'diff_url': pr.get('diff_url', ''),
        'user': pr.get('user', {}).get('login', ''),
        'repository': payload.get('repository', {}).get('full_name', '')
    }


def get_pr_diff(diff_url: str, github_token: str = "") -> Optional[str]:
    """获取 PR 差异内容"""
    try:
        headers = {}
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        
        response = requests.get(diff_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"获取 PR 差异失败: {e}")
        return None


def analyze_code_changes(diff_content: str, openai_api_key: str = "") -> str:
    """
    使用 AI 分析代码变更
    
    Args:
        diff_content: GitHub PR 差异内容
        openai_api_key: OpenAI API 密钥
        
    Returns:
        AI 生成的代码变更摘要
    """
    if not openai_api_key:
        return "❌ OpenAI API 密钥未配置，无法进行 AI 分析"
    
    try:
        client = OpenAI(api_key=openai_api_key)
        
        system_prompt = """你是一个专业的代码审查助手。请分析以下 GitHub PR 的代码变更，并提供简洁、专业的摘要。

要求：
1. 识别主要的代码变更类型（新增、修改、删除）
2. 分析变更的功能影响
3. 指出潜在的问题或改进建议
4. 使用中文回复
5. 保持客观、专业的语调

请按照以下格式输出：
## 变更摘要
[简要描述主要变更]

## 详细分析
[详细分析代码变更]

## 建议
[如果有的话，提供改进建议]"""

        user_prompt = f"请分析以下 GitHub PR 的代码变更：\n\n{diff_content[:4000]}"  # 限制长度
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"❌ AI 分析失败: {str(e)}"


def format_feishu_message(pr_info: Dict[str, str], summary: str) -> Dict[str, Any]:
    """格式化飞书消息"""
    return {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": f"PR #{pr_info['number']}: {pr_info['title']}",
                    "content": [
                        [{"tag": "text", "text": f"📋 **PR 摘要**\n\n"}],
                        [{"tag": "text", "text": f"🔗 **链接**: {pr_info['html_url']}\n"}],
                        [{"tag": "text", "text": f"👤 **作者**: {pr_info['user']}\n"}],
                        [{"tag": "text", "text": f"📝 **变更摘要**:\n{summary}\n"}],
                        [{"tag": "text", "text": f"📅 **处理时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"}]
                    ]
                }
            }
        }
    }


def send_summary_to_feishu(message: Dict[str, Any], webhook_url: str) -> bool:
    """发送摘要到飞书"""
    try:
        response = requests.post(
            webhook_url,
            json=message,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"发送到飞书失败: {e}")
        return False


def process_github_pr(diff_content: str, pr_info: Dict[str, str], 
                     openai_api_key: str = "", feishu_webhook_url: str = "") -> Dict[str, Any]:
    """
    处理 GitHub PR
    
    Args:
        diff_content: PR 差异内容
        pr_info: PR 信息
        openai_api_key: OpenAI API 密钥
        feishu_webhook_url: 飞书 Webhook URL
        
    Returns:
        处理结果
    """
    try:
        # AI 分析
        summary = analyze_code_changes(diff_content, openai_api_key)
        
        # 发送到飞书（如果配置了）
        feishu_sent = False
        if feishu_webhook_url and not summary.startswith("❌"):
            feishu_message = format_feishu_message(pr_info, summary)
            feishu_sent = send_summary_to_feishu(feishu_message, feishu_webhook_url)
        
        return {
            'status': 'success',
            'pr_number': pr_info['number'],
            'pr_title': pr_info['title'],
            'summary': summary,
            'feishu_sent': feishu_sent,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        } 