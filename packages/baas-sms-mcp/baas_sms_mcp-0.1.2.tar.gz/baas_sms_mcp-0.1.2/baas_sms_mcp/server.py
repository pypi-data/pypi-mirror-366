#!/usr/bin/env python3
"""
BaaS SMS/MMS MCP Server

Model Context Protocol server for SMS and MMS messaging services.
This server provides tools for sending SMS/MMS messages, checking message status,
and retrieving sending history through BaaS API integration.
"""

import os
import httpx
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP

# Create the FastMCP instance for SMS/MMS messaging service
mcp = FastMCP("baas-mcp")

# Configuration
API_BASE_URL = "https://api.aiapp.link"  # Fixed BaaS API endpoint
BAAS_API_KEY = os.getenv("BAAS_API_KEY", "")
PROJECT_ID = os.getenv("PROJECT_ID", "")

# HTTP client setup
client = httpx.AsyncClient(timeout=30.0)

@mcp.tool()
async def send_sms(
    recipients: List[Dict[str, str]],
    message: str,
    callback_number: str,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send SMS message to one or multiple recipients for user authentication, notifications, or marketing campaigns
    
    Perfect for: user registration verification, order confirmations, 2FA codes, promotional messages
    
    Args:
        recipients: List of recipients with phone_number (Korean format: 010-1234-5678) and member_code (unique identifier)
        message: SMS message content (max 2000 characters, supports Korean text)
        callback_number: Sender callback number (your business number)
        project_id: Project UUID (optional, uses env var if not provided)
    
    Returns:
        Dictionary with success status, group_id for tracking, and sending statistics
        Use group_id with get_message_status() to check delivery
    """
    try:
        # Use provided project_id or fallback to environment variable
        current_project_id = project_id or PROJECT_ID
        if not current_project_id:
            return {
                "success": False,
                "error": "프로젝트 ID가 필요합니다",
                "error_code": "MISSING_PROJECT_ID"
            }
        
        # Validate input
        if not recipients or len(recipients) > 1000:
            return {
                "success": False,
                "error": "수신자 수는 1명 이상 1000명 이하여야 합니다",
                "error_code": "INVALID_RECIPIENTS_COUNT"
            }
        
        if len(message) > 2000:
            return {
                "success": False,
                "error": "메시지 길이가 2000자를 초과했습니다",
                "error_code": "MESSAGE_TOO_LONG"
            }
        
        # Prepare API request
        payload = {
            "recipients": recipients,
            "message": message,
            "callback_number": callback_number,
            "project_id": current_project_id,
            "channel_id": 1  # SMS channel
        }
        
        headers = {
            "Authorization": f"Bearer {BAAS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Make API call
        response = await client.post(
            f"{API_BASE_URL}/message/sms",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return {
                    "success": True,
                    "group_id": result["data"]["group_id"],
                    "message": "SMS가 성공적으로 전송되었습니다",
                    "sent_count": len(recipients),
                    "failed_count": 0
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error"),
                    "error_code": result.get("error_code", "UNKNOWN_ERROR")
                }
        else:
            return {
                "success": False,
                "error": f"API 호출이 실패했습니다 (상태코드: {response.status_code})",
                "error_code": "API_ERROR"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"SMS 전송에 실패했습니다: {str(e)}",
            "error_code": "INTERNAL_ERROR"
        }

@mcp.tool()
async def send_mms(
    recipients: List[Dict[str, str]],
    message: str,
    subject: str,
    callback_number: str,
    image_urls: Optional[List[str]] = None,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send MMS message with images to one or multiple recipients for rich media marketing and notifications
    
    Perfect for: product catalogs, order confirmations with photos, event invitations, visual promotions
    
    Args:
        recipients: List of recipients with phone_number (Korean format: 010-1234-5678) and member_code (unique identifier)
        message: MMS message content (max 2000 characters, supports Korean text and emojis)
        subject: MMS subject line (max 40 characters, appears as message title)
        callback_number: Sender callback number (your business number)
        image_urls: List of publicly accessible image URLs to attach (max 5 images, JPG/PNG format)
        project_id: Project UUID (optional, uses env var if not provided)
        
    Returns:
        Dictionary with success status, group_id for tracking, and sending statistics
        Use group_id with get_message_status() to check delivery and view analytics
    """
    try:
        # Use provided project_id or fallback to environment variable
        current_project_id = project_id or PROJECT_ID
        if not current_project_id:
            return {
                "success": False,
                "error": "프로젝트 ID가 필요합니다",
                "error_code": "MISSING_PROJECT_ID"
            }
        
        # Validate input
        if not recipients or len(recipients) > 1000:
            return {
                "success": False,
                "error": "수신자 수는 1명 이상 1000명 이하여야 합니다",
                "error_code": "INVALID_RECIPIENTS_COUNT"
            }
        
        if len(message) > 2000:
            return {
                "success": False,
                "error": "메시지 길이가 2000자를 초과했습니다",
                "error_code": "MESSAGE_TOO_LONG"
            }
        
        if len(subject) > 40:
            return {
                "success": False,
                "error": "제목 길이가 40자를 초과했습니다",
                "error_code": "SUBJECT_TOO_LONG"
            }
        
        if image_urls and len(image_urls) > 5:
            return {
                "success": False,
                "error": "최대 5개의 이미지만 첨부 가능합니다",
                "error_code": "TOO_MANY_IMAGES"
            }
        
        # Prepare API request
        payload = {
            "recipients": recipients,
            "message": message,
            "subject": subject,
            "callback_number": callback_number,
            "project_id": current_project_id,
            "channel_id": 3,  # MMS channel
            "img_url_list": image_urls or []
        }
        
        headers = {
            "Authorization": f"Bearer {BAAS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Make API call
        response = await client.post(
            f"{API_BASE_URL}/message/mms",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return {
                    "success": True,
                    "group_id": result["data"]["group_id"],
                    "message": "MMS가 성공적으로 전송되었습니다",
                    "sent_count": len(recipients),
                    "failed_count": 0
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error"),
                    "error_code": result.get("error_code", "UNKNOWN_ERROR")
                }
        else:
            return {
                "success": False,
                "error": f"API 호출이 실패했습니다 (상태코드: {response.status_code})",
                "error_code": "API_ERROR"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"MMS 전송에 실패했습니다: {str(e)}",
            "error_code": "INTERNAL_ERROR"
        }

@mcp.tool()
async def get_message_status(group_id: int) -> Dict[str, Any]:
    """
    Get detailed message delivery status and analytics by group ID for monitoring and debugging
    
    Perfect for: checking delivery success rates, debugging failed messages, generating delivery reports
    
    Args:
        group_id: Message group ID returned from send_sms() or send_mms() functions
        
    Returns:
        Dictionary with overall delivery status, success/failure counts, and individual recipient details
        Status values: "전송중" (sending), "성공" (success), "실패" (failed), "부분성공" (partial success)
    """
    try:
        headers = {
            "Authorization": f"Bearer {BAAS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Make API call to get message status
        response = await client.get(
            f"{API_BASE_URL}/message/send_history/sms/{group_id}/messages",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                messages = result.get("data", [])
                
                # Calculate statistics
                total_count = len(messages)
                success_count = sum(1 for msg in messages if msg.get("result") == "성공")
                failed_count = sum(1 for msg in messages if msg.get("result") == "실패")
                pending_count = total_count - success_count - failed_count
                
                # Determine overall status
                if pending_count > 0:
                    status = "전송중"
                elif failed_count == 0:
                    status = "성공"
                else:
                    status = "실패" if success_count == 0 else "부분성공"
                
                return {
                    "group_id": group_id,
                    "status": status,
                    "total_count": total_count,
                    "success_count": success_count,
                    "failed_count": failed_count,
                    "pending_count": pending_count,
                    "messages": [
                        {
                            "phone": msg.get("phone", ""),
                            "name": msg.get("name", ""),
                            "status": msg.get("result", ""),
                            "reason": msg.get("reason")
                        }
                        for msg in messages
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "메시지 상태 조회에 실패했습니다"),
                    "error_code": result.get("error_code", "UNKNOWN_ERROR")
                }
        else:
            return {
                "success": False,
                "error": f"API 호출이 실패했습니다 (상태코드: {response.status_code})",
                "error_code": "API_ERROR"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"메시지 상태 조회에 실패했습니다: {str(e)}",
            "error_code": "INTERNAL_ERROR"
        }

@mcp.tool()
async def get_send_history(
    project_id: Optional[str] = None,
    offset: int = 0,
    limit: int = 20,
    message_type: str = "ALL"
) -> Dict[str, Any]:
    """
    Get message sending history for a project
    
    Args:
        project_id: Project UUID (optional, uses env var if not provided)
        offset: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 20, max: 100)
        message_type: Filter by message type ("SMS", "MMS", "ALL")
        
    Returns:
        Dictionary with sending history data
    """
    try:
        # Use provided project_id or fallback to environment variable
        current_project_id = project_id or PROJECT_ID
        if not current_project_id:
            return {
                "success": False,
                "error": "프로젝트 ID가 필요합니다",
                "error_code": "MISSING_PROJECT_ID"
            }
        
        # Validate parameters
        if limit > 100:
            limit = 100
        if offset < 0:
            offset = 0
        if message_type not in ["SMS", "MMS", "ALL"]:
            message_type = "ALL"
        
        headers = {
            "Authorization": f"Bearer {BAAS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        params = {
            "offset": offset,
            "limit": limit,
            "message_type": message_type
        }
        
        # Make API call (Note: This endpoint needs to be implemented in the API)
        # For now, return a placeholder response
        return {
            "success": True,
            "data": {
                "project_id": current_project_id,
                "total_count": 0,
                "offset": offset,
                "limit": limit,
                "message_type": message_type,
                "history": []
            },
            "message": "전송 기록 엔드포인트가 아직 API에 구현되지 않았습니다"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"전송 기록 조회에 실패했습니다: {str(e)}",
            "error_code": "INTERNAL_ERROR"
        }

# Cleanup function to close HTTP client
async def cleanup():
    await client.aclose()

def main():
    """BaaS SMS/MCP 서버의 메인 진입점"""
    print("BaaS SMS/MMS MCP 서버를 시작합니다...")
    print(f"API 기본 URL: {API_BASE_URL}")
    print(f"프로젝트 ID: {PROJECT_ID}")
    
    try:
        mcp.run(transport="stdio")
    finally:
        import asyncio
        asyncio.run(cleanup())

# Run the server if the script is executed directly
if __name__ == "__main__":
    main()