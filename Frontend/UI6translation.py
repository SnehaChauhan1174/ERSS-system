# translations.py

TEXT = {
    "en": {
        "nav_home": "Home",
        "nav_analysis": "Call Analysis",
        "nav_reports": "Reports",
        "home_title": "ERSS AI Operations",
        "home_subtitle": "View Overall Performance.",
        "car_title_1": "Real-Time Audio Analysis",
        "car_desc_1": "Process emergency calls with sub-30s latency.",
        "car_title_2": "Automated Auditing",
        "car_desc_2": "Ensure 100% protocol compliance across all call operators automatically.",
        "car_title_3": "Comprehensive Performance Reports",
        "car_desc_3": "Generate actionable insights and evaluate performance metrics.",
        "analysis_title": "Call Analysis",
        "analysis_desc": "Upload raw ERSS audio for AI transcription, summary, and protocol auditing.",
        "brand_title": "ERSS Transcript Solution",
        
        "metric_1_title": "Total Calls This Week",
        "metric_1_delta": "5.2% Increase compared to last 7 days",
        "metric_2_title": "Average Compliance Score",
        "metric_2_delta": "1.2% Increase compared to last 7 days",
        "metric_3_title": "High Severity Calls",
        "metric_3_delta": "-2.1% Compared to last 7 days",

        # Categories for Graph 1
        "cat_police": "Police (112)",
        "cat_medical": "Medical (108)",
        "cat_traffic": "Traffic",
        "cat_fire": "Fire (101)",
        "cat_women": "Women's Helpline (1090)",
        "cat_other": "Other",

        # Graph 1 & 2 Labels
        "graph_1_title": "Calls Per Category (Past Week)",
        "graph_1_x": "Category",
        "graph_1_y": "Call Volume",
        "graph_2_title": "Average KPI Compliance (n=20)",
        "graph_2_x": "Call Taker",
        "graph_2_y": "Score (Out of 100)",
        "agent_prefix": "Agent",

        # Graph 3 & 4 Labels
        "graph_3_title": "Call Severity Breakdown",
        "graph_3_cat": "Severity",
        "graph_3_val": "Percentage",
        "sev_low": "Low",
        "sev_med": "Medium",
        "sev_high": "High",
        "graph_4_title": "Today's Hourly Compliance Trend",
        "graph_4_x": "Hour of the day",
        "graph_4_y": "Compliance Score",

        # About Section
        "about_title": "About our service",
        "about_card1_title": "Impact of AI based ERSS transcription and auditing",
        "about_card1_desc": "Faster audit cycles, operator accountability, automated monitoring, actionable insights...",
        "about_card2_title": "Tools and techniques used",
        "about_card2_desc": "Open AI Faster Whisper model and Groq's AI model for sentiment analysis, keyword analysis, intent detection and more.",
        "about_card3_title": "Call transcription pipeline",
        "about_card3_desc": "ERSS audio recieved, audio cleanup using VAD, feature extraction and vector embeddings, speech to text transformer model, Formatted transcript, AI auditing layer.",

        # Audio Section
        "audio_section_title": "Select Saved Call Audios",
        "audio_section_desc": "Filter and listen to raw ERSS audio files securely.",
        "audio_date_label": "Select Date",
        "audio_hour_label": "Select Hour",
        "audio_select_label": "Available Recordings",
        "audio_no_files": "No audio files found for this specific hour.",
        "audio_folder_missing": "The 'Audios' folder is missing. Please create it in the root directory.",
        # Audio Widget (Range Filters)
        "audio_start_date": "Start Date",
        "audio_end_date": "End Date",
        "audio_start_hour": "Start Hour",
        "audio_end_hour": "End Hour",
        "audio_invalid_range": "Start date/time cannot be after end date/time.",
        "audio_no_files_range": "No audio files found within this selected time range.",

        # Call Analysis Page
        "lbl_upload": "Upload Audio File (.wav, .mp3)",
        "lbl_taker_id": "Call Taker ID",
        "lbl_analyze_btn": "Analyze Call",
        "lbl_loading": "AI is processing audio (Transcription, NLP, Auditing)... Please wait.",
        "err_no_file": "Please upload an audio file first.",
        "err_no_id": "Please enter a Call Taker ID.",
        "tab_trans_sum": "Transcription & Summary",
        "tab_audit": "Audit",
        
        # Transcription Tab Details
        "lbl_incident_type": "Incident Type",
        "lbl_severity": "Severity",
        "lbl_caller": "Caller & Location",
        "lbl_key_facts": "Key Facts",
        "lbl_dispatcher_actions": "Call Taker Actions",
        "lbl_entities": "Important Entities",
        "lbl_final_summary": "Overall Summary",
        "lbl_transcript": "Call Transcript",

        # Transcript & Summary Updates
        "lbl_call_summary_title": "CALL SUMMARY",
        "lbl_incident_overview": "Incident Overview",
        "lbl_add_info": "Additional Information",
        "lbl_no_data": "No additional data available.",
        "lbl_subtype": "Incident Subtype",
        "lbl_caller_name": "Caller Name",
        "lbl_caller_loc": "Caller Location",
        "lbl_district": "District",
        
        # Audit Tab
        "lbl_audit_empty": "Automated Audit is currently pending. Please check back later.",

        # Reports Page
        "reports_title": "Historical Reports",
        "reports_desc": "Browse and review previously processed ERSS call reports.",
        "reports_empty_state": "Select a recording above to view its analysis report.",
        
        # Audio Widget (New States)
        "audio_no_report": "Audio found, but no corresponding analysis report exists yet.",

        # Audit Tab
        "lbl_audit_title": "AUDIT REPORT",
        "lbl_total_score": "Total Weighted Score",
        "lbl_verdict": "Performance Verdict",
        "lbl_vocal_score": "Overall Vocal Score",
        "lbl_script_comp": "Script & Protocol Compliance",
        "lbl_op_stat": "Opening Statement",
        "lbl_info_gath": "Information Gathering",
        "lbl_caller_mgt": "Caller Management",
        "lbl_cl_stat": "Closing Statement",
        "lbl_silence_ana": "Silence Analysis",
        "lbl_soft_skills": "Soft Skills & Behavioral Analysis",
        "lbl_justification": "Audit Justification",
        "lbl_adaptive": "Adaptive Dimensions",
        "lbl_qualitative": "Qualitative Traits",
    },

    "hi": {
        "nav_home": "होम",
        "nav_analysis": "कॉल विश्लेषण",
        "nav_reports": "रिपोर्ट्स",
        "home_title": "ERSS AI ऑपरेशंस",
        "home_subtitle": "परफ़ॉर्मेंस डेटा देखें।",
        "car_title_1": "रीयल-टाइम ऑडियो विश्लेषण",
        "car_desc_1": "आपातकालीन कॉल 30 सेकंड में प्रोसेस करें।",
        "car_title_2": "स्वचालित ऑडिटिंग",
        "car_desc_2": "सभी कॉल ऑपरेटर में 100% प्रोटोकॉल अनुपालन सुनिश्चित करें।",
        "car_title_3": "व्यापक प्रदर्शन रिपोर्ट",
        "car_desc_3": "परफॉर्मेंस मेट्रिक्स का ऑडिट करें और इनसाइट्स तैयार करें।",
        "analysis_title": "कॉल विश्लेषण",
        "analysis_desc": "AI ट्रांसक्रिप्शन, समरी और प्रोटोकॉल ऑडिटिंग के लिए ERSS ऑडियो अपलोड करें।",
        "brand_title": "ERSS ट्रांसक्रिप्ट समाधान",

        # Metrics
        "metric_1_title": "कुल कॉल (इस हफ़्ते)",
        "metric_1_delta": "पिछले 7 दिनों के मुकाबले 5.2%",
        "metric_2_title": "औसत अनुपालन स्कोर",
        "metric_2_delta": "1.2% सुधार पिछले 7 दिनों से",
        "metric_3_title": "उच्च गंभीरता कॉल",
        "metric_3_delta": "-2.1% पिछले 7 दिनों से",

        # Categories for Graph 1
        "cat_police": "पुलिस (112)",
        "cat_medical": "चिकित्सा (108)",
        "cat_traffic": "यातायात",
        "cat_fire": "अग्नि (101)",
        "cat_women": "महिला हेल्पलाइन (1090)",
        "cat_other": "अन्य",

        # Graph 1 & 2 Labels
        "graph_1_title": "श्रेणी के अनुसार कॉल (पिछले सप्ताह)",
        "graph_1_x": "श्रेणी",
        "graph_1_y": "कॉल की संख्या",
        "graph_2_title": "कॉल टेकर द्वारा KPI अनुपालन (n=20)",
        "graph_2_x": "कॉल टेकर",
        "graph_2_y": "स्कोर (100 में से)",
        "agent_prefix": "एजेंट",

        # Graph 3 & 4 Labels
        "graph_3_title": "कॉल गंभीरता का विवरण",
        "graph_3_cat": "गंभीरता",
        "graph_3_val": "प्रतिशत",
        "sev_low": "कम",
        "sev_med": "मध्यम",
        "sev_high": "उच्च",
        "graph_4_title": "आज का प्रति घंटा अनुपालन रुझान",
        "graph_4_x": "दिन का घंटा",
        "graph_4_y": "अनुपालन स्कोर",

        # About Section
        "about_title": "हमारी सेवा के बारे में",
        "about_card1_title": "AI आधारित ERSS ट्रांसक्रिप्शन और ऑडिटिंग का प्रभाव",
        "about_card1_desc": "तेज ऑडिट चक्र, ऑपरेटर जवाबदेही, स्वचालित निगरानी, कार्रवाई योग्य अंतर्दृष्टि...",
        "about_card2_title": "उपयोग किए गए उपकरण और तकनीकें",
        "about_card2_desc": "भावना विश्लेषण, कीवर्ड विश्लेषण, इरादे का पता लगाने और बहुत कुछ के लिए Open AI फास्टर व्हिस्पर मॉडल और Groq का AI मॉडल।",
        "about_card3_title": "कॉल ट्रांसक्रिप्शन पाइपलाइन",
        "about_card3_desc": "ERSS ऑडियो प्राप्त, VAD का उपयोग करके ऑडियो क्लीनअप, फीचर निष्कर्षण और वेक्टर एम्बेडिंग, स्पीच टू टेक्स्ट ट्रांसफार्मर मॉडल, स्वरूपित ट्रांसक्रिप्ट, AI ऑडिटिंग लेयर।",

        # Audio Section
        "audio_section_title": "कॉल ऑडियो चुनें",
        "audio_section_desc": "कच्चे ERSS ऑडियो फ़ाइलों को फ़िल्टर करें और सुरक्षित रूप से सुनें।",
        "audio_date_label": "तारीख चुनें",
        "audio_hour_label": "घंटा चुनें",
        "audio_select_label": "उपलब्ध रिकॉर्डिंग",
        "audio_no_files": "इस विशिष्ट घंटे के लिए कोई ऑडियो फ़ाइल नहीं मिली।",
        "audio_folder_missing": "'Audios' फ़ोल्डर गायब है। कृपया इसे रूट डायरेक्टरी में बनाएं।",
        # Audio Widget (Range Filters)
        "audio_start_date": "आरंभ तिथि",
        "audio_end_date": "अंतिम तिथि",
        "audio_start_hour": "आरंभिक समय",
        "audio_end_hour": "समाप्ति समय",
        "audio_invalid_range": "आरंभ तिथि/समय अंतिम तिथि/समय के बाद नहीं हो सकता।",
        "audio_no_files_range": "इस चयनित समय सीमा के भीतर कोई ऑडियो फ़ाइल नहीं मिली।",

        # Call Analysis Page
        "lbl_upload": "ऑडियो फ़ाइल अपलोड करें (.wav, .mp3)",
        "lbl_taker_id": "कॉल टेकर ID",
        "lbl_analyze_btn": "कॉल का विश्लेषण करें",
        "lbl_loading": "AI ऑडियो प्रोसेस कर रहा है (ट्रांसक्रिप्शन, NLP, ऑडिटिंग)... कृपया प्रतीक्षा करें।",
        "err_no_file": "कृपया पहले एक ऑडियो फ़ाइल अपलोड करें।",
        "err_no_id": "कृपया कॉल टेकर ID दर्ज करें।",
        "tab_trans_sum": "ट्रांसक्रिप्शन और सारांश",
        "tab_audit": "ऑडिट",
        
        # Transcription Tab Details
        "lbl_incident_type": "घटना का प्रकार",
        "lbl_severity": "गंभीरता",
        "lbl_caller": "कॉलर और स्थान",
        "lbl_key_facts": "प्रमुख स्थापित तथ्य",
        "lbl_dispatcher_actions": "कॉल ऑपरेटर की कार्रवाई",
        "lbl_entities": "महत्वपूर्ण संस्थाएं",
        "lbl_final_summary": "सारांश",
        "lbl_transcript": "कॉल ट्रांसक्रिप्ट",
        
        # Transcript & Summary Updates
        "lbl_call_summary_title": "कॉल सारांश",
        "lbl_incident_overview": "घटना का अवलोकन",
        "lbl_add_info": "अतिरिक्त जानकारी",
        "lbl_no_data": "कोई अतिरिक्त डेटा उपलब्ध नहीं है।",
        "lbl_subtype": "घटना उप-प्रकार",
        "lbl_caller_name": "कॉलर का नाम",
        "lbl_caller_loc": "कॉलर का स्थान",
        "lbl_district": "ज़िला",
        
        # Audit Tab
        "lbl_audit_empty": "स्वचालित ऑडिट वर्तमान में लंबित है। कृपया बाद में जांचें।",

        # Reports Page
        "reports_title": "ऐतिहासिक रिपोर्ट",
        "reports_desc": "पहले से प्रोसेस किए गए ERSS कॉल रिपोर्ट ब्राउज़ करें और समीक्षा करें।",
        "reports_empty_state": "इसका विश्लेषण रिपोर्ट देखने के लिए ऊपर एक रिकॉर्डिंग चुनें।",
        
        # Audio Widget (New States)
        "audio_no_report": "ऑडियो मिला, लेकिन अभी तक कोई संबंधित विश्लेषण रिपोर्ट मौजूद नहीं है।",

        # Audit Tab
        "lbl_audit_title": "ऑडिट रिपोर्ट",
        "lbl_total_score": "कुल भारित स्कोर",
        "lbl_verdict": "प्रदर्शन निर्णय",
        "lbl_vocal_score": "कुल वोकल स्कोर",
        "lbl_script_comp": "स्क्रिप्ट और प्रोटोकॉल अनुपालन",
        "lbl_op_stat": "प्रारंभिक वक्तव्य",
        "lbl_info_gath": "जानकारी एकत्र करना",
        "lbl_caller_mgt": "कॉलर प्रबंधन",
        "lbl_cl_stat": "समापन वक्तव्य",
        "lbl_silence_ana": "मौन विश्लेषण",
        "lbl_soft_skills": "सॉफ्ट स्किल्स और व्यवहार विश्लेषण",
        "lbl_justification": "ऑडिट औचित्य",
        "lbl_adaptive": "अनुकूली आयाम",
        "lbl_qualitative": "गुणात्मक लक्षण",
    }
}