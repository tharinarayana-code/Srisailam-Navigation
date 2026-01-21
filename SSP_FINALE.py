import pandas as pd
import json
from pathlib import Path

# ======================================================
# CONFIGURATION SECTION
# ======================================================

# Public Google Sheet CSV URL
GOOGLE_SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_lzbX4EaUcfvJjJZVl-AcMdyosxKyhghJZwvm1wlD0lE7UqFpLH73Lh3eHQf0pPr6pXZag8P64odh/pub?output=csv"
)

# Required columns that MUST exist in the Google Sheet
REQUIRED_COLUMNS = [
    "display name",
    "name_te",
    "name_hi",
    "name_ta",
    "name_kn",
    "name_ml",
    "description_en",
    "description_te",
    "description_hi",
    "description_ta",
    "description_kn",
    "description_ml",
    "category",
    "latitude",
    "longitude"
]

# Output folder name
OUTPUT_FOLDER = "Srisailam_Navigation_Output"

# ======================================================
# OUTPUT DIRECTORY SETUP
# ======================================================

# Try saving on Desktop; fallback to current directory
desktop = Path.home() / "Desktop"
base_dir = (desktop if desktop.exists() else Path.cwd()) / OUTPUT_FOLDER
base_dir.mkdir(parents=True, exist_ok=True)

# Output file paths
json_file = base_dir / "locations.json"
html_file = base_dir / "index.html"
js_file = base_dir / "app.js"
css_file = base_dir / "style2.css"

# ======================================================
# READ & CLEAN GOOGLE SHEET DATA
# ======================================================

# ============ READ & CLEAN DATA ============
df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
df.columns = df.columns.str.strip().str.lower()

# ✅ FIX: Replace NaN values with empty strings
df = df.fillna("")


# Check for missing required columns
for col in REQUIRED_COLUMNS:
    if col not in df.columns:
        raise ValueError(f"Missing required column: {col}")

# Convert latitude & longitude to numeric values
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

# Normalize category values
df["category"] = df["category"].astype(str).str.strip().str.upper()

# Remove rows with invalid coordinates
before = len(df)
df.dropna(subset=["latitude", "longitude"], inplace=True)
skipped = before - len(df)

if skipped:
    print(f"⚠️ Skipped {skipped} invalid rows due to missing coordinates")

# Keep only required columns
df = df[REQUIRED_COLUMNS]

# Convert DataFrame to list of dictionaries
locations = df.to_dict(orient="records")

# ======================================================
# WRITE JSON FILE (UNCHANGED STRUCTURE)
# ======================================================

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(locations, f, indent=2, ensure_ascii=False)

# ======================================================
# WRITE HTML FILE (UNCHANGED CONTENT)
# ======================================================

html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-VV51QJ8C7L"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-VV51QJ8C7L');
</script>

  <link rel="stylesheet" href="style2.css">
  <meta charset="UTF-8">
  <title>Srisailam Smart Navigation</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  
  <link rel="icon" type="image/png" href="logo.jpg">
  <style>
      /* --- FOOTER CREDITS STYLING (Subtle/Hidden mode) --- */
      .dev-credit {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    color: #666; /* Changed from #999 to #666 for darker, more visible text */
    text-decoration: none;
    font-weight: normal;
    transition: all 0.2s ease;
    padding: 0 4px;
}

      /* Only show color when someone actually hovers over it */
      .dev-credit:hover {
          color: #0077b5; 
          opacity: 1;
      }

      .dev-credit svg {
    width: 14px; /* Increased from 12px to 14px */
    height: 14px; /* Increased from 12px to 14px */
    fill: currentColor;
    position: relative;
    top: -1px; 
}

      .divider {
          color: #ddd; /* Very faint divider */
          margin: 0 3px;
      }
      
      /* Wrapper to push it to bottom */
      #developer-credits {
    margin-top: 25px; 
    padding-top: 10px;
    border-top: 1px solid #f0f0f0;
    font-size: 14px; /* Increased from 11px to 14px */
    opacity: 0.85; /* Increased from 0.6 to 0.85 */
}
      
      #developer-credits:hover {
          opacity: 1; /* Make it visible if they intentionally look at it */
      }
  </style>
</head>
<body id="top">
<header>
  <h1 id="app-title">Srisailam Temple Area Navigation</h1>
  <h4 id="app-subtitle">Select category → choose place → navigate</h4>
  
  <div id="language-selector">
      <label id="lang-label" for="lang">Language:</label>
      <select id="lang">
          <option value="en">English</option>
          <option value="te">తెలుగు</option>
          <option value="hi">हिंदी</option>
          <option value="ta">தமிழ்</option>
          <option value="kn">ಕನ್ನಡ</option>
          <option value="ml">മലയാളം</option>
      </select>
  </div>
  <div id="search-box">
      <div style="position: relative; max-width: 500px; margin: 0 auto;">
          <input
              type="text"
              id="searchInput"
              placeholder="Search places, food, temples…"
          />
          <button 
              id="clearSearch" 
              type="button"
              style="display: none;"
              aria-label="Clear search"
          >✕</button>
      </div>
  </div>
  <div id="free-darshan-container" style="margin: 15px 0;"></div>
</header>
</header> 
<div id="hero-section" style="
    max-width: 600px; 
    margin: 10px auto 20px auto; 
    padding: 0 15px; 
    text-align: center;
">
    <div style="
        position: relative;
        border-radius: 15px; 
        overflow: hidden; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border: 2px solid #fff;
    ">
        <img 
            src="temple_banner.jpeg" 
            alt="Srisailam Mallikarjuna Swamy Temple" 
            style="
                width: 100%; 
                height: 200px; /* Fixed height for consistency */
                object-fit: cover; /* Ensures image covers area without stretching */
                display: block;
            "
        >
    </div>
</div>
<main id="app"></main>

<section id="search-results" style="display:none;">
  <h2 id="search-title">Search Results</h2>
  <ul id="search-list"></ul>
</section>

<a href="#top" id="back-to-top" aria-label="Back to top">
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
    <line x1="12" y1="30" x2="12" y2="5"></line>
    <polyline points="5 12 12 5 19 12"></polyline>
  </svg>
</a>

<footer id="temple-footer">
    <p id="footer-note" style="font-size: 13px; color: #777; text-align:center;">
        Navigation is provided via Google Maps. Routes may vary based on traffic and conditions.
    </p>

    <p id="footer-update" style="font-size: 13px; color: #777; text-align:center;">
        Last updated: December 2025
    </p>

    <div id="developer-credits" style="text-align: center; display: flex; justify-content: center; align-items: center; flex-wrap: wrap;">
        <span style="margin-right: 4px;">Developed by: </span>
        
        <a href="https://www.linkedin.com/in/bhodini-gundu" target="_blank" class="dev-credit">
            <svg viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
            Gundu Bhodini
        </a>
    
        <span class="divider">|</span>

        <a href="https://www.linkedin.com/in/aditya-karre" target="_blank" class="dev-credit">
            <svg viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
            Aditya Karre
        </a>

    </div>
</footer>

<script src="app.js"></script>

</body>
</html>
"""

with open(html_file, "w", encoding="utf-8") as f:
    f.write(html)

# ======================================================
# WRITE JAVASCRIPT FILE
# ======================================================

js_code = """
/* ================= GLOBAL STATE ================= */
let locationsData = [];
let currentLang = "en";
let searchQuery = "";
let openCategoryList = null; // tracks currently opened category list
let openLocationDetails = null; // tracks open location description

// ================= HISTORY INIT (iOS SUPPORT) =================
history.replaceState({ level: "home" }, "");

/* ================= STATIC UI TRANSLATIONS ================= */
const STATIC_TRANSLATIONS = {
  title: {
    en: "Srisailam Temple Area Navigation",
    te: "శ్రీశైలం ఆలయ ప్రాంత నావిగేషన్",
    hi: "श्रीशैलम मंदिर क्षेत्र नेविगेशन",
    ta: "ஸ்ரீசைலம் கோவில் பகுதி வழிசெலுத்தல்",
    kn: "ಶ್ರೀಶೈಲಂ ದೇವಾಲಯ ಪ್ರದೇಶ ನ್ಯಾವಿಗೇಷನ್",
    ml: "ശ്രീശൈലം ക്ഷേത്ര പരിസര നാവിഗേഷൻ"
  },
  subtitle: {
    en: "Select category → choose place → navigate",
    te: "వర్గాన్ని ఎంచుకోండి → స్థలాన్ని ఎంచుకోండి → నావిగేట్ చేయండి",
    hi: "श्रेणी चुनें → स्थान चुनें → नेविगेट करें",
    ta: "வகையைத் தேர்ந்தெடுக்கவும் → இடத்தைத் தேர்ந்தெடுக்கவும் → வழிகாட்டவும்",
    kn: "ವರ್ಗವನ್ನು ಆಯ್ಕೆಮಾಡಿ → ಸ್ಥಳವನ್ನು ಆಯ್ಕೆಮಾಡಿ → ನ್ಯಾವಿಗೇಟ್ ಮಾಡಿ",
    ml: "വിഭാഗം തിരഞ്ഞെടുക്കുക → സ്ഥലം തിരഞ്ഞെടുക്കുക → നാവിഗേറ്റ് ചെയ്യുക"
  },
  langLabel: {
    en: "Language:",
    te: "భాష:",
    hi: "भाषा:",
    ta: "மொழி:",
    kn: "ಭಾಷೆ:",
    ml: "ഭാഷ:"
  },
  searchPlaceholder: {
    en: "Search places, food, temples…",
    te: "స్థలాలు, ఆహారం, ఆలయాలను వెతకండి...",
    hi: "स्थान, भोजन, मंदिर खोजें...",
    ta: "இடங்கள், உணவு, கோவில்களைத் தேடுங்கள்...",
    kn: "ಸ್ಥಳಗಳು, ಆಹಾರ, ದೇವಾಲಯಗಳನ್ನು ಹುಡುಕಿ...",
    ml: "സ്ഥലങ്ങൾ, ഭക്ഷണം, ക്ഷേത്രങ്ങൾ എന്നിവ തിരയുക..."
  },
  searchTitle: {
    en: "Search Results",
    te: "శోధన ఫలితాలు",
    hi: "खोज परिणाम",
    ta: "தேடல் முடிவுகள்",
    kn: "ಹುಡುಕಾಟ ಫಲಿತಾಂಶಗಳು",
    ml: "തിരയൽ ഫലങ്ങൾ"
  }
};

function updateStaticText() {
  const titleEl = document.getElementById("app-title");
  if(titleEl) titleEl.textContent = STATIC_TRANSLATIONS.title[currentLang] || STATIC_TRANSLATIONS.title.en;

  const subtitleEl = document.getElementById("app-subtitle");
  if(subtitleEl) subtitleEl.textContent = STATIC_TRANSLATIONS.subtitle[currentLang] || STATIC_TRANSLATIONS.subtitle.en;

  const langLabelEl = document.getElementById("lang-label");
  if(langLabelEl) langLabelEl.textContent = STATIC_TRANSLATIONS.langLabel[currentLang] || STATIC_TRANSLATIONS.langLabel.en;

  const searchInputEl = document.getElementById("searchInput");
  if(searchInputEl) searchInputEl.placeholder = STATIC_TRANSLATIONS.searchPlaceholder[currentLang] || STATIC_TRANSLATIONS.searchPlaceholder.en;

  const searchTitleEl = document.getElementById("search-title");
  if(searchTitleEl) searchTitleEl.textContent = STATIC_TRANSLATIONS.searchTitle[currentLang] || STATIC_TRANSLATIONS.searchTitle.en;
}

/* ================= LOAD DATA ================= */
fetch("locations.json")
  .then(res => res.json())
  .then(data => {
    locationsData = data;
    searchQuery = "";
    updateStaticText();
    document.getElementById("app").style.display = "block";
    document.getElementById("search-results").style.display = "none";
    renderApp();
  })
  .catch(err => console.error("Failed to load locations.json", err));

/* ================= CATEGORY LABELS ================= */
const CATEGORY_LABELS = {
  TEMPLE:{en:"Temples",te:"ఆలయాలు",hi:"मंदिर",ta:"கோவில்கள்",kn:"ದೇವಾಲಯಗಳು",ml:"ക്ഷേത്രങ്ങൾ"},
  ASHRAM:{en:"Ashrams / Mathams",te:"ఆశ్రమాలు / మఠాలు",hi:"आश्रम / मठ",ta:"ஆசிரமங்கள் / மடங்கள்",kn:"ಆಶ್ರಮಗಳು / ಮಠಗಳು",ml:"ആശ്രമങ്ങൾ / മഠങ്ങൾ"},
  ACCOMMODATION:{en:"Accommodation",te:"వసతి",hi:"आवास",ta:"தங்குமிடம்",kn:"ವಸತಿ",ml:"താമസം"},
  FOOD:{en:"Food",te:"ఆహారం",hi:"भोजन",ta:"உணவு",kn:"ಆಹಾರ",ml:"ഭക്ഷണം"},
  FACILITY:{en:"Facilities",te:"సౌకర్యాలు",hi:"सुविधाएं",ta:"வசதிகள்",kn:"ಸೌಲಭ್ಯಗಳು",ml:"സൗകര്യങ്ങൾ"},
  TRANSPORT:{en:"Transport",te:"రవాణా",hi:"परिवहन",ta:"போக்குவரத்து",kn:"ಸಾರಿಗೆ",ml:"ഗതാഗതം"},
  UTILITY:{en:"Utilities",te:"సేవలు",hi:"सेवाएं",ta:"சேவைகள்",kn:"ಸೇವೆಗಳು",ml:"സേവനങ്ങൾ"},
  TOURIST_SPOT:{en:"Tourist Spots",te:"పర్యాటక ప్రాంతాలు",hi:"पर्यटन स्थल",ta:"சுற்றுலா இடங்கள்",kn:"ಪರ್ಯಟನಾ ಸ್ಥಳಗಳು",ml:"സഞ്ചാര കേന്ദ്രങ്ങൾ"}
};

/* ================= BUTTON LABELS ================= */
const BUTTON_LABELS = {
  openMaps: {
    en: "Open in Google Maps",
    te: "గూగుల్ మ్యాప్స్‌లో తెరవండి",
    hi: "गूगल मैप्स में खोलें",
    ta: "கூகுள் மேப்ஸில் திறக்கவும்",
    kn: "ಗೂಗಲ್ ಮ್ಯಾಪ್ಸ್‌ನಲ್ಲಿ ತೆರೆಯಿರಿ",
    ml: "ഗൂഗിൾ മാപ്സിൽ തുറക്കുക"
  },
  navigate: {
    en: "Navigate",
    te: "నావిగేట్ చేయండి",
    hi: "नेविगेट करें",
    ta: "வழிகாட்டு",
    kn: "ನ್ಯಾವಿಗೇಟ್ ಮಾಡಿ",
    ml: "നാവിഗേറ്റ് ചെയ്യുക"
  }
};

/* ================= SMART SEARCH MATCH ================= */
function matchesSearch(l) {
  if (!searchQuery) return true;

  const query = searchQuery.toLowerCase();
  const allLanguages = ['en', 'te', 'hi', 'ta', 'kn', 'ml'];
  
  let searchableText = "";
  searchableText += (l["display name"] || "").toLowerCase() + " ";
  
  allLanguages.forEach(lang => {
    searchableText += (l["name_" + lang] || "").toLowerCase() + " ";
  });
  
  allLanguages.forEach(lang => {
    const catLabel = CATEGORY_LABELS[l.category]?.[lang];
    if (catLabel) {
      searchableText += catLabel.toLowerCase() + " ";
    }
  });
  
  searchableText += (l.category || "").toLowerCase().replace(/_/g, " ") + " ";
  
  allLanguages.forEach(lang => {
    searchableText += (l["description_" + lang] || "").toLowerCase() + " ";
  });
  
  return searchableText.includes(query);
}

/* ================= FREE DARSHAN (STANDALONE) ================= */
function renderFreeDarshan() {
  const container = document.getElementById("free-darshan-container");
  container.innerHTML = "";

  const free = locationsData.find(
    l => l.category === "SARVA DARSHANAM ENTRANCE"
  );
  if (!free) return;

  const btn = document.createElement("button");
  btn.textContent =
    free["name_" + currentLang] || free["display name"];

  btn.onclick = () =>
  window.open(
    `https://www.google.com/maps/search/?api=1&query=${free.latitude},${free.longitude}`,
    "_blank"
  );

  btn.style.padding = "12px 16px";
  btn.style.fontSize = "16px";
  btn.style.fontWeight = "bold";
  btn.style.cursor = "pointer";

  container.appendChild(btn);
}

/* ================= BROWSE MODE ================= */
function renderApp() {
  renderFreeDarshan();

  const app = document.getElementById("app");
  app.innerHTML = "";
  app.style.display = "block";
  document.getElementById("search-results").style.display = "none";

  const CATEGORY_ICONS = {
    TEMPLE: "🛕",
    ASHRAM: "🕉️",
    ACCOMMODATION: "🏨",
    FOOD: "🍛",
    FACILITY: "🏥",
    TRANSPORT: "🚌",
    UTILITY: "🔧",
    TOURIST_SPOT: "🏞️"
  };

  const grouped = {};
  locationsData
    .filter(l => l.category !== "SARVA DARSHANAM ENTRANCE")
    .forEach(l => (grouped[l.category] ||= []).push(l));

  for (const cat in grouped) {
    const section = document.createElement("section");
    const h = document.createElement("h2");
    
    const iconSpan = document.createElement("span");
    iconSpan.textContent = CATEGORY_ICONS[cat] || "📍";
    iconSpan.style.fontSize = "24px";
    iconSpan.style.marginRight = "12px";
    h.appendChild(iconSpan);
    
    const textNode = document.createTextNode(CATEGORY_LABELS[cat]?.[currentLang] || cat);
    h.appendChild(textNode);
    
    h.style.cursor = "pointer";

    const ul = document.createElement("ul");
    ul.style.display = "none";

  h.onclick = () => {
  const isOpen = ul.style.display === "block";

  // Close all categories & location details
  document.querySelectorAll("#app ul").forEach(u => u.style.display = "none");
  document.querySelectorAll("#app ul div").forEach(d => d.style.display = "none");

  if (!isOpen) {
    ul.style.display = "block";

    // ⬅ push CATEGORY level
    history.pushState({ level: "category" }, "");
  } else {
    ul.style.display = "none";
  }
};
    grouped[cat].forEach(l => {
      const li = document.createElement("li");

      const name = document.createElement("strong");
      name.textContent = l["name_" + currentLang] || l["display name"];
      name.style.cursor = "pointer";

      const details = document.createElement("div");
      details.style.display = "none";

      if (l["description_" + currentLang]) {
        const desc = document.createElement("p");
        desc.textContent = l["description_" + currentLang];
        desc.style.margin = "6px 0";
        details.append(desc);
      }
      
      const btn = document.createElement("button");
      btn.textContent = BUTTON_LABELS.navigate[currentLang];
      
      btn.onclick = () =>
        window.open(
          `https://www.google.com/maps/search/?api=1&query=${l.latitude},${l.longitude}`,
          "_blank"
        );

      details.append(btn);

      name.onclick = () => {
  const isOpen = details.style.display === "block";

  // Close other open locations in this category
  ul.querySelectorAll("div").forEach(d => d.style.display = "none");

  if (!isOpen) {
    details.style.display = "block";

    // ⬅ push LOCATION level
    history.pushState({ level: "location" }, "");
  } else {
    details.style.display = "none";
  }
};
      li.append(name, details);
      ul.append(li);
    });

    section.append(h, ul, document.createElement("hr"));
    app.append(section);
  }
}

/* ================= SEARCH MODE ================= */
function renderSearchResults() {
  const list = document.getElementById("search-list");
  list.innerHTML = "";

  const results = locationsData
    .filter(l => l.category !== "SARVA DARSHANAM ENTRANCE")
    .filter(matchesSearch);

  if (results.length === 0) {
    list.innerHTML = "<li>No matching locations found</li>";
  } else {
    results.forEach(l => {
      const li = document.createElement("li");

      const name = document.createElement("strong");
      name.textContent = l["name_" + currentLang] || l["display name"];
      name.style.cursor = "pointer";

      const details = document.createElement("div");
      details.style.display = "none";

      if (l["description_" + currentLang]) {
        const desc = document.createElement("p");
        desc.textContent = l["description_" + currentLang];
        desc.style.margin = "6px 0";
        details.append(desc);
      }

      const btn = document.createElement("button");
      btn.textContent = BUTTON_LABELS.navigate[currentLang];
      
      btn.onclick = () =>
        window.open(
          `https://www.google.com/maps/search/?api=1&query=${l.latitude},${l.longitude}`,
          "_blank"
        );

      details.append(btn);

      name.onclick = () => {
        const isOpen = details.style.display === "block";
        document.querySelectorAll("#search-list div").forEach(d => d.style.display = "none");
        details.style.display = isOpen ? "none" : "block";
      };

      li.append(name, details);
      list.append(li);
    });
  }

  document.getElementById("app").style.display = "none";
  document.getElementById("search-results").style.display = "block";
}

/* ================= EVENTS ================= */
document.getElementById("lang").addEventListener("change", e => {
  currentLang = e.target.value;
  updateStaticText();
  searchQuery ? renderSearchResults() : renderApp();
});

const searchInput = document.getElementById("searchInput");
const clearBtn = document.getElementById("clearSearch");

searchInput.addEventListener("input", e => {
  searchQuery = e.target.value.trim().toLowerCase();
  clearBtn.style.display = searchQuery ? "flex" : "none";

  const hero = document.getElementById("hero-section");

  if (searchQuery) {
    if (hero) hero.style.display = "none";   // 🔴 HIDE IMAGE
    renderSearchResults();
  } else {
    if (hero) hero.style.display = "block";  // 🟢 SHOW IMAGE
    renderApp();
  }
});


clearBtn.addEventListener("click", () => {
  const hero = document.getElementById("hero-section");

  searchInput.value = "";
  searchQuery = "";
  clearBtn.style.display = "none";

  if (hero) hero.style.display = "block"; // 🟢 SHOW IMAGE AGAIN

  renderApp();
  searchInput.focus();
});


/* ================= BACK TO TOP VISIBILITY ================= */
document.addEventListener("DOMContentLoaded", () => {
  const backToTopBtn = document.getElementById("back-to-top");
  if (!backToTopBtn) return;
  backToTopBtn.style.display = "none";
  window.addEventListener("scroll", () => {
    if (window.scrollY > 150) {
      backToTopBtn.style.display = "flex"; 
    } else {
      backToTopBtn.style.display = "none";
    }
  });
});
// ================= FINAL BACK / SWIPE HANDLING =================
window.addEventListener("popstate", () => {

  // 1️⃣ If a LOCATION description is open → close it
  const openLocation = document.querySelector(
    '#app ul li div[style*="block"]'
  );
  if (openLocation) {
    openLocation.style.display = "none";
    return;
  }

  // 2️⃣ Else if a CATEGORY list is open → close it
  const openCategory = document.querySelector(
    '#app ul[style*="block"]'
  );
  if (openCategory) {
    openCategory.style.display = "none";
    return;
  }

  // 3️⃣ Else → allow browser to exit
});

/* ================= BASIC INSPECT BLOCKING (DESKTOP ONLY) ================= */
document.addEventListener("contextmenu", function (e) {
  e.preventDefault();
});

document.addEventListener("keydown", function (e) {
  if (
    e.key === "F12" ||
    (e.ctrlKey && e.shiftKey && ["I", "J", "C"].includes(e.key)) ||
    (e.ctrlKey && e.key === "U")
  ) {
    e.preventDefault();
  }
});

"""

with open(js_file, "w", encoding="utf-8") as f:
    f.write(js_code)

# ======================================================
# WRITE CSS FILE
# ======================================================

css_code = """

/* ================= RESET & BASE ================= */
html {
  scroll-behavior: smooth;
}

footer {
  padding-bottom: 120px; /* creates space for back-to-top button */
}

footer p,
footer .developed-by {
  font-size: 14px;
  color: #666;
  text-align: center;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 16px;
  line-height: 1.6;
  color: #333;
  background-color: #faf9f7;
  padding: 0;
  margin: 0;
}

/* ================= HEADER ================= */
header {
  background: linear-gradient(135deg, #ff9933 0%, #ff7722 100%);
  color: white;
  padding: 24px 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

header h1 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  letter-spacing: 0.5px;
}

header > p {
  font-size: 15px;
  margin-bottom: 20px;
  opacity: 0.95;
  font-weight: 400;
}

/* ================= LANGUAGE SELECTOR ================= */
#language-selector {
  margin: 16px 0;
}

#language-selector label {
  font-size: 15px;
  margin-right: 10px;
  font-weight: 500;
}

#language-selector select {
  font-size: 16px;
  padding: 10px 14px;
  border: 2px solid white;
  border-radius: 8px;
  background-color: white;
  color: #333;
  cursor: pointer;
  min-width: 140px;
  font-weight: 500;
}

#language-selector select:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.3);
}

/* ================= SEARCH BOX ================= */
#search-box {
  margin: 16px 0 0 0;
}

#searchInput {
  width: 100%;
  max-width: 500px;
  font-size: 17px;
  padding: 14px 18px;
  border: 2px solid white;
  border-radius: 12px;
  background-color: white;
  color: #333;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

#searchInput::placeholder {
  color: #999;
  font-size: 16px;
}

#searchInput:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.3), 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* ================= FREE DARSHAN COUNTER ================= */
#free-darshan-container {
  margin: 20px 0 0 0;
}

#free-darshan-container button {
  background-color: #fff;
  color: #d84315;
  border: 3px solid #d84315;
  padding: 16px 28px;
  font-size: 18px;
  font-weight: 700;
  border-radius: 12px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(216, 67, 21, 0.2);
  transition: all 0.2s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

#free-darshan-container button:hover {
  background-color: #d84315;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(216, 67, 21, 0.3);
}

#free-darshan-container button:active {
  transform: translateY(0);
}

/* ================= MAIN CONTENT ================= */
main {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 16px;
}

/* ================= CATEGORY SECTIONS ================= */
section {
  margin-bottom: 28px;
}

section h2 {
  font-size: 22px;
  font-weight: 600;
  color: #d84315;
  padding: 16px 18px;
  background-color: #fff;
  border-left: 5px solid #ff9933;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  transition: all 0.2s ease;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Category Icon/Image */
section h2 img {
  width: 32px;
  height: 32px;
  object-fit: contain;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}
/* ⬇️ ADD THE NEW CODE RIGHT HERE ⬇️ */

/* Small mobile phones */
@media (max-width: 480px) {
  header {
    padding: 20px 12px;
  }

  header h1 {
    font-size: 24px;
  }

  header > p {
    font-size: 14px;
  }

  #searchInput {
    font-size: 16px;
    padding: 12px 16px;
  }

  #free-darshan-container button {
    padding: 14px 24px;
    font-size: 16px;
    width: 100%; /* Full width on small screens */
  }

  section h2 {
    font-size: 20px;
    padding: 14px 16px;
  }

  section ul li {
    padding: 16px 16px;
  }

  section ul li strong {
    font-size: 17px;
  }

  button {
    width: 100%; /* Full width buttons on mobile */
    padding: 14px 20px;
    font-size: 15px;
  }

  #back-to-top {
    bottom: 16px;
    right: 16px;
    width: 48px;
    height: 48px;
    line-height: 48px;
    font-size: 22px;
  }

  #language-selector select {
    min-width: 120px;
    padding: 10px 12px;
  }
}

/* Very small screens */
@media (max-width: 360px) {
  header h1 {
    font-size: 22px;
  }

  section h2 {
    font-size: 18px;
  }

  #free-darshan-container button {
    font-size: 15px;
    padding: 12px 20px;
  }
}

/* Improve touch targets for all interactive elements */
@media (hover: none) and (pointer: coarse) {
  /* Mobile/touch devices */
  button, 
  section h2, 
  section ul li strong,
  #searchInput,
  #language-selector select {
    min-height: 44px; /* Apple's recommended touch target */
  }
}
section h2:hover {
  background-color: #fff5f0;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.12);
}

section h2:active {
  transform: scale(0.98);
}

/* ================= LOCATION LISTS ================= */
section ul {
  list-style: none;
  padding: 0;
  margin: 0;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

section ul li {
  padding: 18px 20px;
  border-bottom: 1px solid #f0f0f0;
}

section ul li:last-child {
  border-bottom: none;
}

section ul li strong {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  cursor: pointer;
  padding: 4px 0;
  transition: color 0.2s ease;
}

section ul li strong:hover {
  color: #ff7722;
}

/* ================= LOCATION DETAILS ================= */
section ul li div {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

section ul li div p {
  font-size: 15px;
  line-height: 1.7;
  color: #555;
  margin: 8px 0 14px 0;
  max-width: 100%;
}

/* ================= NAVIGATION BUTTONS ================= */
button {
  background-color: #ff7722;
  color: white;
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(255, 119, 34, 0.3);
  transition: all 0.2s ease;
  margin-top: 8px;
}

button:hover {
  background-color: #ff9933;
  box-shadow: 0 4px 10px rgba(255, 119, 34, 0.4);
  transform: translateY(-1px);
}

button:active {
  transform: translateY(0);
}

/* ================= HORIZONTAL RULES ================= */
hr {
  border: none;
  height: 1px;
  background-color: #e0e0e0;
  margin: 24px 0;
}

/* ================= SEARCH RESULTS ================= */
#search-results {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 16px;
}

#search-results h2 {
  font-size: 24px;
  font-weight: 600;
  color: #d84315;
  margin-bottom: 16px;
}

#search-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

#search-list li {
  background-color: white;
  padding: 18px 20px;
  margin-bottom: 12px;
  border-radius: 8px;
  border-left: 4px solid #ff9933;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

#search-list li strong {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  cursor: pointer;
  padding: 4px 0;
  transition: color 0.2s ease;
}

#search-list li strong:hover {
  color: #ff7722;
}

#search-list li div {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

/* ================= BACK TO TOP BUTTON ================= */
#back-to-top {
    position: fixed;
    bottom: 30px;
    right: 30px;
    display: none;
    background-color: #ff6600;
    color: white;
    border: none;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    
    /* Flexbox centers the SVG icon perfectly */
    display: flex; /* Note: JS toggles this to 'flex' or 'none' */
    align-items: center;
    justify-content: center;
    
    cursor: pointer;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    z-index: 1000;
    transition: background-color 0.3s;
    text-decoration: none; /* Removes any underline lines */
}

/* Base size for the icon inside the button */
#back-to-top svg {
    width: 28px;
    height: 28px;
    stroke-width: 3px; /* Default thickness */
}

#back-to-top:hover {
    background-color: #cc5200;
}

/* Mobile - Make it BIG and BOLD for common users */
@media (max-width: 768px) {
    #back-to-top {
        bottom: 130px; /* aligns just above footer text */
        right: 20px;
    }
}


    #back-to-top svg {
        width: 36px;  /* Icon size */
        height: 36px;
        stroke-width: 4px; /* EXTRA THICK lines */
    }


/* Small screens */
@media (max-width: 480px) {
    #back-to-top {
        bottom: 150px; /* between footer and credits */
        right: 16px;
    }
}


    
    #back-to-top svg {
        width: 32px;
        height: 32px;
        stroke-width: 4px; /* Still keeping it thick */
    }


/* ================= FOOTER ================= */
footer {
  background-color: #f5f5f5;
  padding: 20px 16px;
  margin-top: 40px;
  border-top: 1px solid #e0e0e0;
}

footer p {
  font-size: 14px;
  color: #666;
  text-align: center;
  margin: 8px 0;
  line-height: 1.6;
}

/* ================= RESPONSIVE DESIGN ================= */

/* Tablet and larger */
@media (min-width: 768px) {
  header h1 {
    font-size: 32px;
  }

  header > p {
    font-size: 16px;
  }

  #searchInput {
    font-size: 18px;
    padding: 16px 20px;
  }

  section h2 {
    font-size: 24px;
    padding: 18px 22px;
  }

  section ul li strong {
    font-size: 19px;
  }

  section ul li div p {
    font-size: 16px;
  }

  #back-to-top {
    width: 56px;
    height: 56px;
    line-height: 56px;
    font-size: 26px;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  header h1 {
    font-size: 36px;
  }

  section h2 {
    font-size: 26px;
  }

  section ul li strong {
    font-size: 20px;
  }
}
.category-icon {
  font-size: 28px;
  margin-right: 12px;
  display: inline-flex;
  align-items: center;
  vertical-align: middle;
}

/* If using image icons instead */
section h2 img {
  width: 32px;
  height: 32px;
  object-fit: contain;
  margin-right: 12px;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}
/* ================= SEARCH CLEAR BUTTON ================= */
#clearSearch {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #999;
  font-size: 24px;
  width: 36px;
  height: 36px;
  padding: 0;
  cursor: pointer;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: none;
  margin: 0;
}

#clearSearch:hover {
  background-color: #f0f0f0;
  color: #d84315;
  transform: translateY(-50%) scale(1.1);
}

#clearSearch:active {
  transform: translateY(-50%) scale(0.95);
}

/* Adjust search input padding to make room for X button */
#searchInput {
  padding-right: 48px !important;
}

"""

with open(css_file, "w", encoding="utf-8") as f:
    f.write(css_code)

# ======================================================
# FINAL STATUS MESSAGE
# ======================================================

print("✅ All files generated successfully!")
print(f"📁 Output directory: {base_dir}")
print(f"📄 Locations count: {len(locations)}")
print("🧾 Files created: index.html, locations.json, app.js, style2.css")