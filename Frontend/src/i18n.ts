import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

// Initial translations
const resources = {
    en: {
        translation: {
            "app.title": "Criminal Law Knowledge Base",
            "nav.home": "Home",
            "nav.search": "Search",
            "nav.chat": "Chat",
            "nav.about": "About",
            "nav.contact": "Contact",
            "hero.title": "AI-Powered Legal Search",
            "hero.subtitle": "Find relevant criminal law sections, analyze precedents, and get intelligent recommendations.",
            "search.placeholder": "Search for laws, cases, or legal concepts...",
            "search.button": "Search",
            "footer.copyright": "© 2024 Criminal Law Knowledge Base. All rights reserved.",
            "error.generic": "Something went wrong",
            "error.reload": "Reload Page",
            "error.home": "Go Home"
        }
    },
    hi: {
        translation: {
            "app.title": "आपराधिक कानून ज्ञान आधार",
            "nav.home": "होम",
            "nav.search": "खोजें",
            "nav.chat": "चैट",
            "nav.about": "हमारे बारे में",
            "nav.contact": "संपर्क",
            "hero.title": "एआई-संचालित कानूनी खोज",
            "hero.subtitle": "प्रासंगिक आपराधिक कानून धाराएं खोजें, नजीरों का विश्लेषण करें और बुद्धिमान सिफारिशें प्राप्त करें।",
            "search.placeholder": "कानून, मामले या कानूनी अवधारणाएं खोजें...",
            "search.button": "खोजें",
            "footer.copyright": "© 2024 आपराधिक कानून ज्ञान आधार। सर्वाधिकार सुरक्षित।",
            "error.generic": "कुछ गलत हो गया",
            "error.reload": "पेज रीलोड करें",
            "error.home": "होम पर जाएं"
        }
    }
};

i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
        resources,
        fallbackLng: "en",
        interpolation: {
            escapeValue: false // react already safes from xss
        }
    });

export default i18n;
