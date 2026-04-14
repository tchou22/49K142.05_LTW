import json
import os
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from google import genai
from .models import TuVan, KhieuNai


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def ask_ai(message, history):
    client = get_client()
    if client is None:
        return "Chatbot AI chưa được cấu hình GEMINI_API_KEY."

    context = "\n".join([f"Khách: {h['user']}\nAI: {h['ai']}" for h in history])

    prompt = f"""
Bạn là nhân viên tư vấn của trung tâm Flying Yoga.
Trả lời ngắn gọn, thân thiện, đúng trọng tâm.
Nếu không chắc thông tin thì nói chưa có thông tin chính xác, không được bịa.

Lịch sử trò chuyện gần đây:
{context}

Câu hỏi hiện tại của khách: {message}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return (response.text or "").strip() or "Mình chưa trả lời được câu này. Bạn thử hỏi lại nhé."
    except Exception as e:
        print("GEMINI ERROR:", repr(e))
        return "Hiện chatbot AI đang bận. Bạn vui lòng thử lại sau nhé."


@require_POST
def chat(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        message = data.get("message", "").strip()

        if not message:
            return JsonResponse({"reply": "Bạn hãy nhập nội dung trước nhé."})

        lower_message = message.lower()

        if request.session.get("dang_cho_sdt"):
            tuvan_id = request.session.get("tuvan_id")
            if tuvan_id:
                tuvan = TuVan.objects.filter(id=tuvan_id).first()
                if tuvan:
                    tuvan.sdt = message
                    tuvan.save()

            request.session.pop("dang_cho_sdt", None)
            request.session.pop("tuvan_id", None)

            return JsonResponse({
                "reply": "Cảm ơn bạn! Trung tâm đã nhận được số điện thoại và sẽ liên hệ sớm nhất."
            })

        if "tư vấn" in lower_message or "tu van" in lower_message:
            tuvan = TuVan.objects.create(sdt="unknown", noi_dung=message)
            request.session["dang_cho_sdt"] = True
            request.session["tuvan_id"] = tuvan.id
            reply = "Mình đã ghi nhận yêu cầu tư vấn. Bạn vui lòng để lại số điện thoại để trung tâm liên hệ nhé!"

        elif "khiếu nại" in lower_message or "khieu nai" in lower_message:
            KhieuNai.objects.create(noi_dung=message)
            reply = "Mình đã ghi nhận khiếu nại. Bên mình sẽ xử lý sớm và phản hồi lại cho bạn!"

        else:
            history = request.session.get("chat_history", [])
            reply = ask_ai(message, history)
            history.append({"user": message, "ai": reply})
            request.session["chat_history"] = history[-3:]

        return JsonResponse({"reply": reply})

    except Exception as e:
        print("CHATBOT ERROR:", repr(e))
        return JsonResponse(
            {"reply": "Chatbot đang lỗi. Bạn vui lòng thử lại sau nhé."},
            status=500
        )