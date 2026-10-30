import json
import os
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from google import genai
from .models import TuVan, KhieuNai

from goi_tap.models import GoiTap
from lich_tap.models import LichHoc


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

def get_goi_tap_context():
    goi_taps = GoiTap.objects.filter(trang_thai="hoat_dong").order_by("gia_goi")

    if not goi_taps.exists():
        return "Hiện chưa có gói tập đang hoạt động trong hệ thống."

    lines = ["DANH SÁCH GÓI TẬP ĐANG HOẠT ĐỘNG:"]

    for goi in goi_taps:
        lines.append(
            f"- Mã gói: {goi.ma_goi}\n"
            f"  Tên gói: {goi.ten_goi}\n"
            f"  Loại gói: {goi.get_loai_goi_display()}\n"
            f"  Thời hạn / số buổi: {goi.thoi_han_so_buoi}\n"
            f"  Giá: {goi.gia_goi:,.0f} VNĐ\n"
            f"  Ghi chú: {goi.ghi_chu or 'Không có'}"
        )

    return "\n".join(lines)


def get_lich_tap_context():
    lich_hocs = (
        LichHoc.objects
        .filter(trang_thai=True)
        .select_related("goi_tap")
        .order_by("thu", "gio_bat_dau")
    )

    if not lich_hocs.exists():
        return "Hiện chưa có lịch học đang hoạt động trong hệ thống."

    lines = ["DANH SÁCH LỊCH HỌC ĐANG HOẠT ĐỘNG:"]

    for lich in lich_hocs:
        lines.append(
            f"- Mã lịch: {lich.ma_lich}\n"
            f"  Gói tập: {lich.goi_tap.ten_goi}\n"
            f"  Thời gian: {lich.get_thu_display()}, "
            f"{lich.gio_bat_dau.strftime('%H:%M')} - {lich.gio_ket_thuc.strftime('%H:%M')}\n"
            f"  Phòng: {lich.phong}\n"
            f"  HLV phụ trách: {lich.hlv_phu_trach}\n"
            f"  Số chỗ tối đa: {lich.so_cho_toi_da}"
        )

    return "\n".join(lines)


def build_project_context(message):
    lower_message = message.lower()
    contexts = []

    if (
        "gói" in lower_message
        or "goi" in lower_message
        or "giá" in lower_message
        or "gia" in lower_message
        or "học phí" in lower_message
        or "hoc phi" in lower_message
    ):
        contexts.append(get_goi_tap_context())

    if (
        "lịch" in lower_message
        or "lich" in lower_message
        or "giờ học" in lower_message
        or "gio hoc" in lower_message
        or "hlv" in lower_message
        or "phòng" in lower_message
        or "phong" in lower_message
    ):
        contexts.append(get_lich_tap_context())

    if not contexts:
        contexts.append(
            "THÔNG TIN TRUNG TÂM:\n"
            "- Trung tâm Flying Yoga có các chức năng: quản lý hội viên, gói tập, lịch học, đăng ký lịch, tư vấn, khiếu nại/phản hồi, tích điểm và thông báo.\n"
            "- Nếu khách hỏi về gói tập hoặc lịch học thì ưu tiên giới thiệu theo dữ liệu hệ thống."
        )

    return "\n\n".join(contexts)


def ask_ai(message, history):
    client = get_client()
    if client is None:
        return "Chatbot AI chưa được cấu hình GEMINI_API_KEY."

    context = "\n".join([f"Khách: {h['user']}\nAI: {h['ai']}" for h in history])

    project_context = build_project_context(message)

    prompt = f"""
Bạn là nhân viên tư vấn của trung tâm Flying Yoga.

Yêu cầu trả lời:
- Trả lời bằng tiếng Việt.
- Giọng thân thiện, dễ hiểu, giống nhân viên tư vấn thật.
- Chỉ sử dụng thông tin có trong dữ liệu hệ thống bên dưới.
- Không được bịa thêm giá, lịch, HLV hoặc gói tập nếu dữ liệu không có.
- Nếu khách hỏi gói tập thì liệt kê tên gói, loại gói, số buổi/thời hạn, giá và ghi chú.
- Nếu khách hỏi lịch tập thì liệt kê thứ, giờ học, phòng, HLV và gói tập tương ứng.
- Nếu thông tin chưa đủ thì mời khách để lại số điện thoại để được tư vấn thêm.

DỮ LIỆU HỆ THỐNG:
{project_context}

Lịch sử trò chuyện gần đây:
{context}

Câu hỏi hiện tại của khách:
{message}
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