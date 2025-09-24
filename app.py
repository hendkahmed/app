
import hashlib
import json
from datetime import datetime, timedelta, date
import streamlit as st

# ------------------------
# Perinvo — Daily Wisdom (Streamlit)
# ------------------------
st.set_page_config(
    page_title="Perinvo — Daily Wisdom",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

PERINVO_LOGO = "https://perinvo.com/wp-content/uploads/2025/07/111111111111111-2.png"

# ---- Custom CSS ----
st.markdown(
    """
    <style>
      :root {
        --primary: #003060;
        --secondary: #00C0D0;
      }
      .perinvo-card {
        background: var(--background-color, #ffffff);
        border-radius: 18px;
        box-shadow: 0 10px 35px rgba(0,0,0,.08);
        padding: 20px;
        margin: 14px 0;
      }
      .perinvo-title {
        font-weight: 900; font-size: 26px; margin: 0;
      }
      .perinvo-sub {
        font-size: 12px; opacity: .8;
      }
      .chip {
        display:inline-block; background:#e6fbff; color:#003b45; padding:6px 10px; border-radius:999px; font-size:12px; margin-right:6px;
      }
      .muted { color: #64748b; font-size: 13px; }
      .quote { font-weight: 800; font-size: 24px; margin-top: 6px; }
      .advice { font-size: 18px; margin-top: 4px; }
      .why { color: #64748b; font-size: 14px; margin-top: 6px; }
      .btn-row .stButton>button { border-radius:12px; padding:8px 14px; font-weight:700; }
      .header-wrap { display:flex; align-items:center; gap:12px; }
      .header-wrap img { width:40px; height:40px; border-radius:12px; }
      .footer { color:#64748b; font-size:12px; display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- Data: Original aphorisms ----
DATA = [
    dict(t_ar="اترك أثراً لا أثراً ضجيج.", t_en="Leave a mark, not a noise.", k="impact", a_ar="اسأل نفسك: ما الأثر الصغير الذي أستطيع صنعه اليوم؟", a_en="Ask: what's the smallest impact I can make today?"),
    dict(t_ar="من لا يخطّط؛ يخطّط للفوضى.", t_en="If you don't plan, you plan for chaos.", k="planning", a_ar="اكتب ثلاثة أهداف واضحة لهذا اليوم.", a_en="Write three clear goals for the day."),
    dict(t_ar="الزمن لا يكرم المتردد.", t_en="Time rarely honors hesitation.", k="decisiveness", a_ar="اتخذ قراراً مؤجلاً منذ أسبوع.", a_en="Make one decision you've delayed for a week."),
    dict(t_ar="الإنجاز ابنُ الاتساق.", t_en="Achievement is the child of consistency.", k="consistency", a_ar="خمس عشرة دقيقة يوميًا تفعل الأعاجيب.", a_en="Fifteen daily minutes can move mountains."),
    dict(t_ar="شكراً تصنع فريقاً؛ وعتاباً بلا لطف يهدم.", t_en="Gratitude builds teams; harsh blame breaks them.", k="team", a_ar="اشكر زميلاً على مساهمة محددة.", a_en="Thank a teammate for a specific contribution."),
    dict(t_ar="اعمل بذكاء ثم بجهد.", t_en="Work smart, then hard.", k="smart", a_ar="إلغِ مهمة لا تضيف قيمة.", a_en="Eliminate one low-value task."),
    dict(t_ar="كل يوم فرصة لإعادة التعريف.", t_en="Each day is a chance to redefine.", k="renewal", a_ar="ابدأ الصفحة من جديد ولو بسطر.", a_en="Start a new page—even with one line."),
    dict(t_ar="التوازن قرار متجدد.", t_en="Balance is a renewed decision.", k="balance", a_ar="حدد ساعة صامتة بلا إشعارات.", a_en="Pick one silent hour—no notifications."),
    dict(t_ar="التعلّم السريع يهزم الكمال البطيء.", t_en="Fast learning beats slow perfection.", k="learning", a_ar="جرّب نسخة مبكرة من فكرتك.", a_en="Ship an early version of your idea."),
    dict(t_ar="الكلمات جسور أو جدران.", t_en="Words are bridges or walls.", k="communication", a_ar="أعد صياغة رسالة بنبرة بنّاءة.", a_en="Rewrite a message with a constructive tone."),
    dict(t_ar="أقوى استثمار: صحتك.", t_en="Your strongest investment is your health.", k="health", a_ar="امشِ عشر دقائق بعد الأكل.", a_en="Walk ten minutes after lunch."),
    dict(t_ar="الفرصة تطرق باب المستعد.", t_en="Opportunity knocks on the prepared.", k="opportunity", a_ar="جهّز قائمة مهارات تريد تطويرها.", a_en="List a skill you will sharpen next."),
    dict(t_ar="تغيير واحد يغيّر أشياء كثيرة.", t_en="One change shifts many things.", k="change", a_ar="ابدأ بعادة صغيرة قابلة للقياس.", a_en="Start one tiny, measurable habit."),
    dict(t_ar="الهدوء شجاعة بلا ضجيج.", t_en="Calm is courage without noise.", k="calm", a_ar="تنفّس 4×4×4 لمدة دقيقة.", a_en="Do a 4×4×4 breathing minute."),
    dict(t_ar="النية بوابة الاتجاه.", t_en="Intention is the gateway to direction.", k="intent", a_ar="حدّد نية عملك قبل أن تبدأ.", a_en="Set an intention before you begin."),
    dict(t_ar="المعلومة بلا تطبيق زخرفة.", t_en="Knowledge without application is decoration.", k="action", a_ar="طبّق فكرة واحدة قرأتها أمس.", a_en="Apply one idea you read yesterday."),
    dict(t_ar="الصداقة صيانة.", t_en="Friendship needs maintenance.", k="relationships", a_ar="أرسل رسالة ود صادقة لشخص عزيز.", a_en="Send a sincere note to a friend."),
    dict(t_ar="لا تنتظر المزاج؛ اصنعه.", t_en="Don't wait for mood; make it.", k="energy", a_ar="سماع مقطع موسيقي يرفع طاقتك.", a_en="Play a short energizing track."),
    dict(t_ar="الفشل معلّم مُكلف لكنه صادق.", t_en="Failure is an expensive but honest teacher.", k="failure", a_ar="اكتب درساً واحداً من إخفاق قديم.", a_en="Write one lesson from a past failure."),
    dict(t_ar="الوقت الذي تعطيه لعقلك يردّه لك مضاعفاً.", t_en="Time you give your mind returns with interest.", k="focus", a_ar="أغلق التبويبات وركّز 25 دقيقة.", a_en="Close tabs and focus for 25 minutes."),
]

AR = "العربية"
EN = "English"

CATS_AR = dict(impact="أثر", planning="تخطيط", decisiveness="حسم", consistency="اتساق", team="فريق", smart="ذكاء",
               renewal="تجديد", balance="توازن", learning="تعلّم", communication="تواصل", health="صحة",
               opportunity="فرصة", change="تغيير", calm="هدوء", intent="نية", action="تطبيق", relationships="علاقات",
               energy="طاقة", failure="تعلّم", focus="تركيز")

CATS_EN = dict(impact="Impact", planning="Planning", decisiveness="Decisiveness", consistency="Consistency", team="Team",
               smart="Smart", renewal="Renewal", balance="Balance", learning="Learning", communication="Communication",
               health="Health", opportunity="Opportunity", change="Change", calm="Calm", intent="Intention",
               action="Action", relationships="Relationships", energy="Energy", failure="Learning", focus="Focus")

def pick_index(n: int, seed: str) -> int:
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return int(h[:8], 16) % n

# ------------------------ UI Header ------------------------
col1, col2 = st.columns([1, 7], vertical_alignment="center")
with col1:
    st.image(PERINVO_LOGO, width=46)
with col2:
    st.markdown("<h1 class='perinvo-title'>Perinvo — Daily Wisdom</h1>", unsafe_allow_html=True)
    st.markdown("<div class='perinvo-sub'>Auto-Rotate • AR/EN • Copy & Share</div>", unsafe_allow_html=True)

st.divider()

# ------------------------ Controls ------------------------
left, right = st.columns([2,1])
with left:
    lang = st.radio("Language / اللغة", [AR, EN], horizontal=True, index=0)
with right:
    preview = st.toggle("Preview tomorrow")

# Custom list (JSON)
with st.expander("Customize list (optional) — JSON of wisdom items", expanded=False):
    sample_json = json.dumps(DATA[:3], ensure_ascii=False, indent=2)
    custom = st.text_area("Paste list here to override (leave empty to use default):", height=180, value="")
    if custom.strip():
        try:
            DATA = json.loads(custom)
            st.success("Custom list loaded.")
        except Exception as e:
            st.error(f"Invalid JSON: {e}")

# ------------------------ Logic ------------------------
today = date.today()
target_day = today + timedelta(days=1) if preview else today
seed = f"{target_day.isoformat()}-perinvo"
idx = pick_index(len(DATA), seed)
item = DATA[idx]

is_ar = (lang == AR)

quote = item["t_ar"] if is_ar else item["t_en"]
advice = item["a_ar"] if is_ar else item["a_en"]
cat = item.get("k", "")
cat_label = (dict(**CATS_AR).get(cat, "حكمة") if is_ar else dict(**CATS_EN).get(cat, "Wisdom"))

# ------------------------ Display Card ------------------------
st.markdown('<div class="perinvo-card">', unsafe_allow_html=True)

colA, colB = st.columns([3,2])
with colA:
    st.caption(datetime.now().strftime("%A, %B %d, %Y") if not is_ar else today.strftime("%A, %d %B %Y"))
with colB:
    # Session-only streak (note: does not persist across sessions)
    if "streak" not in st.session_state:
        st.session_state.streak = 1
        st.session_state.last_date = today.isoformat()
    else:
        if st.session_state.last_date != today.isoformat() and not preview:
            st.session_state.streak = (st.session_state.streak or 0) + 1
            st.session_state.last_date = today.isoformat()
    st.markdown(f"**🔥 Streak:** {st.session_state.streak}")

# Chips
st.markdown(f"<span class='chip'>#{cat_label}</span>", unsafe_allow_html=True)

st.markdown(f"<div class='quote'>“{quote}”</div>", unsafe_allow_html=True)
st.markdown(f"<div class='advice'>{advice}</div>", unsafe_allow_html=True)

why_text = ("لماذا هذه اليوم؟ التركيز: " + cat_label) if is_ar else ("Why this today? Focus: " + cat_label)
st.markdown(f"<div class='why'>{why_text}</div>", unsafe_allow_html=True)

# Buttons
st.markdown('<div class="btn-row">', unsafe_allow_html=True)
colx, coly, colz = st.columns(3)
with colx:
    if st.button("📋 Copy / نسخ"):
        clip = f"🧠 Perinvo — Daily Wisdom\\n\\n“{quote}”\\n\\n{('نصيحة' if is_ar else 'Advice')}: {advice}"
        st.code(clip, language="text")
        st.success("Copied text is ready. (Streamlit may require manual copy)")
with coly:
    share_txt = f"{quote}\\n\\n{advice}"
    wa_link = "https://wa.me/?text=" + share_txt.replace(" ", "%20")
    st.link_button("Share on WhatsApp", wa_link)
with colz:
    st.write(" ")
    st.caption("Preview doesn't change streak or saved day.")

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

st.markdown(
    """
    <div class="footer">
      <div>Tip: same day -> same wisdom for everyone (date-based, deterministic).</div>
      <div>Perinvo ©</div>
    </div>
    """,
    unsafe_allow_html=True
)
