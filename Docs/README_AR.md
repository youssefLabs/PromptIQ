<div dir="rtl">

<p align="center">
  <img src="banner-promptiq.jpg" alt="PromptIQ" width="750">
</p>

<h1 align="center">PromptIQ</h1>

<p align="center">
  <strong>أداة هندسة البرومبت الذكية — نسخ تحكم + تقييم بالذكاء الاصطناعي + اختبار A/B + تحسين تلقائي</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/promptiq/"><img src="https://img.shields.io/pypi/v/promptiq?color=blueviolet&style=for-the-badge"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge"></a>
</p>

<p align="center">�  <a href="../README.md">🇬🇧 English</a> ·�  <a href="./README_AR.md">🇸🇦 العربية</a> ·�  <a href="./README_FR.md">🇫🇷 Français</a> ·�  <a href="./README_ZH.md">🇨🇳 中文</a>�</p>�
</p>


<p align="center">
  <a href="../README.md">&#x1F1EC;&#x1F1E7; English</a> &middot;
  <a href="./README_AR.md">&#x1F1F8;&#x1F1E6; &#x627;&#x644;&#x639;&#x631;&#x628;&#x64A;&#x629;</a> &middot;
  <a href="./README_FR.md">&#x1F1EB;&#x1F1F7; Fran&ccedil;ais</a> &middot;
  <a href="./README_ZH.md">&#x1F1E8;&#x1F1F3; &#x4E2D;&#x6587;</a>
</p>

---

## 💀 المشكلة

قضيت ساعات في ضبط البرومبت. اشتغل بشكل مثالي.
عملت تعديل بسيط.
وقعت كل حاجة.

لا تاريخ. لا رجوع. لا diff. **النسخة اللي اشتغلت راحت للأبد.**

---

## ✦ إيه هو PromptIQ؟

PromptIQ هو نظام تحكم في الإصدارات للـ prompts — مع ذكاء اصطناعي حقيقي جوه.

أمر واحد يعمل كل ده:

```bash
promptiq commit chatbot system.txt -m "تحسين النبرة" --judge --test-cases inputs.json
```

1. ✅ يحفظ الإصدار مع semver (`v1.2.0`) وهاش
2. ✅ يقيّم نص البرومبت على 5 أبعاد
3. ✅ يشغّل البرومبت على inputs حقيقية ويقيّم الـ output الفعلي
4. ✅ يقارن بالإصدار السابق ويحكم على الفائز
5. ✅ يولّد نسخة محسّنة تستهدف نقاط ضعفك
6. ✅ يحفظ كل ده محلياً في JSON — بدون cloud، بدون حساب

---

## ⚡ التثبيت

```bash
# مع Claude (موصى به)
pip install "promptiq[anthropic]"
export ANTHROPIC_API_KEY=sk-ant-...

# مع OpenAI
pip install "promptiq[openai]"
export OPENAI_API_KEY=sk-...
```

---

## 🚀 البداية السريعة

```bash
# حفظ إصدار
promptiq commit chatbot system.txt -m "مسودة أولى"

# حفظ + تقييم كامل
promptiq commit chatbot system.txt -m "محسّن" --judge --test-cases inputs.json

# مقارنة إصدارين
promptiq diff chatbot 1.0.0 1.1.0

# اختبار A/B
promptiq ab chatbot 1.0.0 1.1.0 --test-cases inputs.json

# نسخة محسّنة بالذكاء الاصطناعي
promptiq improve chatbot

# تصدير سجل التغييرات
promptiq export chatbot
```

---

## 🧠 الـ Judge ذو الـ 4 مراحل

```
المرحلة 1 ── تحليل النص        تقييم البرومبت نفسه
المرحلة 2 ── تقييم الـ Output  تشغيل على LLM حقيقي وتقييم النتيجة
المرحلة 3 ── مقارنة الإصدار   مقارنة بالإصدار السابق
المرحلة 4 ── التحسين التلقائي  نسخة محسّنة مع قائمة التغييرات
```

### المرحلة 1 — تحليل النص

| البُعد | ما يقيسه |
|---|---|
| الوضوح | هل الكلام واضح لا لبس فيه؟ |
| التحديد | هل التعليمات محددة وقابلة للتنفيذ؟ |
| الإيجاز | خالٍ من التكرار والحشو؟ |
| جودة التعليمات | هل توجّه النموذج بفاعلية؟ |
| المتانة | هل يتعامل مع الحالات الاستثنائية؟ |

### المرحلة 2 — تقييم الـ Output الحقيقي

```
  Test 1: اشرح الذكاء الاصطناعي لطفل عمره 10 سنين
    الصلة:         ████████░░ 8/10
    اتباع التعليمات: ██████░░░░ 6/10
    الجودة:         ███████░░░ 7/10
    الحكم: الإجابة دقيقة لكن المصطلحات كانت صعبة للفئة المستهدفة
```

### المرحلة 3 — مقارنة الإصدارات

```
  الإصدار القديم:  6.2/10
  الإصدار الجديد:  8.4/10
  الفرق:           ▲ 2.2 نقطة

  الإصدار الجديد يفوز ✓

  التحسينات:
  ✅ إضافة متطلبات صيغة JSON الصريحة
  ✅ تحديد الحد الأقصى للرد

  التراجعات:
  ❌ تعريف الشخصية أصبح غامضاً نسبياً
```

### المرحلة 4 — التحسين التلقائي

```
  التغييرات:
  → استبدال "كن مفيداً" بـ"أجب في 3 جمل أو أقل" (تحديد +2)
  → إضافة "إذا لم تعرف قل 'لا أعرف'" (متانة +1.5)
  → إزالة عبارة "كنموذج ذكاء اصطناعي" الزائدة (إيجاز +1)

  💡 الإصدار المحسّن محفوظ في: suggested.txt
```

---

## 🔬 اختبار A/B

```bash
promptiq ab chatbot 1.0.0 1.2.0 --test-cases inputs.json
```

```
  v1.0.0 يفوز: 1
  v1.2.0 يفوز: 2

  متوسط v1.0.0: 6.8/10
  متوسط v1.2.0: 7.6/10
  الفرق: ▲ 0.8 نقطة

  الفائز: v1.2.0
```

---

## 📖 جميع الأوامر

```bash
promptiq commit <اسم> <ملف> -m "رسالة" [--judge] [--test-cases ملف.json]
promptiq log <اسم>
promptiq diff <اسم> <ref_a> <ref_b>
promptiq judge <ملف> [--test-cases ملف.json]
promptiq improve <اسم>
promptiq ab <اسم> <ref_a> <ref_b> --test-cases ملف.json
promptiq status <اسم>
promptiq checkout <اسم> <ref>
promptiq ls
promptiq export <اسم> [--format markdown|json|scores]
promptiq branch create|switch|ls <اسم>
```

---

## 🗄️ التخزين

```
~/.promptiq/
└── prompts/
    ├── chatbot.json
    └── summarizer.json
```

JSON عادي. يمكن قراءته بأي محرر نصوص. لا قاعدة بيانات. لا قفل للمورّد.

---

## 📄 الرخصة

MIT — استخدمه، فوركه، ابنِ عليه، أطلقه.

---

<p align="center">
  <em>هندسة البرومبت لا يجب أن تكون تخميناً.<br>
  كل تغيير يجب أن يكون قابلاً للقياس. كل إصدار قابل للتحسين.<br>
  هذا ما PromptIQ موجود من أجله.</em>
</p>

</div>
