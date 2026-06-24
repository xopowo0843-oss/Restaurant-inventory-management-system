"""사업자등록증 / 세금계산서 OCR — Claude Vision API"""

import base64
import json
import os
import re
from io import BytesIO


def _to_base64_images(file_stream, filename: str) -> list[dict]:
    """파일을 base64 이미지 리스트로 변환 (PDF는 각 페이지를 이미지로)"""
    data = file_stream.read()
    ext = filename.rsplit(".", 1)[-1].lower()

    if ext == "pdf":
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=data, filetype="pdf")
            images = []
            for page in doc:
                pix = page.get_pixmap(dpi=200)
                img_bytes = pix.tobytes("png")
                images.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": base64.b64encode(img_bytes).decode(),
                    }
                })
            return images
        except Exception as e:
            raise ValueError(f"PDF 변환 실패: {e}")
    else:
        media_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                     "png": "image/png", "webp": "image/webp"}
        media_type = media_map.get(ext, "image/jpeg")
        return [{
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": base64.b64encode(data).decode(),
            }
        }]


def extract_supplier_info(file_stream, filename: str) -> dict:
    """
    사업자등록증 또는 세금계산서 이미지/PDF에서 공급업체 정보 추출.
    Returns dict with keys: name, business_no, address, phone, email, bank_name,
                            bank_account, bank_holder, memo
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다. .env 파일에 추가해 주세요.")

    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    images = _to_base64_images(file_stream, filename)

    prompt = """이 문서(사업자등록증 또는 세금계산서)에서 공급업체 정보를 추출해 주세요.

다음 JSON 형식으로만 응답하세요. 값을 찾을 수 없으면 빈 문자열("")로 두세요:

{
  "name": "업체명(상호)",
  "business_no": "사업자등록번호 (000-00-00000 형식)",
  "address": "사업장 주소",
  "phone": "전화번호",
  "representative": "대표자명",
  "business_type": "업태/종목",
  "bank_name": "은행명 (세금계산서에 있는 경우)",
  "bank_account": "계좌번호 (세금계산서에 있는 경우)",
  "bank_holder": "예금주 (세금계산서에 있는 경우)",
  "email": "이메일 (있는 경우)",
  "doc_type": "사업자등록증 또는 세금계산서"
}

JSON만 출력하고 다른 설명은 추가하지 마세요."""

    content = images + [{"type": "text", "text": prompt}]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": content}]
    )

    text = response.content[0].text.strip()

    # JSON 파싱
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if not json_match:
        raise ValueError("문서에서 정보를 추출하지 못했습니다.")

    data = json.loads(json_match.group())

    # memo 필드에 대표자, 업태 등 추가 정보 포함
    extra = []
    if data.get("representative"):
        extra.append(f"대표자: {data['representative']}")
    if data.get("business_type"):
        extra.append(f"업태/종목: {data['business_type']}")
    if data.get("doc_type"):
        extra.append(f"문서: {data['doc_type']}")

    return {
        "name": data.get("name", ""),
        "business_no": data.get("business_no", ""),
        "address": data.get("address", ""),
        "phone": data.get("phone", ""),
        "email": data.get("email", ""),
        "bank_name": data.get("bank_name", ""),
        "bank_account": data.get("bank_account", ""),
        "bank_holder": data.get("bank_holder", ""),
        "memo": " / ".join(extra),
    }
