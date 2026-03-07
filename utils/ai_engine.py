"""
utils/ai_engine.py
==================
Multi-factor weighted AI risk scoring engine with full multilingual output.

Scoring weights:
  Pain     : 0-3→0  | 4-6→1  | 7-8→2  | 9-10→3
  Sleep    : ≥7→0   | 5-6.9→1| <5→2   | <4→3
  Temp     : <99.5→0| ≥99.5→1| ≥100.4→3
  Activity : Low→1  | others→0

Hard overrides (always High):
  pain≥9, temp≥100.4, sleep<4, or (pain≥7 AND sleep<5)
"""

AI_MESSAGES: dict[str, dict[str, str]] = {
    "English": {
        "fever":         "🚨 CRITICAL: Fever detected. Possible infection. Seek immediate medical attention.",
        "severe_pain":   "🚨 CRITICAL: Severe pain reported. Contact your doctor immediately.",
        "no_sleep":      "🚨 CRITICAL: Extreme sleep deprivation detected. Urgent medical review needed.",
        "pain_sleep":    "🚨 CRITICAL: High pain combined with lack of sleep. Contact Doctor immediately.",
        "high_risk":     "🚨 HIGH RISK: Multiple danger signals detected ({}). Consult your doctor urgently.",
        "moderate":      "⚠️ WARNING: Elevating symptoms ({}). Rest recommended and monitor closely.",
        "low":           "✅ Condition looks stable. Maintain current medication and routine.",
        "r_severe_pain": "severe pain",
        "r_high_pain":   "high pain",
        "r_mod_pain":    "moderate pain",
        "r_ext_sleep":   "extreme sleep deprivation",
        "r_low_sleep":   "very low sleep",
        "r_red_sleep":   "reduced sleep",
        "r_fever":       "fever",
        "r_elev_temp":   "elevated temperature",
        "r_low_act":     "low activity",
    },
    "Hindi": {
        "fever":         "🚨 गंभीर: बुखार का पता चला। संक्रमण की संभावना। तुरंत चिकित्सा सहायता लें।",
        "severe_pain":   "🚨 गंभीर: तीव्र दर्द। तुरंत अपने डॉक्टर से संपर्क करें।",
        "no_sleep":      "🚨 गंभीर: अत्यधिक नींद की कमी। तुरंत चिकित्सा समीक्षा आवश्यक।",
        "pain_sleep":    "🚨 गंभीर: उच्च दर्द और नींद की कमी। तुरंत डॉक्टर से संपर्क करें।",
        "high_risk":     "🚨 उच्च जोखिम: कई खतरनाक संकेत ({}). तुरंत डॉक्टर से परामर्श करें।",
        "moderate":      "⚠️ चेतावनी: बढ़ते लक्षण ({}). आराम करें और निगरानी जारी रखें।",
        "low":           "✅ स्थिति स्थिर दिखती है। वर्तमान दवाई और दिनचर्या बनाए रखें।",
        "r_severe_pain": "तीव्र दर्द",
        "r_high_pain":   "उच्च दर्द",
        "r_mod_pain":    "मध्यम दर्द",
        "r_ext_sleep":   "अत्यधिक नींद की कमी",
        "r_low_sleep":   "बहुत कम नींद",
        "r_red_sleep":   "कम नींद",
        "r_fever":       "बुखार",
        "r_elev_temp":   "ऊंचा तापमान",
        "r_low_act":     "कम गतिविधि",
    },
    "Tamil": {
        "fever":         "🚨 தீவிரம்: காய்ச்சல் கண்டறியப்பட்டது. உடனடி மருத்துவ உதவி பெறவும்.",
        "severe_pain":   "🚨 தீவிரம்: கடுமையான வலி. உடனடியாக மருத்துவரை தொடர்பு கொள்ளவும்.",
        "no_sleep":      "🚨 தீவிரம்: தீவிர தூக்கமின்மை. உடனடி மருத்துவ மதிப்பாய்வு தேவை.",
        "pain_sleep":    "🚨 தீவிரம்: அதிக வலியும் தூக்கமின்மையும். உடனடியாக மருத்துவரை அழைக்கவும்.",
        "high_risk":     "🚨 அதிக இடர்: பல ஆபத்து அறிகுறிகள் ({}). உடனடியாக மருத்துவரை அணுகவும்.",
        "moderate":      "⚠️ எச்சரிக்கை: அறிகுறிகள் அதிகரிக்கின்றன ({}). ஓய்வெடுங்கள்.",
        "low":           "✅ நிலை நிலையாக உள்ளது. தற்போதைய மருந்து மற்றும் வழக்கத்தை தொடரவும்.",
        "r_severe_pain": "கடுமையான வலி",
        "r_high_pain":   "அதிக வலி",
        "r_mod_pain":    "நடுத்தர வலி",
        "r_ext_sleep":   "தீவிர தூக்கமின்மை",
        "r_low_sleep":   "மிகக் குறைந்த தூக்கம்",
        "r_red_sleep":   "குறைந்த தூக்கம்",
        "r_fever":       "காய்ச்சல்",
        "r_elev_temp":   "உயர்ந்த வெப்பநிலை",
        "r_low_act":     "குறைந்த செயல்பாடு",
    },
}

# Activity values that map to "Low" across all languages
_LOW_ACTIVITY_VALUES = {"Low", "कम", "குறைவு"}


def assess_risk(
    pain: int,
    sleep: float,
    activity: str,
    temp: float,
    lang: str = "English",
) -> tuple[str, str, str]:
    """
    Assess health risk from vital signs.

    Returns:
        risk_level   : "High" | "Moderate" | "Low"
        message      : Translated recommendation string
        alert_status : "Urgent" | "Monitor" | "Normal"
    """
    m = AI_MESSAGES.get(lang, AI_MESSAGES["English"])
    score = 0
    reasons: list[str] = []

    # ── Pain ─────────────────────────────────────────────────────────────────
    if pain >= 9:
        score += 3;  reasons.append(m["r_severe_pain"])
    elif pain >= 7:
        score += 2;  reasons.append(m["r_high_pain"])
    elif pain >= 4:
        score += 1;  reasons.append(m["r_mod_pain"])

    # ── Sleep ─────────────────────────────────────────────────────────────────
    if sleep < 4:
        score += 3;  reasons.append(m["r_ext_sleep"])
    elif sleep < 5:
        score += 2;  reasons.append(m["r_low_sleep"])
    elif sleep < 7:
        score += 1;  reasons.append(m["r_red_sleep"])

    # ── Temperature ───────────────────────────────────────────────────────────
    if temp >= 100.4:
        score += 3;  reasons.append(m["r_fever"])
    elif temp >= 99.5:
        score += 1;  reasons.append(m["r_elev_temp"])

    # ── Activity ─────────────────────────────────────────────────────────────
    if str(activity).strip() in _LOW_ACTIVITY_VALUES:
        score += 1;  reasons.append(m["r_low_act"])

    # ── Hard overrides ────────────────────────────────────────────────────────
    hard_override = (
        pain >= 9
        or temp >= 100.4
        or sleep < 4
        or (pain >= 7 and sleep < 5)
    )

    reason_str = ", ".join(reasons)

    if hard_override or score >= 4:
        risk_level, alert_status = "High", "Urgent"
        if temp >= 100.4:          msg = m["fever"]
        elif pain >= 9:            msg = m["severe_pain"]
        elif sleep < 4:            msg = m["no_sleep"]
        elif pain >= 7 and sleep < 5: msg = m["pain_sleep"]
        else:                      msg = m["high_risk"].format(reason_str)

    elif score >= 2:
        risk_level, alert_status = "Moderate", "Monitor"
        msg = m["moderate"].format(reason_str)

    else:
        risk_level, alert_status = "Low", "Normal"
        msg = m["low"]

    return risk_level, msg, alert_status
