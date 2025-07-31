# MCP 서버 데이터 모델 정의

## 개요

FastSDK를 사용하여 SMS/MMS 기능을 제공하는 MCP 서버 구축을 위한 데이터 모델을 정의합니다.

## MCP 서버 아키텍처

### 서버 구성 요소
```
MCP Server (FastSDK)
├── Tools (도구)
│   ├── send_sms
│   ├── send_mms
│   ├── get_message_status
│   └── get_send_history
├── Resources (리소스)
│   ├── message_templates
│   ├── recipient_groups
│   └── send_statistics
└── Prompts (프롬프트)
    ├── compose_sms
    ├── compose_mms
    └── analyze_send_results
```

## Tools 정의

### 1. send_sms Tool

#### 기능
단일 또는 복수의 수신자에게 SMS를 발송합니다.

#### 입력 스키마
```json
{
  "name": "send_sms",
  "description": "Send SMS message to one or multiple recipients",
  "inputSchema": {
    "type": "object",
    "properties": {
      "project_id": {
        "type": "string",
        "format": "uuid",
        "description": "Project UUID for multi-tenant isolation"
      },
      "recipients": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "phone_number": {
              "type": "string",
              "pattern": "^010-\\d{4}-\\d{4}$",
              "description": "Recipient phone number in Korean format"
            },
            "member_code": {
              "type": "string",
              "description": "Unique member identifier"
            }
          },
          "required": ["phone_number", "member_code"]
        },
        "minItems": 1,
        "maxItems": 1000,
        "description": "List of recipients"
      },
      "message": {
        "type": "string",
        "maxLength": 2000,
        "description": "SMS message content"
      },
      "callback_number": {
        "type": "string",
        "pattern": "^(?:\\d{2,4}-\\d{3,4}-\\d{4}|\\d{4}-\\d{4})$",
        "description": "Sender callback number"
      }
    },
    "required": ["project_id", "recipients", "message", "callback_number"]
  }
}
```

#### 출력 스키마
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Operation success status"
    },
    "group_id": {
      "type": "integer",
      "description": "Message group ID for tracking"
    },
    "message": {
      "type": "string",
      "description": "Result message"
    },
    "sent_count": {
      "type": "integer",
      "description": "Number of messages sent successfully"
    },
    "failed_count": {
      "type": "integer",
      "description": "Number of failed messages"
    }
  }
}
```

### 2. send_mms Tool

#### 기능
단일 또는 복수의 수신자에게 MMS를 발송합니다.

#### 입력 스키마
```json
{
  "name": "send_mms",
  "description": "Send MMS message with images to one or multiple recipients",
  "inputSchema": {
    "type": "object",
    "properties": {
      "project_id": {
        "type": "string",
        "format": "uuid",
        "description": "Project UUID for multi-tenant isolation"
      },
      "recipients": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "phone_number": {
              "type": "string",
              "pattern": "^010-\\d{4}-\\d{4}$"
            },
            "member_code": {
              "type": "string"
            }
          },
          "required": ["phone_number", "member_code"]
        },
        "minItems": 1,
        "maxItems": 1000
      },
      "message": {
        "type": "string",
        "maxLength": 2000,
        "description": "MMS message content"
      },
      "subject": {
        "type": "string",
        "maxLength": 40,
        "description": "MMS subject line"
      },
      "callback_number": {
        "type": "string",
        "pattern": "^(?:\\d{2,4}-\\d{3,4}-\\d{4}|\\d{4}-\\d{4})$"
      },
      "image_urls": {
        "type": "array",
        "items": {
          "type": "string",
          "format": "uri",
          "description": "Image URL (must be accessible)"
        },
        "maxItems": 5,
        "description": "List of image URLs to attach"
      }
    },
    "required": ["project_id", "recipients", "message", "subject", "callback_number"]
  }
}
```

### 3. get_message_status Tool

#### 기능
메시지 그룹의 발송 상태를 조회합니다.

#### 입력 스키마
```json
{
  "name": "get_message_status",
  "description": "Get message sending status by group ID",
  "inputSchema": {
    "type": "object",
    "properties": {
      "group_id": {
        "type": "integer",
        "description": "Message group ID to check status"
      }
    },
    "required": ["group_id"]
  }
}
```

#### 출력 스키마
```json
{
  "type": "object",
  "properties": {
    "group_id": {
      "type": "integer"
    },
    "status": {
      "type": "string",
      "enum": ["전송중", "성공", "실패"],
      "description": "Overall group status"
    },
    "total_count": {
      "type": "integer",
      "description": "Total number of messages in group"
    },
    "success_count": {
      "type": "integer",
      "description": "Number of successfully sent messages"
    },
    "failed_count": {
      "type": "integer",
      "description": "Number of failed messages"
    },
    "pending_count": {
      "type": "integer",
      "description": "Number of pending messages"
    },
    "messages": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "phone": {
            "type": "string"
          },
          "name": {
            "type": "string"
          },
          "status": {
            "type": "string",
            "enum": ["전송중", "성공", "실패"]
          },
          "reason": {
            "type": "string",
            "description": "Failure reason if applicable"
          }
        }
      }
    }
  }
}
```

### 4. get_send_history Tool

#### 기능
프로젝트의 메시지 발송 이력을 조회합니다.

#### 입력 스키마
```json
{
  "name": "get_send_history",
  "description": "Get message sending history for a project",
  "inputSchema": {
    "type": "object",
    "properties": {
      "project_id": {
        "type": "string",
        "format": "uuid"
      },
      "offset": {
        "type": "integer",
        "minimum": 0,
        "default": 0,
        "description": "Number of records to skip"
      },
      "limit": {
        "type": "integer",
        "minimum": 1,
        "maximum": 100,
        "default": 20,
        "description": "Maximum number of records to return"
      },
      "message_type": {
        "type": "string",
        "enum": ["SMS", "MMS", "ALL"],
        "default": "ALL",
        "description": "Filter by message type"
      }
    },
    "required": ["project_id"]
  }
}
```

## Resources 정의

### 1. message_templates Resource

#### 기능
메시지 템플릿 관리 및 조회

#### 스키마
```json
{
  "uri": "message-templates://",
  "name": "Message Templates",
  "description": "Manage and retrieve message templates",
  "mimeType": "application/json"
}
```

### 2. recipient_groups Resource

#### 기능
수신자 그룹 관리

#### 스키마
```json
{
  "uri": "recipient-groups://",
  "name": "Recipient Groups",
  "description": "Manage recipient groups for batch messaging",
  "mimeType": "application/json"
}
```

### 3. send_statistics Resource

#### 기능
발송 통계 데이터 조회

#### 스키마
```json
{
  "uri": "send-statistics://",
  "name": "Send Statistics",
  "description": "View messaging statistics and analytics",
  "mimeType": "application/json"
}
```

## Prompts 정의

### 1. compose_sms Prompt

#### 기능
SMS 메시지 작성 도움

```json
{
  "name": "compose_sms",
  "description": "Help compose effective SMS messages",
  "arguments": [
    {
      "name": "purpose",
      "description": "Purpose of the SMS (marketing, notification, etc.)",
      "required": true
    },
    {
      "name": "target_audience",
      "description": "Target audience characteristics",
      "required": false
    },
    {
      "name": "key_message",
      "description": "Key message to convey",
      "required": true
    }
  ]
}
```

### 2. compose_mms Prompt

#### 기능
MMS 메시지 및 이미지 조합 제안

```json
{
  "name": "compose_mms",
  "description": "Help compose MMS messages with image suggestions",
  "arguments": [
    {
      "name": "campaign_type",
      "description": "Type of campaign (promotional, informational, etc.)",
      "required": true
    },
    {
      "name": "product_service",
      "description": "Product or service being promoted",
      "required": false
    },
    {
      "name": "image_style",
      "description": "Preferred image style or format",
      "required": false
    }
  ]
}
```

### 3. analyze_send_results Prompt

#### 기능
발송 결과 분석 및 개선 제안

```json
{
  "name": "analyze_send_results",
  "description": "Analyze sending results and provide improvement suggestions",
  "arguments": [
    {
      "name": "group_id",
      "description": "Message group ID to analyze",
      "required": true
    },
    {
      "name": "analysis_type",
      "description": "Type of analysis (performance, failure_analysis, etc.)",
      "required": false
    }
  ]
}
```

## 에러 처리 모델

### 표준 에러 응답
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {
      "field": "string",
      "reason": "string"
    }
  }
}
```

### 에러 코드 정의
- `INVALID_PROJECT`: 잘못된 프로젝트 ID
- `AUTHENTICATION_FAILED`: 인증 실패
- `INVALID_PHONE_NUMBER`: 잘못된 전화번호 형식
- `MESSAGE_TOO_LONG`: 메시지 길이 초과
- `RECIPIENT_NOT_FOUND`: 수신자를 찾을 수 없음
- `EXTERNAL_API_ERROR`: 외부 벤더 API 오류
- `RATE_LIMIT_EXCEEDED`: 발송 한도 초과

## 설정 파라미터

### 서버 설정
```json
{
  "server": {
    "name": "SMS-MMS-MCP-Server",
    "version": "1.0.0",
    "api_base_url": "http://localhost:8000",
    "authentication": {
      "type": "jwt",
      "token_header": "Authorization"
    }
  },
  "limits": {
    "max_recipients_per_request": 1000,
    "max_message_length": 2000,
    "max_images_per_mms": 5,
    "rate_limit_per_minute": 100
  },
  "vendors": {
    "default": "telnet",
    "fallback": "uracle"
  }
}
```

## 보안 고려사항

### 인증 및 권한
- JWT 토큰 기반 인증
- 프로젝트별 리소스 격리
- API 호출 로깅 및 감사

### 데이터 보호
- 개인정보 마스킹 처리
- 전송 데이터 암호화
- 로그 데이터 보안 저장

### 요청 제한
- 요청 빈도 제한 (Rate Limiting)
- 대량 발송 시 배치 크기 제한
- 동시 연결 수 제한

## 성능 최적화

### 캐싱 전략
- 수신자 그룹 정보 캐싱
- 템플릿 데이터 캐싱
- 발송 통계 임시 저장

### 비동기 처리
- 대량 발송 시 백그라운드 처리
- 외부 API 호출 비동기화
- 상태 업데이트 큐잉

### 모니터링
- API 응답 시간 모니터링
- 발송 성공률 추적
- 외부 벤더 API 상태 확인

## FastSDK 구현 가이드

### 서버 초기화
```python
from fastsdk import FastMCP

server = FastMCP("sms-mms-server")

# Tools 등록
server.tool(send_sms)
server.tool(send_mms)
server.tool(get_message_status)
server.tool(get_send_history)

# Resources 등록
server.resource(message_templates)
server.resource(recipient_groups)
server.resource(send_statistics)

# Prompts 등록
server.prompt(compose_sms)
server.prompt(compose_mms)
server.prompt(analyze_send_results)
```

### 도구 구현 예시
```python
@server.tool()
async def send_sms(
    project_id: str,
    recipients: List[dict],
    message: str,
    callback_number: str
) -> dict:
    # API 호출 및 결과 반@환 로직
    pass
```

이 데이터 모델 정의를 기반으로 FastSDK를 사용하여 MCP 서버를 구축하면, SMS/MMS 기능을 효과적으로 제공할 수 있습니다.