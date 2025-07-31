# BaaS SMS/MCP 서버

[![npm version](https://badge.fury.io/js/baas-sms-mcp.svg)](https://badge.fury.io/js/baas-sms-mcp)
[![PyPI version](https://badge.fury.io/py/baas-sms-mcp.svg)](https://badge.fury.io/py/baas-sms-mcp)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

SMS 및 MMS 메시징 서비스를 위한 모델 컨텍스트 프로토콜(MCP) 서버입니다. 이 서버는 Claude가 개발자들이 웹과 모바일 애플리케이션에서 메시징 기능을 쉽게 구현할 수 있도록 BaaS API 서비스와의 직접 연동을 제공합니다.

## 기능

- **개발자 친화적**: Claude가 애플리케이션용 메시징 코드를 자동으로 생성
- **SMS 발송**: 단일 또는 다중 수신자에게 SMS 메시지 발송
- **MMS 발송**: 이미지 첨부와 함께 MMS 메시지 발송
- **메시지 상태**: 발송 상태 및 전달 확인 체크
- **전송 기록**: 프로젝트별 메시지 전송 기록 조회
- **다중 프레임워크 지원**: React, Vue, Node.js, Python 등과 호환
- **프로젝트 격리**: 프로젝트 기반 접근 제어를 통한 멀티 테넌트 지원
- **에러 핸들링**: 상세한 에러 코드와 함께 포괄적인 에러 처리

## 사용 사례

- **인증**: 사용자 등록/로그인을 위한 SMS 인증 코드
- **알림**: 주문 확인, 배송 업데이트, 알림
- **마케팅**: 프로모션 메시지, 이벤트 알림
- **이중 인증**: 보안 인증 메시지
- **고객 지원**: 자동화된 지원 메시지 및 업데이트

## 설치

### npm 사용 (권장)

```bash
npm install -g baas-sms-mcp
```

또는 설치 없이 바로 실행:
```bash
npx baas-sms-mcp
```

### pip 사용

```bash
pip install baas-sms-mcp
```

### 소스에서 설치

```bash
git clone https://github.com/your-org/baas-sms-mcp.git
cd baas-sms-mcp
npm install
```

## 설정

다음 환경변수를 설정하세요:

```bash
export BAAS_API_KEY="your_baas_api_key_here"  
export PROJECT_ID="your_project_uuid_here"
```

참고: `BAAS_API_BASE_URL`은 `https://api.aiapp.link`로 고정되어 있어 설정할 필요가 없습니다.

## 사용법

### 명령줄

설치 후 서버를 직접 실행할 수 있습니다:

```bash
baas-sms-mcp
```

### Claude Desktop과 함께 사용

Claude Desktop 설정에 이 서버를 추가하세요:

```json
{
  "mcpServers": {
    "baas-sms-mcp": {
      "command": "npx",
      "args": ["baas-sms-mcp"],
      "env": {
        "BAAS_API_KEY": "your_api_key",
        "PROJECT_ID": "your_project_id"
      }
    }
  }
}
```

또는 전역으로 설치한 경우:

```json
{
  "mcpServers": {
    "baas-sms-mcp": {
      "command": "baas-sms-mcp",
      "env": {
        "BAAS_API_KEY": "your_api_key",
        "PROJECT_ID": "your_project_id"
      }
    }
  }
}
```

### 프로그래밍 방식 사용

```python
from baas_sms_mcp import main

# MCP 서버 실행
main()
```

## 개발자 예제

### 예제 1: SMS 인증을 통한 사용자 등록

**Claude에게 요청:**
> "SMS 인증 코드를 보내는 사용자 등록 API를 만들어주세요"

**Claude가 생성할 코드:**

```javascript
// Node.js/Express 예제
app.post('/register', async (req, res) => {
  const { phoneNumber, username } = req.body;
  
  // 인증 코드 생성
  const verificationCode = Math.floor(100000 + Math.random() * 900000);
  
  // BaaS MCP를 사용하여 SMS 발송
  const smsResult = await sendSMS({
    recipients: [{ phone_number: phoneNumber, member_code: username }],
    message: `인증 코드는 ${verificationCode} 입니다`,
    callback_number: "02-1234-5678"
  });
  
  if (smsResult.success) {
    // 데이터베이스에 인증 코드 저장
    await saveVerificationCode(phoneNumber, verificationCode);
    res.json({ success: true, message: "인증 코드가 전송되었습니다" });
  } else {
    res.status(500).json({ error: "SMS 전송에 실패했습니다" });
  }
});
```

### 예제 2: 주문 확인 MMS

**Claude에게 요청:**
> "주문이 완료되면 주문 상세 정보와 상품 이미지를 MMS로 보내는 기능을 만들어주세요"

**Claude가 생성할 코드:**

```python
# Python/Django 예제
def send_order_confirmation(order_id, customer_phone):
    order = Order.objects.get(id=order_id)
    
    message = f"""
    주문 확인 #{order.id}
    
    상품: {order.get_items_summary()}
    총액: {order.total}원
    
    주문해 주셔서 감사합니다!
    """
    
    # 상품 이미지와 함께 MMS 발송
    result = send_mms(
        recipients=[{
            "phone_number": customer_phone,
            "member_code": f"customer_{order.customer.id}"
        }],
        message=message,
        subject="주문 확인",
        callback_number="02-1234-5678",
        image_urls=[order.get_product_image_url()]
    )
    
    return result
```

### 예제 3: 실시간 상태 확인

**Claude에게 요청:**
> "SMS 전달 상태를 확인하는 웹훅 엔드포인트를 만들어주세요"

**Claude가 생성할 코드:**

```javascript
// 실시간 상태 확인
app.get('/sms-status/:groupId', async (req, res) => {
  const { groupId } = req.params;
  
  try {
    const status = await checkMessageStatus(groupId);
    
    res.json({
      groupId: status.group_id,
      status: status.status,
      delivered: status.success_count,
      failed: status.failed_count,
      pending: status.pending_count,
      messages: status.messages
    });
  } catch (error) {
    res.status(500).json({ error: "상태 확인에 실패했습니다" });
  }
});
```

## 사용 가능한 도구

### 1. send_sms

사용자 인증, 알림 또는 마케팅 캠페인을 위해 한 명 또는 여러 명의 수신자에게 SMS 메시지를 발송합니다.

다음에 완벽: 사용자 등록 인증, 주문 확인, 2FA 코드, 프로모션 메시지

**매개변수:**
- `recipients`: phone_number(한국 형식: 010-1234-5678)와 member_code(고유 식별자)가 포함된 수신자 목록
- `message`: SMS 메시지 내용 (최대 2000자, 한국어 텍스트 지원)
- `callback_number`: 발신자 콜백 번호 (회사 번호)
- `project_id`: 프로젝트 UUID (선택사항, 제공되지 않으면 환경변수 사용)

**예제:**
```python
await send_sms(
    recipients=[
        {"phone_number": "010-1234-5678", "member_code": "user123"}
    ],
    message="안녕하세요, 테스트 SMS입니다!",
    callback_number="02-1234-5678"
)
```

**응답:**
```json
{
    "success": true,
    "group_id": 12345,
    "message": "SMS가 성공적으로 전송되었습니다",
    "sent_count": 1,
    "failed_count": 0
}
```

### 2. send_mms

리치 미디어 마케팅 및 알림을 위해 이미지와 함께 MMS 메시지를 한 명 또는 여러 명의 수신자에게 발송합니다.

다음에 완벽: 상품 카탈로그, 사진이 포함된 주문 확인, 이벤트 초대장, 시각적 프로모션

**매개변수:**
- `recipients`: phone_number(한국 형식: 010-1234-5678)와 member_code(고유 식별자)가 포함된 수신자 목록
- `message`: MMS 메시지 내용 (최대 2000자, 한국어 텍스트 및 이모지 지원)
- `subject`: MMS 제목 (최대 40자, 메시지 제목으로 표시됨)
- `callback_number`: 발신자 콜백 번호 (회사 번호)
- `image_urls`: 첨부할 공개 접근 가능한 이미지 URL 목록 (최대 5개 이미지, JPG/PNG 형식)
- `project_id`: 프로젝트 UUID (선택사항, 제공되지 않으면 환경변수 사용)

**예제:**
```python
await send_mms(
    recipients=[
        {"phone_number": "010-1234-5678", "member_code": "user123"}
    ],
    message="이 이미지를 확인해보세요!",
    subject="이미지 MMS",
    callback_number="02-1234-5678",
    image_urls=["https://example.com/image.jpg"]
)
```

### 3. get_message_status

모니터링 및 디버깅을 위해 그룹 ID로 상세한 메시지 전달 상태 및 분석을 가져옵니다.

다음에 완벽: 전달 성공률 확인, 실패한 메시지 디버깅, 전달 보고서 생성

**매개변수:**
- `group_id`: send_sms() 또는 send_mms() 함수에서 반환된 메시지 그룹 ID

**응답:**
```json
{
    "group_id": 12345,
    "status": "성공",
    "total_count": 1,
    "success_count": 1,
    "failed_count": 0,
    "pending_count": 0,
    "messages": [
        {
            "phone": "010-1234-5678",
            "name": "홍길동",
            "status": "성공",
            "reason": null
        }
    ]
}
```

### 4. get_send_history

프로젝트의 메시지 전송 기록을 가져옵니다.

**매개변수:**
- `project_id`: 프로젝트 UUID (선택사항, 제공되지 않으면 환경변수 사용)
- `offset`: 건너뛸 레코드 수 (기본값: 0)
- `limit`: 반환할 최대 레코드 수 (기본값: 20, 최대: 100)
- `message_type`: 메시지 유형별 필터 ("SMS", "MMS", "ALL")

## 빠른 시작 템플릿

### 인증 서비스 템플릿

```javascript
// Express.js SMS 인증 서비스
const express = require('express');
const app = express();

// 인증 코드 저장 (프로덕션에서는 Redis/Database 사용)
const verificationCodes = new Map();

app.post('/send-verification', async (req, res) => {
  const { phoneNumber, memberCode } = req.body;
  const code = Math.floor(100000 + Math.random() * 900000);
  
  // 5분 만료 시간으로 코드 저장
  verificationCodes.set(phoneNumber, {
    code,
    expires: Date.now() + 5 * 60 * 1000
  });
  
  // Claude가 MCP 서버를 사용하여 SMS 발송
  const result = await sendSMS({
    recipients: [{ phone_number: phoneNumber, member_code: memberCode }],
    message: `인증 코드: ${code}`,
    callback_number: "02-1234-5678"
  });
  
  res.json({ success: result.success });
});

app.post('/verify-code', (req, res) => {
  const { phoneNumber, code } = req.body;
  const stored = verificationCodes.get(phoneNumber);
  
  if (stored && stored.code == code && Date.now() < stored.expires) {
    verificationCodes.delete(phoneNumber);
    res.json({ success: true, message: "인증 완료!" });
  } else {
    res.json({ success: false, message: "잘못되거나 만료된 코드입니다" });
  }
});
```

## 에러 처리

서버는 다음 에러 코드와 함께 포괄적인 에러 처리를 제공합니다:

- `MISSING_PROJECT_ID`: 프로젝트 ID가 필요합니다
- `INVALID_RECIPIENTS_COUNT`: 수신자 수는 1명 이상 1000명 이하여야 합니다
- `MESSAGE_TOO_LONG`: 메시지 길이가 최대 허용 길이를 초과했습니다
- `SUBJECT_TOO_LONG`: 제목 길이가 40자를 초과했습니다
- `TOO_MANY_IMAGES`: MMS의 경우 최대 5개 이미지만 허용됩니다
- `API_ERROR`: 외부 API 호출이 실패했습니다
- `INTERNAL_ERROR`: 내부 서버 에러

## API 연동

이 MCP 서버는 BaaS API 엔드포인트와 연동됩니다:

- `POST /message/sms` - SMS 메시지 발송
- `POST /message/mms` - MMS 메시지 발송
- `GET /message/send_history/sms/{group_id}/messages` - 메시지 상태 가져오기

## 개발

### 개발 의존성 설치

```bash
uv sync --group dev
```

### 코드 포맷팅

```bash
uv run black baas_sms_mcp/
```

### 타입 체크

```bash
uv run mypy baas_sms_mcp/
```

### 테스트

```bash
uv run pytest
```

### 패키지 빌드

```bash
uv build
```

### PyPI에 배포

```bash
uv publish
```

## 라이선스

MIT 라이선스 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 지원

지원 및 문의사항은 support@aiapp.link로 연락하세요.

## 언어

- [English](README.md)
- [한국어](README.ko.md)