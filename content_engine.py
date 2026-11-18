#!/usr/bin/env python3
"""
content_engine.py - 9-Pillar Hindu Mythology Content & Serialized Story Engine.
Implements:
  - Phase 3: 9 Diversified Content Categories
  - Phase 14: Serialized Multi-Part Story Arc Planner (2-part, 3-part, 4-part series)
  - Emotional escalation, authentic Devanagari narration, and natural cliffhangers
"""

import os
import random
from typing import Dict, Any, List, Optional
from database import is_content_duplicate, record_content_hash, create_or_update_series, get_active_series

# 9 Core Mythology Pillars from Phase 3
PILLARS = [
    "mahabharata",          # 1. Mahabharata mysteries
    "ramayana",             # 2. Ramayana untold stories
    "lesser_known",         # 3. Lesser-known mythological figures
    "divine_power",         # 4. Powerful stories of Shiva, Krishna, Hanuman, Vishnu
    "curses_boons",         # 5. Emotional sacrifices, curses & boons
    "gita_teachings",       # 6. Bhagavad Gita teachings & cosmic truths
    "facts_interpretations",# 7. Mythological facts & lost sacred locations
    "character_battles",    # 8. Character comparisons & philosophical dilemmas
    "dharma_karma"          # 9. Stories of Dharma, Karma, and Destiny
]

# Rich Story Knowledge Base with Serialized & Standalone Scenarios
STORY_CATALOG = [
    # --- MAHABHARATA & SERIALS ---
    {
        "id": "barbareek_sacrifice",
        "pillar": "lesser_known",
        "is_series": True,
        "total_parts": 2,
        "title": "बर्बरीक के तीन बाण और श्रीकृष्ण की परीक्षा",
        "characters": ["Barbareek", "Krishna", "Kurukshetra"],
        "parts": [
            {
                "part_number": 1,
                "top_hook": "BARBAREEK KE 3 TEER",
                "top_hook_hindi": "बर्बरीक के 3 बाण: 1 मिनट में महाभारत खत्म?",
                "cliffhanger": "श्रीकृष्ण ने एक ऐसा दान मांग लिया जिसने युद्ध शुरू होने से पहले ही समाप्त कर दिया। क्या था वह दान? जानिए Part 2 में!",
                "beats": [
                    {
                        "text_hindi": "महाभारत के सबसे शक्तिशाली योद्धा अर्जुन या कर्ण नहीं, बल्कि भीम के पौत्र बर्बरीक थे।",
                        "keyword": "MAHA YODDHA", "sublabel": "BHIM KA POUTRA",
                        "scene": {"character": "barbareek", "setting": "battlefield", "action": "aiming_bow", "mood": "divine", "sky": "divine"}
                    },
                    {
                        "text_hindi": "देवी कामख्या से मिले तीन दिव्य बाणों से वह पूरी सेना को मात्र 1 मिनट में भस्म कर सकते थे।",
                        "keyword": "TEEN BAAN", "sublabel": "KAMAKHYA KA VARDAAN",
                        "scene": {"character": "arrows_glowing", "setting": "cosmos", "action": "arrows_floating", "mood": "divine", "sky": "divine"}
                    },
                    {
                        "text_hindi": "उनका प्रण था कि जो पक्ष हार रहा होगा, वह उसी की ओर से लड़ेंगे।",
                        "keyword": "VISMYAKARI PRAN", "sublabel": "HARTE KA SAHARA",
                        "scene": {"character": "barbareek", "setting": "peepal_tree", "action": "standing_noble", "mood": "dusk", "sky": "dusk"}
                    },
                    {
                        "text_hindi": "श्रीकृष्ण जानते थे कि अगर बर्बरीक उतरे, तो दोनों सेनाएं बारी-बारी से पूरी तरह समाप्त हो जाएंगी।",
                        "keyword": "KRISHNA LEELA", "sublabel": "DHARMA SANKAT",
                        "scene": {"character": "krishna_silhouette", "setting": "peepal_tree", "action": "testing_hero", "mood": "dusk", "sky": "dusk"}
                    },
                    {
                        "text_hindi": "तब श्रीकृष्ण एक ब्राह्मण का रूप धरकर बर्बरीक के सामने पहुंचे और एक असंभव दान की मांग कर दी।",
                        "keyword": "BRAHMAN ROOP", "sublabel": "PARIKSHA KI GHADI",
                        "scene": {"character": "krishna_brahman", "setting": "forest_path", "action": "asking_daan", "mood": "dusk", "sky": "dusk"}
                    },
                    {
                        "text_hindi": "श्रीकृष्ण ने ऐसा क्या मांग लिया जिसने बर्बरीक को हैरान कर दिया? आगे की गाथा देखिए Part 2 में! अभी फॉलो करें।",
                        "keyword": "KAHANI KA MOD", "sublabel": "PART 2 ANE WALA HAI",
                        "scene": {"character": "barbareek_shocked", "setting": "curtain_cliffhanger", "action": "cliffhanger_pose", "mood": "battle", "sky": "battle"}
                    }
                ]
            },
            {
                "part_number": 2,
                "top_hook": "SHISH KA MAHADAN",
                "top_hook_hindi": "बर्बरीक का शीश दान और खाटू श्याम अवतार",
                "cliffhanger": "बर्बरीक के इस बलिदान के बाद श्रीकृष्ण ने उन्हें कलयुग का भगवान बना दिया।",
                "beats": [
                    {
                        "text_hindi": "Part 1 में आपने देखा कि ब्राह्मण रूपी श्रीकृष्ण ने बर्बरीक से दान मांगा। पर जानते हैं वह दान क्या था?",
                        "keyword": "PURVAVALOKAN", "sublabel": "PART 1 KA JAWAB",
                        "scene": {"character": "krishna_brahman", "setting": "peepal_tree", "action": "pointing_finger", "mood": "divine", "sky": "divine"}
                    },
                    {
                        "text_hindi": "श्रीकृष्ण ने कहा: युद्ध भूमि की बलि के लिए मुझे सबसे वीर योद्धा का शीश चाहिए!",
                        "keyword": "SHEESH DAAN", "sublabel": "PARIKSHA KI CHARAM",
                        "scene": {"character": "krishna_divine_form", "setting": "clouds", "action": "divine_glow", "mood": "divine", "sky": "divine"}
                    },
                    {
                        "text_hindi": "बर्बरीक ने मुस्कुराते हुए तलवार उठाई और बिना झिझके अपना शीश काटकर प्रभु के चरणों में अर्पित कर दिया।",
                        "keyword": "MAHA TYAG", "sublabel": "AMAR BALIDAN",
                        "scene": {"character": "barbareek_kneeling", "setting": "sacred_altar", "action": "holding_sword", "mood": "peace", "sky": "peace"}
                    },
                    {
                        "text_hindi": "प्रसन्न होकर श्रीकृष्ण ने शीश को एक ऊंचे पर्वत पर स्थापित किया ताकि वह पूरा महाभारत युद्ध देख सके।",
                        "keyword": "YUDDHA SAKSHI", "sublabel": "PARVAT SHIKHAR",
                        "scene": {"character": "sheesh_on_hill", "setting": "mountain_peak", "action": "watching_battle", "mood": "dusk", "sky": "dusk"}
                    },
                    {
                        "text_hindi": "युद्ध समाप्ति पर बर्बरीक ने गवाही दी: यहां न अर्जुन लड़ रहे थे, न कर्ण—हर तरफ केवल श्रीकृष्ण का चक्र चल रहा था!",
                        "keyword": "SATYA PRAKASH", "sublabel": "SUDARSHANA KA PRAKOP",
                        "scene": {"character": "flaming_chakra", "setting": "kurukshetra_dust", "action": "spinning_chakra", "mood": "battle", "sky": "battle"}
                    },
                    {
                        "text_hindi": "प्रभु ने उन्हें वरदान दिया कि कलयुग में तुम 'खाटू श्याम' के नाम से पूजे जाओगे! कमेंट में लिखें 'जय श्री श्याम'।",
                        "keyword": "KHATU SHYAM", "sublabel": "KALIYUG AVATAR",
                        "scene": {"character": "khatu_shyam_aura", "setting": "temple_sacred", "action": "divine_blessing", "mood": "peace", "sky": "peace"}
                    }
                ]
            }
        ]
    },

    # --- RAMAYANA & BOONS ---
    {
        "id": "kumbhakarna_boon_curse",
        "pillar": "ramayana",
        "is_series": False,
        "total_parts": 1,
        "title": "कुंभकर्ण को 6 महीने सोने का श्राप कैसे मिला?",
        "top_hook": "KUMBHAKARNA KA VARDAAN",
        "top_hook_hindi": "कुंभकर्ण की जुबान पर सरस्वती: इंद्रासन या निद्रासन?",
        "beats": [
            {
                "text_hindi": "रावण का भाई कुंभकर्ण इतना पराक्रमी था कि उसकी घोर तपस्या देखकर स्वर्ग के देवराज इंद्र कांप उठे थे।",
                "keyword": "GHOR TAPASYA", "sublabel": "INDRA KA BHAYA",
                "scene": {"character": "kumbhakarna_tapasya", "setting": "himalayas", "action": "deep_meditation", "mood": "dusk", "sky": "dusk"}
            },
            {
                "text_hindi": "जब ब्रह्मा जी वरदान देने प्रकट हुए, तो देवता भयभीत होकर माता सरस्वती की शरण में पहुंचे।",
                "keyword": "BRAHMA DARSHAN", "sublabel": "DEVTAON KI PRARTHANA",
                "scene": {"character": "brahma_seated", "setting": "clouds_golden", "action": "blessing_gesture", "mood": "divine", "sky": "divine"}
            },
            {
                "text_hindi": "देवताओं ने प्रार्थना की: यदि कुंभकर्ण अमर हो गया, तो तीनों लोकों में प्रलय आ जाएगी।",
                "keyword": "PRALAYA KA DARR", "sublabel": "SWARGA PAR SANKAT",
                "scene": {"character": "indra_silhouette", "setting": "swarga_gate", "action": "folding_hands", "mood": "dusk", "sky": "dusk"}
            },
            {
                "text_hindi": "जैसे ही कुंभकर्ण ने 'इंद्रासन' मांगना चाहा, देवी सरस्वती उसकी जिह्वा पर बैठ गईं और मुंह से निकला 'निद्रासन'!",
                "keyword": "SARASWATI LEELA", "sublabel": "INDRAASAN SE NIDRAASAN",
                "scene": {"character": "saraswati_light", "setting": "divine_rays", "action": "cosmic_aura", "mood": "divine", "sky": "divine"}
            },
            {
                "text_hindi": "ब्रह्मा जी ने 'तथास्तु' कह दिया। इसके बाद कुंभकर्ण को 6 महीने सोने और केवल 1 दिन जागने का वरदान मिला।",
                "keyword": "TATHAASTU", "sublabel": "6 MAHINE KI NIND",
                "scene": {"character": "kumbhakarna_sleeping", "setting": "lanka_cave", "action": "giant_slumber", "mood": "night", "sky": "night"}
            },
            {
                "text_hindi": "सनातन धर्म के ऐसे रहस्यमय प्रसंग जानने के लिए सब्सक्राइब करें! क्या कुंभकर्ण अधर्मी था? अपनी राय लिखें।",
                "keyword": "SANATAN RAHASYA", "sublabel": "COMMENT MEIN BATAEIN",
                "scene": {"character": "om_radiance", "setting": "mandir_silhouette", "action": "divine_glow", "mood": "peace", "sky": "peace"}
            }
        ]
    },

    # --- SHIVA & DIVINE POWER ---
    {
        "id": "shiva_neelkanth_halahal",
        "pillar": "divine_power",
        "is_series": False,
        "total_parts": 1,
        "title": "जब महादेव ने हलाहल विष पीकर सृष्टि बचाई",
        "top_hook": "MAHADEV NEELKANTH KAISE BANE?",
        "top_hook_hindi": "नीलकंठ महादेव: जब कालकूट विष से कांप उठी सृष्टि",
        "beats": [
            {
                "text_hindi": "समुद्र मंथन के समय अमृत से पहले एक ऐसा भयानक विष निकला जिससे तीनों लोकों में हाहाकार मच गया।",
                "keyword": "SAMUDRA MANTHAN", "sublabel": "HALAHAL VISH",
                "scene": {"character": "samudra_churning", "setting": "churning_ocean", "action": "ocean_waves", "mood": "battle", "sky": "battle"}
            },
            {
                "text_hindi": "उस कालकूट विष की गंध मात्र से देवता और असुर मूर्छित होकर गिरने लगे थे।",
                "keyword": "PRALAYANKARI", "sublabel": "CHRONIC HEAT",
                "scene": {"character": "poison_smoke", "setting": "toxic_clouds", "action": "rising_vapors", "mood": "night", "sky": "night"}
            },
            {
                "text_hindi": "संसार को भस्म होने से बचाने के लिए सभी देवी-देवता कैलाश पर भगवान शिव की शरण में पहुंचे।",
                "keyword": "KAILASH SHARAN", "sublabel": "DEVTAON KI GUHAAR",
                "scene": {"character": "kailash_parvat", "setting": "snow_mountain", "action": "serene_silence", "mood": "peace", "sky": "peace"}
            },
            {
                "text_hindi": "करुणामयी महादेव ने बिना किसी संकोच के उस समस्त विष को अपनी हथेली में भरकर पी लिया।",
                "keyword": "MAHADEV TYAG", "sublabel": "VISH PAAN",
                "scene": {"character": "shiva_drinking_poison", "setting": "kailash_cliff", "action": "drinking_poison", "mood": "divine", "sky": "divine"}
            },
            {
                "text_hindi": "माता पार्वती ने विष को शिवजी के गले में ही थाम लिया, जिससे उनका कंठ नीला पड़ गया और वे 'नीलकंठ' कहलाए।",
                "keyword": "NEELKANTH", "sublabel": "PARVATI KI SHAKTI",
                "scene": {"character": "shiva_blue_throat", "setting": "divine_meditation", "action": "blue_glow", "mood": "divine", "sky": "divine"}
            },
            {
                "text_hindi": "संसार के दुख स्वयं पी लेने वाले महादेव के लिए एक 'हर हर महादेव' कमेंट में जरूर लिखें!",
                "keyword": "HAR HAR MAHADEV", "sublabel": "DEVON KE DEV",
                "scene": {"character": "trishul_damru", "setting": "sacred_himalayas", "action": "trishul_golden", "mood": "peace", "sky": "peace"}
            }
        ]
    },

    # --- BHAGAVAD GITA & KARMA ---
    {
        "id": "gita_karmanye_vadhikaraste",
        "pillar": "gita_teachings",
        "is_series": False,
        "total_parts": 1,
        "title": "कर्मण्येवाधिकारस्ते: श्रीकृष्ण का जीवन बदलने वाला उपदेश",
        "top_hook": "KARMA KA ASLI ARTHA",
        "top_hook_hindi": "कर्मण्येवाधिकारस्ते: फल की चिंता से मुक्ति कैसे?",
        "beats": [
            {
                "text_hindi": "कुरुक्षेत्र के मैदान में जब गांडीवधारी अर्जुन के हाथ कांपने लगे, तब श्रीकृष्ण ने मुस्कुराते हुए एक सत्य कहा।",
                "keyword": "GANDIV KAAPNE LAGA", "sublabel": "MOH MEIN ARJUN",
                "scene": {"character": "arjun_weeping", "setting": "chariot_battle", "action": "bow_on_ground", "mood": "dusk", "sky": "dusk"}
            },
            {
                "text_hindi": "प्रभु ने कहा: हे अर्जुन! तुम्हारा अधिकार केवल अपने कर्म पर है, उसके फल पर कभी नहीं।",
                "keyword": "KARMANYE VADHIKARASTE", "sublabel": "SHLOKA 2.47",
                "scene": {"character": "krishna_smiling", "setting": "chariot_center", "action": "divine_teaching", "mood": "divine", "sky": "divine"}
            },
            {
                "text_hindi": "जब तुम केवल परिणाम के बारे में सोचते हो, तो तुम्हारा आज का कर्म कमजोर और भयभीत हो जाता है।",
                "keyword": "PARINAAM KA BHAYA", "sublabel": "CHINTA KA BANDHAN",
                "scene": {"character": "arjun_listening", "setting": "battlefield_fog", "action": "looking_up", "mood": "dusk", "sky": "dusk"}
            },
            {
                "text_hindi": "युद्ध जीतना या हारना समय के गर्भ में है, लेकिन पूरी निष्ठा से लड़ना केवल तुम्हारे हाथ में है।",
                "keyword": "NISHKAMA KARMA", "sublabel": "DHARMA YUDDHA",
                "scene": {"character": "krishna_holding_reins", "setting": "white_horses", "action": "steering_chariot", "mood": "peace", "sky": "peace"}
            },
            {
                "text_hindi": "यह सुनते ही अर्जुन ने धनुष उठाया और उनका सारा संशय नष्ट हो गया।",
                "keyword": "GANDIV UTHAYA", "sublabel": "SANSHAY NASHT",
                "scene": {"character": "arjun_aiming_sun", "setting": "morning_sun", "action": "firm_stance", "mood": "battle", "sky": "battle"}
            },
            {
                "text_hindi": "गीता का यह एक श्लोक आपके जीवन की हर चिंता दूर कर सकता है। कमेंट में लिखें 'जय श्री कृष्णा'!",
                "keyword": "JAI SHREE KRISHNA", "sublabel": "GITA GYAN",
                "scene": {"character": "gita_pustak_glow", "setting": "sacred_light", "action": "radiating_wisdom", "mood": "divine", "sky": "divine"}
            }
        ]
    },

    # --- CHARACTER COMPARISONS ---
    {
        "id": "karna_vs_arjun_truth",
        "pillar": "character_battles",
        "is_series": False,
        "total_parts": 1,
        "title": "कर्ण या अर्जुन: श्रीकृष्ण की दृष्टि में कौन श्रेष्ठ था?",
        "top_hook": "KARNA YA ARJUN SHRESHTHA?",
        "top_hook_hindi": "कर्ण या अर्जुन: रथ 2 कदम पीछे क्यों हटा?",
        "beats": [
            {
                "text_hindi": "कुरुक्षेत्र युद्ध में एक पल ऐसा आया जब अर्जुन के बाण से कर्ण का रथ 10 कदम पीछे खिसक गया।",
                "keyword": "ARJUN KA BAAN", "sublabel": "10 KADAM PICHE",
                "scene": {"character": "arjun_shooting", "setting": "kurukshetra_dust", "action": "release_arrow", "mood": "battle", "sky": "battle"}
            },
            {
                "text_hindi": "लेकिन जब कर्ण ने बाण मारा, तो अर्जुन का रथ केवल 2 कदम पीछे हटा... फिर भी श्रीकृष्ण ने कर्ण की प्रशंसा की!",
                "keyword": "KRISHNA PRASHANSA", "sublabel": "KEVAL 2 KADAM",
                "scene": {"character": "krishna_applauding", "setting": "chariot_seat", "action": "nodding_smiling", "mood": "divine", "sky": "divine"}
            },
            {
                "text_hindi": "अर्जुन को बुरा लगा और उन्होंने पूछा: केशव! मैंने उसका रथ 10 कदम धकेला, फिर भी आप उसकी वाहवाही कर रहे हैं?",
                "keyword": "ARJUN KA PRASHNA", "sublabel": "ABHIMAAN KA JAWAB",
                "scene": {"character": "arjun_questioning", "setting": "chariot_standing", "action": "asking_lord", "mood": "dusk", "sky": "dusk"}
            },
            {
                "text_hindi": "श्रीकृष्ण ने कहा: पार्थ! तुम्हारे रथ पर स्वयं ब्रह्मांड के रक्षक मैं बैठा हूं, ध्वजा पर साक्षात महावीर हनुमान हैं!",
                "keyword": "HANUMAN KI DHWAJA", "sublabel": "BRAHMAND KA BHAAR",
                "scene": {"character": "hanuman_on_flag", "setting": "flag_fluttering", "action": "roaring_flag", "mood": "divine", "sky": "divine"}
            },
            {
                "text_hindi": "जिस रथ पर त्रिभुवन का भार हो, उसे अकेले अपने बाणों से 2 कदम पीछे धकेल देना कर्ण के अदम्य शौर्य का प्रमाण है!",
                "keyword": "ADAMYA SHAURYA", "sublabel": "KARNA KA TEJ",
                "scene": {"character": "karna_golden_bow", "setting": "sunset_glory", "action": "bow_held_high", "mood": "dusk", "sky": "dusk"}
            },
            {
                "text_hindi": "दानवीर और वीर कर्ण के इस पराक्रम को नमन! आपकी नजर में कौन महान था? कमेंट में बताएं।",
                "keyword": "VIRAT YODDHA", "sublabel": "APNI RAI DEIN",
                "scene": {"character": "karna_standing_proud", "setting": "golden_horizon", "action": "saluting_sun", "mood": "peace", "sky": "peace"}
            }
        ]
    }
]

def get_next_daily_mix() -> List[Dict[str, Any]]:
    """
    Selects 5 distinct reels for the day following the optimal strategy:
      - Slot 1: Divine Power / Sacred Morning
      - Slot 2: Ongoing Series Chapter (or Part 1 of a serialized story)
      - Slot 3: Character Deep-dive / Lesser-known legend
      - Slot 4: High-impact Mystery / Curse / Bhagavad Gita
      - Slot 5: Prime-time Series Continuation / Climax
    """
    selected_reels = []
    
    # Check active ongoing series from DB
    active = get_active_series()
    
    # 1. Slot 1: Divine Power (Shiva / Hanuman / Vishnu)
    r1 = [s for s in STORY_CATALOG if s["pillar"] in ("divine_power", "ramayana")][0]
    reel1 = {
        "slug": f"reel_{r1['id']}",
        "title": r1["title"],
        "top_hook": r1["top_hook"],
        "top_hook_hindi": r1["top_hook_hindi"],
        "category": r1["pillar"],
        "is_series": False,
        "part_number": 1,
        "total_parts": 1,
        "beats": r1["beats"],
        "caption": f"{r1['top_hook_hindi']} 🔱\n\n{r1['beats'][0]['text_hindi']}\n\nपूरी गाथा देखिए और सनातन धर्म के ऐसे ही प्रामाणिक रहस्यों के लिए फॉलो करें @untold_mythology_legends!\n\n#sanatandharma #mahadev #untoldmythology #reelsindia #hinduism"
    }
    selected_reels.append(reel1)

    # 2. Slot 2: Serialized Part 1 (Barbareek Part 1)
    barbareek = [s for s in STORY_CATALOG if s["id"] == "barbareek_sacrifice"][0]
    p1 = barbareek["parts"][0]
    reel2 = {
        "slug": f"barbareek_part_01",
        "series_id": "series_barbareek",
        "title": f"बर्बरीक की अमर गाथा - Part 1",
        "top_hook": p1["top_hook"],
        "top_hook_hindi": p1["top_hook_hindi"],
        "category": "series_ongoing",
        "is_series": True,
        "part_number": 1,
        "total_parts": 2,
        "beats": p1["beats"],
        "caption": f"⚡ PART 1: {p1['top_hook_hindi']} 🏹\n\nबर्बरीक के तीन बाणों से पूरी महाभारत 1 मिनट में समाप्त हो सकती थी! लेकिन श्रीकृष्ण ने ऐसा क्या मांगा?\n\n👉 Part 2 आ रहा है! जानने के लिए अभी फॉलो करें @untold_mythology_legends!\n\n#barbareek #khatushyam #mahabharat #sanatandharma #reelsindia"
    }
    selected_reels.append(reel2)

    # 3. Slot 3: Character Comparison (Karna vs Arjun)
    r3 = [s for s in STORY_CATALOG if s["id"] == "karna_vs_arjun_truth"][0]
    reel3 = {
        "slug": f"reel_{r3['id']}",
        "title": r3["title"],
        "top_hook": r3["top_hook"],
        "top_hook_hindi": r3["top_hook_hindi"],
        "category": r3["pillar"],
        "is_series": False,
        "part_number": 1,
        "total_parts": 1,
        "beats": r3["beats"],
        "caption": f"कर्ण या अर्जुन: श्रीकृष्ण ने कर्ण की प्रशंसा क्यों की? 🏹\n\n{r3['beats'][4]['text_hindi']}\n\nआपकी दृष्टि में कौन श्रेष्ठ था? कमेंट में बताएं!\n\nFollow @untold_mythology_legends for daily authentic Hindu legends!\n\n#karna #arjun #krishna #mahabharata #sanatan #reelsindia"
    }
    selected_reels.append(reel3)

    # 4. Slot 4: Bhagavad Gita / Dharma Teaching
    r4 = [s for s in STORY_CATALOG if s["id"] == "gita_karmanye_vadhikaraste"][0]
    reel4 = {
        "slug": f"reel_{r4['id']}",
        "title": r4["title"],
        "top_hook": r4["top_hook"],
        "top_hook_hindi": r4["top_hook_hindi"],
        "category": r4["pillar"],
        "is_series": False,
        "part_number": 1,
        "total_parts": 1,
        "beats": r4["beats"],
        "caption": f"कर्मण्येवाधिकारस्ते: श्रीकृष्ण का यह एक श्लोक हर चिंता मिटा देगा 🪷\n\n'तुम्हारा अधिकार केवल कर्म पर है, फल पर नहीं।'\n\nकमेंट में 'जय श्री कृष्णा' लिखें और रोजाना गीता ज्ञान के लिए फॉलो करें @untold_mythology_legends!\n\n#bhagavadgita #krishna #karmayoga #sanatan #spiritualwisdom"
    }
    selected_reels.append(reel4)

    # 5. Slot 5: Prime-Time Series Climax (Barbareek Part 2)
    p2 = barbareek["parts"][1]
    reel5 = {
        "slug": f"barbareek_part_02",
        "series_id": "series_barbareek",
        "title": f"बर्बरीक की अमर गाथा - Part 2 (अंतिम भाग)",
        "top_hook": p2["top_hook"],
        "top_hook_hindi": p2["top_hook_hindi"],
        "category": "series_cliffhanger",
        "is_series": True,
        "part_number": 2,
        "total_parts": 2,
        "beats": p2["beats"],
        "caption": f"⚡ PART 2 (FINAL): {p2['top_hook_hindi']} 🌸\n\nPart 1 में पूछे गए प्रश्न का रहस्य: जब बर्बरीक ने हंसते हुए अपना शीश काटकर श्रीकृष्ण को दान कर दिया!\n\nप्रभु ने वरदान दिया: कलयुग में तुम 'खाटू श्याम' बनकर पूजे जाओगे।\n\nकमेंट में लिखें 'जय श्री श्याम' और अगली सीरीज के लिए फॉलो करें @untold_mythology_legends!\n\n#khatushyam #barbareek #mahabharat #sanatandharma #reelsindia"
    }
    selected_reels.append(reel5)

    return selected_reels
