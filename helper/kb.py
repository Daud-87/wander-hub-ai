"""Built-in Pakistan travel guide for the Wander Hub chatbot.

No API key and no external service: answers come from this curated list.
Prices are rough guides only and change often - the replies say so.
"""
import re

# months: 1-12 when the place is generally a good time to visit
PLACES = {
    "hunza": {
        "names": ["hunza", "karimabad", "altit", "baltit", "passu", "attabad", "gojal"],
        "title": "Hunza Valley (Gilgit-Baltistan)",
        "highlights": ["Baltit Fort and Altit Fort in Karimabad", "Attabad Lake and boat ride",
                       "Passu Cones and Hussaini Suspension Bridge", "Eagle's Nest viewpoint for sunrise/sunset",
                       "Khunjerab Pass (Pakistan-China border, usually open about May to November)"],
        "months": [4, 5, 6, 7, 8, 9, 10],
        "season": "April to October. Apple-blossom and cherry-blossom season is April; golden autumn colours are in October. Winters are very cold and some roads close.",
        "budget": "roughly PKR 8,000-25,000 per person per day depending on hotel class and transport (guesthouses are cheaper than lakeside resorts).",
        "pack": "layers: warm jacket for evenings, sun cap and sunscreen, comfortable walking shoes, power bank, some cash (ATMs are limited).",
        "safety": "Generally welcoming and popular with families. Road trips on the Karakoram Highway are long, so start early and check for landslide or road-closure updates before travelling.",
        "food": "Try Chapshuro, Hunza walnut cake, apricot dishes, Diram Fiti and fresh trout.",
        "reach": "Fly Islamabad to Gilgit (weather dependent) then drive about 2.5-3 hours, or take the Karakoram Highway by road from Islamabad (about 14-18 hours; usually broken into two days).",
        "tags": ["mountain", "family", "culture", "photography", "adventure", "honeymoon"],
    },
    "skardu": {
        "names": ["skardu", "shangrila", "shangrila resort", "kachura", "shigar", "katpana", "satpara"],
        "title": "Skardu (Gilgit-Baltistan)",
        "highlights": ["Shangrila Resort and Lower Kachura Lake", "Upper Kachura Lake", "Satpara Lake",
                       "Katpana Cold Desert", "Shigar Fort", "Gateway to K2 and Baltoro treks"],
        "months": [5, 6, 7, 8, 9, 10],
        "season": "May to early October. Deosai plains are open roughly June to September; autumn (September-October) is clear and beautiful.",
        "budget": "roughly PKR 10,000-30,000 per person per day, higher in peak summer when hotels and jeeps are in demand.",
        "pack": "warm layers, windproof jacket, sunglasses and sunscreen (high altitude sun), walking shoes, any personal medicines.",
        "safety": "Popular and safe for most travellers. Flights from Islamabad are often cancelled for weather, so keep spare days. Road routes (Karakoram Highway or via Astore) are long; check road status first.",
        "food": "Try local apricot products, Balti dishes like Mamtu and Chapshuro, and Kharmang tea.",
        "reach": "Fly Islamabad to Skardu (weather dependent) or drive via the Karakoram Highway/Gilgit or via Babusar and Astore (about 18-24 hours total, usually over two days).",
        "tags": ["mountain", "lakes", "adventure", "photography", "trekking", "honeymoon"],
    },
    "deosai": {
        "names": ["deosai", "sheosar", "land of giants"],
        "title": "Deosai National Park (near Skardu)",
        "highlights": ["Sheosar Lake", "Wildflower meadows in July-August", "Himalayan brown bear habitat",
                       "Sunset and stargazing on the plateau"],
        "months": [6, 7, 8, 9],
        "season": "June to September only; the plateau at about 4,100 m is snowbound the rest of the year.",
        "budget": "mostly jeep hire and entry fees, roughly PKR 15,000-30,000 per jeep for the day trip from Skardu.",
        "pack": "very warm layers even in summer, rain jacket, sunscreen, snacks and water (no shops on the plateau).",
        "safety": "Weather changes fast and the road is rough, so go with an experienced jeep driver and start early. Altitude can cause headaches, so go slowly.",
        "food": "Carry packed food; some seasonal tea stalls only.",
        "reach": "Jeep from Skardu (about 2.5-3 hours one way) or from Astore.",
        "tags": ["mountain", "adventure", "photography", "wildlife"],
    },
    "murree": {
        "names": ["murree", "patriata", "new murree", "nathia gali", "nathiagali", "galyat", "ayubia", "bhurban"],
        "title": "Murree and the Galyat hills",
        "highlights": ["Mall Road", "Patriata (New Murree) chairlift and cable car", "Pindi Point", "Ayubia National Park and chairlift",
                       "Nathia Gali walks"],
        "months": [4, 5, 6, 7, 8, 9, 12, 1, 2],
        "season": "April to September for pleasant weather and green hills; December to February for snowfall (very crowded on weekends).",
        "budget": "a weekend for two is roughly PKR 25,000-70,000 including a hotel (about PKR 8,000-25,000 per night), food and fuel. Prices rise on weekends and in snow season.",
        "pack": "warm jacket and umbrella; in winter snow boots and, if driving, snow chains.",
        "safety": "Very popular with families. In heavy snowfall roads can jam or close, so check weather and road updates, carry fuel, blankets and food, and avoid driving at night in snow.",
        "food": "Try roast chicken and chargha at Mall Road restaurants, corn on the cob, and hot tea.",
        "reach": "About 1.5-2.5 hours by road from Islamabad (60 km), depending on traffic.",
        "tags": ["family", "snow", "budget", "weekend", "honeymoon"],
    },
    "swat": {
        "names": ["swat", "kalam", "malam jabba", "mingora", "mahodand", "ushu", "fizagat", "bahrain", "madyan"],
        "title": "Swat Valley (Khyber Pakhtunkhwa)",
        "highlights": ["Kalam and Ushu Forest", "Mahodand Lake", "Malam Jabba", "Fizagat Park (Mingora)",
                       "Bahrain and Madyan riverside"],
        "months": [4, 5, 6, 7, 8, 9, 10],
        "season": "April to October. Summer (June-August) is the most comfortable; October has autumn colours. Winter is cold with snow in the upper valleys.",
        "budget": "roughly PKR 7,000-20,000 per person per day depending on hotel and jeep hire (Mahodand needs a jeep).",
        "pack": "layers, rain jacket, comfortable shoes, cash for jeeps and small shops.",
        "safety": "A popular family destination. Check current local conditions and weather before going, and avoid riverbanks after heavy rain because water can rise quickly.",
        "food": "Try Swati trout, chapli kebab, local honey and fresh fruit.",
        "reach": "Islamabad to Mingora by motorway and the Swat Expressway in about 4-5 hours; Kalam is another 3-4 hours.",
        "tags": ["mountain", "family", "lakes", "nature", "honeymoon"],
    },
    "naran": {
        "names": ["naran", "kaghan", "saif ul malook", "saiful malook", "saif-ul-malook", "lalazar", "babusar", "lulusar", "shogran", "siri paye top"],
        "title": "Naran, Kaghan Valley and Shogran",
        "highlights": ["Lake Saif-ul-Malook (jeep from Naran)", "Lalazar Plateau", "Lulusar Lake", "Babusar Top (seasonal)",
                       "Shogran and Siri Paye meadows"],
        "months": [6, 7, 8, 9],
        "season": "June to September. Upper areas and Babusar Top are usually open only from about June to October and can close with early snow; the valley is very cold and snowbound in winter.",
        "budget": "roughly PKR 7,000-20,000 per person per day; jeep rides to Saif-ul-Malook and Shogran are a significant part of the cost.",
        "pack": "warm jacket even in July (nights are cold), rain jacket, sturdy shoes, sunscreen, cash.",
        "safety": "Very popular with families. Roads can be blocked by landslides or snow, so check the latest update, avoid night driving, and hire local jeeps for the steep tracks.",
        "food": "Try fresh trout, karahi and barbecue in Naran bazaar, and hot tea by the lake.",
        "reach": "About 6-8 hours by road from Islamabad via Abbottabad, Mansehra and Balakot.",
        "tags": ["mountain", "family", "lakes", "honeymoon", "nature"],
    },
    "fairy meadows": {
        "names": ["fairy meadows", "fairy meadow", "nanga parbat", "raikot", "beyal", "tato"],
        "title": "Fairy Meadows and Nanga Parbat viewpoint",
        "highlights": ["Close views of Nanga Parbat", "Beyal Camp (about 1 hour further)", "Camping and stargazing",
                       "Raikot Bridge jeep ride"],
        "months": [5, 6, 7, 8, 9],
        "season": "May to September. In winter the area is snowbound and mostly closed.",
        "budget": "roughly PKR 12,000-30,000 per person for a 2-day trip including jeep, horse or porter, and a basic hut or camp.",
        "pack": "warm sleeping layers, rain jacket, trekking shoes, torch, snacks, a small bag (porters are available).",
        "safety": "The route has a narrow cliffside jeep track followed by a trek of about 3-4 hours, so it suits fit families but is hard for very young children or elderly relatives (horses are available). Use experienced local drivers, avoid travelling in rain, and check current conditions before going.",
        "food": "Basic dal, rice, eggs and tea at the huts; carry snacks.",
        "reach": "Drive the Karakoram Highway to Raikot Bridge, take a jeep to Tato village, then trek or ride about 3-4 hours.",
        "tags": ["mountain", "adventure", "trekking", "camping", "photography"],
    },
    "neelum": {
        "names": ["neelum", "keran", "sharda", "arang kel", "ratti gali", "muzaffarabad", "azad kashmir", "ajk"],
        "title": "Neelum Valley (Azad Kashmir)",
        "highlights": ["Keran and Sharda along the river", "Arang Kel (chairlift and short hike)", "Ratti Gali Lake (seasonal)",
                       "Kutton waterfalls and Neelum river viewpoints"],
        "months": [5, 6, 7, 8, 9, 10],
        "season": "May to October. Higher areas such as Ratti Gali are snowbound until about June.",
        "budget": "roughly PKR 7,000-18,000 per person per day.",
        "pack": "light layers, rain jacket, comfortable shoes, CNIC (needed for checkposts).",
        "safety": "Popular and generally fine for tourists, but road conditions vary and areas close to the Line of Control can have restrictions. Carry your CNIC, check the latest local advice and avoid night driving.",
        "food": "Fresh trout, kashmiri chai and local walnuts.",
        "reach": "About 5-6 hours from Islamabad to Muzaffarabad, then 5-7 hours up the valley to Sharda/Arang Kel.",
        "tags": ["mountain", "nature", "family", "honeymoon", "photography"],
    },
    "chitral": {
        "names": ["chitral", "kalash", "kalasha", "bumburet", "rumbur", "birir", "shandur", "garam chashma"],
        "title": "Chitral and the Kalash Valleys",
        "highlights": ["Kalash valleys (Bumburet, Rumbur, Birir)", "Chitral Fort and Shahi Mosque", "Shandur Polo Festival (usually early July)",
                       "Garam Chashma hot springs"],
        "months": [4, 5, 6, 7, 8, 9, 10],
        "season": "April to October. Kalash festivals: Chilimjusht (mid-May), Uchau (late August), Chaumos (December).",
        "budget": "roughly PKR 8,000-20,000 per person per day.",
        "pack": "layers, modest clothing (respect local customs, ask before photographing people), sun protection, cash.",
        "safety": "Generally peaceful. The Lowari Tunnel road is long, so check conditions and keep spare days.",
        "food": "Try Chitrali Shapik, Pulao and walnut bread.",
        "reach": "Drive from Peshawar or Islamabad through Dir and the Lowari Tunnel (about 9-11 hours), or fly Islamabad-Chitral on clear days.",
        "tags": ["culture", "mountain", "festival", "adventure"],
    },
    "kumrat": {
        "names": ["kumrat", "jahaz banda", "upper dir"],
        "title": "Kumrat Valley (Upper Dir)",
        "highlights": ["Deodar forests and the Panjkora river", "Jahaz Banda meadow trek", "Camping near Kumrat bazaar",
                       "Kumrat waterfall"],
        "months": [5, 6, 7, 8, 9, 10],
        "season": "May to October. Winter brings heavy snow and few services.",
        "budget": "roughly PKR 6,000-15,000 per person per day, with camping being the cheapest option.",
        "pack": "warm clothes for cold nights, rain jacket, sturdy shoes, a power bank (electricity is limited).",
        "safety": "Popular with young groups and families, but the final road is rough. Check weather and go with a reliable driver; avoid river crossings after rain.",
        "food": "Simple local food: trout, dal, rice, tea.",
        "reach": "Roughly 8-9 hours by road from Islamabad via the Motorway, Swat Expressway/Timergara and Dir.",
        "tags": ["nature", "camping", "adventure", "budget"],
    },
    "lahore": {
        "names": ["lahore", "badshahi", "lahore fort", "shalimar", "wazir khan", "walled city", "food street", "anarkali", "gawalmandi"],
        "title": "Lahore (Punjab)",
        "highlights": ["Badshahi Mosque and Lahore Fort", "Walled City and Wazir Khan Mosque", "Shalimar Gardens",
                       "Food Street near Fort Road at night", "Anarkali Bazaar and Liberty Market"],
        "months": [10, 11, 12, 1, 2, 3],
        "season": "October to March is the best time, with pleasant weather. Summers (May-August) are very hot.",
        "budget": "roughly PKR 6,000-18,000 per person per day, with street food very affordable.",
        "pack": "light cotton in summer, a light jacket in winter, comfortable shoes, and modest clothing for mosques.",
        "safety": "A large, busy city that is generally fine for tourists; use ride-hailing apps, keep valuables safe in crowded bazaars, and expect heavy traffic.",
        "food": "Try Siri Paye and Halwa Puri breakfast in Gawalmandi, Lahori chargha, Butt Karahi, chana chaat, lassi and kulfi.",
        "reach": "Allama Iqbal International Airport, the motorway from Islamabad (about 4-5 hours) or train services.",
        "tags": ["culture", "food", "history", "family", "city"],
    },
    "islamabad": {
        "names": ["islamabad", "faisal mosque", "daman e koh", "daman-e-koh", "margalla", "saidpur", "rawal lake", "pir sohawa", "monal", "rawalpindi"],
        "title": "Islamabad and Rawalpindi",
        "highlights": ["Faisal Mosque", "Daman-e-Koh and Margalla Hills trails", "Pakistan Monument and Museum",
                       "Saidpur Village", "Rawal Lake and Lok Virsa"],
        "months": [9, 10, 11, 12, 1, 2, 3, 4],
        "season": "September to April for pleasant weather; summers are hot but the Margalla Hills are cooler.",
        "budget": "roughly PKR 7,000-20,000 per person per day.",
        "pack": "comfortable shoes for trails and a light jacket in winter.",
        "safety": "One of the calmest and best-organised cities for visitors. Margalla trails are best used in daylight and in groups.",
        "food": "Try the Monal restaurant view, Saidpur Village cafes, and chapli kebab and street food in Rawalpindi's Raja Bazaar.",
        "reach": "Islamabad International Airport; a good base for trips north.",
        "tags": ["city", "family", "nature", "food"],
    },
    "karachi": {
        "names": ["karachi", "clifton", "mohatta", "hawksbay", "paradise point", "port grand", "burns road", "french beach"],
        "title": "Karachi (Sindh)",
        "highlights": ["Clifton Beach and Do Darya", "Mohatta Palace and Quaid's Mausoleum", "Port Grand and Frere Hall",
                       "Burns Road food street", "Hawksbay and Paradise Point"],
        "months": [11, 12, 1, 2, 3],
        "season": "November to February for cooler, drier weather.",
        "budget": "roughly PKR 7,000-20,000 per person per day.",
        "pack": "light clothing, sunscreen, comfortable shoes and a hat for the beach.",
        "safety": "A large, busy city. Use ride-hailing apps, avoid isolated beaches after dark, keep valuables hidden, and don't swim where there are rip-current warnings.",
        "food": "Try Burns Road nihari and haleem, bun kebab, biryani and seafood at Do Darya.",
        "reach": "Jinnah International Airport; trains and long-distance buses from the rest of Pakistan.",
        "tags": ["city", "beach", "food", "culture"],
    },
    "gwadar": {
        "names": ["gwadar", "hingol", "kund malir", "ormara", "makran", "balochistan", "princess of hope", "sonmiani"],
        "title": "Makran Coast (Gwadar, Hingol, Kund Malir)",
        "highlights": ["Kund Malir beach", "Hingol National Park and Princess of Hope rock", "Gwadar Hammerhead and Marine Drive",
                       "Makran Coastal Highway scenery"],
        "months": [10, 11, 12, 1, 2, 3],
        "season": "October to March; summers are extremely hot.",
        "budget": "mostly transport, roughly PKR 10,000-30,000 per person per day for a road trip with a hired vehicle.",
        "pack": "sun protection, plenty of drinking water, snacks and fuel; there are few services along the road.",
        "safety": "Security conditions can change, so check the latest travel advice before going, travel in groups, avoid night driving and register your route where required.",
        "food": "Fresh fish and local Balochi sajji.",
        "reach": "By road along the Makran Coastal Highway from Karachi (about 8-9 hours to Gwadar) or by air to Gwadar.",
        "tags": ["beach", "adventure", "road trip", "nature"],
    },
    "mohenjo daro": {
        "names": ["mohenjo daro", "mohenjodaro", "mohenjo-daro", "larkana", "indus civilization", "indus civilisation"],
        "title": "Mohenjo-daro (Sindh)",
        "highlights": ["Ancient Indus Valley city around 4,500 years old (UNESCO World Heritage Site)", "The Great Bath", "Site museum",
                       "Nearby Larkana and Keenjhar areas"],
        "months": [11, 12, 1, 2, 3],
        "season": "November to February; summers are extremely hot.",
        "budget": "a low-cost day trip, roughly PKR 5,000-12,000 per person plus transport.",
        "pack": "hat, sunscreen, water and comfortable shoes (there is very little shade).",
        "safety": "Check local conditions and travel by daytime.",
        "food": "Local Sindhi dishes in Larkana such as Sindhi biryani and sai bhaji.",
        "reach": "Fly or take a train to Sukkur/Larkana, then drive about 1-1.5 hours.",
        "tags": ["history", "culture"],
    },
    "taxila": {
        "names": ["taxila", "rohtas", "rohtas fort", "derawar", "derawar fort", "bahawalpur", "cholistan"],
        "title": "Heritage forts and ruins (Taxila, Rohtas, Derawar)",
        "highlights": ["Taxila's ancient Buddhist sites (UNESCO) near Islamabad", "Rohtas Fort near Jhelum (UNESCO)",
                       "Derawar Fort in the Cholistan desert near Bahawalpur"],
        "months": [10, 11, 12, 1, 2, 3],
        "season": "October to March.",
        "budget": "low cost; day trips from Islamabad or Lahore are roughly PKR 4,000-12,000 per person.",
        "pack": "hat, water and sturdy shoes.",
        "safety": "Easy and generally safe; carry water and avoid the heat of midday in summer.",
        "food": "Local dhaba food on the Grand Trunk Road.",
        "reach": "Taxila is about 45 minutes from Islamabad; Rohtas about 2.5 hours; Derawar is a long drive from Bahawalpur, best with a 4x4 guide.",
        "tags": ["history", "culture", "family", "budget"],
    },
    "peshawar": {
        "names": ["peshawar", "qissa khwani", "bala hisar", "namak mandi", "khyber pass", "khyber", "landi kotal"],
        "title": "Peshawar (Khyber Pakhtunkhwa)",
        "highlights": ["Qissa Khwani Bazaar", "Mahabat Khan Mosque", "Bala Hisar Fort", "Peshawar Museum", "Khyber Pass (viewpoint visits only)"],
        "months": [10, 11, 12, 1, 2, 3],
        "season": "October to March.",
        "budget": "roughly PKR 6,000-15,000 per person per day.",
        "pack": "modest clothing and comfortable shoes for the old city.",
        "safety": "Check current local advice; visit the old city and Khyber area by daylight and preferably with a local guide.",
        "food": "Try Namak Mandi chapli kebab and charsi tikka, kahwa tea and fresh naan.",
        "reach": "About 2 hours by motorway from Islamabad.",
        "tags": ["food", "history", "culture", "city"],
    },
    "multan": {
        "names": ["multan", "sohan halwa"],
        "title": "Multan (Punjab)",
        "highlights": ["Shrines of Shah Rukn-e-Alam and Bahauddin Zakariya", "Blue-tiled Sufi architecture",
                       "Ghanta Ghar and Hussain Agahi Bazaar", "Multani blue pottery"],
        "months": [10, 11, 12, 1, 2, 3],
        "season": "October to March; summers are among the hottest in Pakistan.",
        "budget": "roughly PKR 5,000-12,000 per person per day.",
        "pack": "modest clothing for shrines, hat and water.",
        "safety": "Generally fine for tourists; keep valuables safe in crowded bazaars.",
        "food": "Sohan halwa, Multani sohan halwa, sindhi biryani and mango varieties in summer.",
        "reach": "Fly, train or motorway from Lahore (about 4-5 hours).",
        "tags": ["culture", "history", "food"],
    },
    "ziarat": {
        "names": ["ziarat", "quetta", "harnai"],
        "title": "Ziarat and Quetta (Balochistan)",
        "highlights": ["Ziarat juniper forest (one of the world's oldest)", "Quaid-e-Azam Residency", "Hanna Lake near Quetta",
                       "Quetta bazaars and fruit"],
        "months": [4, 5, 6, 7, 8, 9, 10],
        "season": "April to October; winters are cold with snow.",
        "budget": "roughly PKR 8,000-20,000 per person per day.",
        "pack": "warm layers for cool evenings.",
        "safety": "Security conditions vary, so check the latest travel advice and use trusted drivers or tours.",
        "food": "Quetta's famous Sajji, Kabuli pulao and dried fruits.",
        "reach": "Fly to Quetta, then about 3 hours by road to Ziarat.",
        "tags": ["nature", "culture", "history"],
    },
}

# kinds of places for generic questions
SEASON_WORDS = {
    "summer": [5, 6, 7, 8], "spring": [3, 4, 5], "autumn": [9, 10, 11], "fall": [9, 10, 11], "winter": [12, 1, 2],
    "monsoon": [7, 8],
}
MONTHS = {m: i + 1 for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"])}

INTENTS = [
    ("season", r"best time|when (to|should)|which month|season|weather|climate|best month"),
    ("budget", r"budget|cost|price|cheap|expens|how much|afford|per person|money|spend"),
    ("pack", r"pack|bring|wear|carry|clothes|clothing|luggage|take with"),
    ("safety", r"safe|safety|secur|danger|risk|kids|child|family|families|solo|women|woman|female"),
    ("food", r"food|eat|restaurant|cuisine|dish|dishes|snack|breakfast|dinner|lunch"),
    ("reach", r"reach|how to get|get to|route|transport|travel to|bus|train|flight|fly|drive|distance|road"),
    ("highlights", r"things to do|to see|to visit|visit|places|attraction|sights|see in|do in|itinerary|plan|trip|tour|days?"),
]


def _norm(t):
    return re.sub(r"[^a-z0-9 ]+", " ", (t or "").lower()).strip()


def find_places(text):
    t = " " + _norm(text) + " "
    found = []
    for key, p in PLACES.items():
        # longer names first so 'saif ul malook' wins over 'kel'
        for n in sorted(p["names"], key=len, reverse=True):
            if " " + _norm(n) + " " in t:
                found.append(key)
                break
    return found


def _days(text):
    m = re.search(r"(\d{1,2})\s*(?:-|\s)?\s*(?:day|days|din)", text.lower())
    if m:
        return max(1, min(int(m.group(1)), 10))
    return None


def _bullets(items):
    return "\n".join("• " + i for i in items)


def _itinerary(p, days):
    h = p["highlights"]
    per = max(1, -(-len(h) // days))
    lines = []
    for d in range(days):
        chunk = h[d * per:(d + 1) * per]
        if not chunk:
            chunk = ["Free day: relax, shop for local crafts, or revisit your favourite spot"] if d else h[:1]
        lines.append(f"Day {d + 1}: " + "; ".join(chunk))
    return "\n".join(lines)


def answer_place(key, text):
    p = PLACES[key]
    lt = text.lower()
    intents = [name for name, rx in INTENTS if re.search(rx, lt)]
    days = _days(text)
    parts = []
    if days and "highlights" not in intents:
        intents.insert(0, "highlights")
    if not intents:
        intents = ["highlights", "season", "budget"]
    for it in intents[:3]:
        if it == "season":
            parts.append("Best time to visit: " + p["season"])
        elif it == "budget":
            parts.append("Budget: " + p["budget"] + " These are rough guides and prices change, so confirm before booking.")
        elif it == "pack":
            parts.append("What to pack: " + p["pack"])
        elif it == "safety":
            parts.append("Safety and families: " + p["safety"])
        elif it == "food":
            parts.append("Food: " + p["food"])
        elif it == "reach":
            parts.append("Getting there: " + p["reach"])
        elif it == "highlights":
            if days:
                parts.append(f"Suggested {days}-day plan:\n" + _itinerary(p, days))
            else:
                parts.append("Top things to do:\n" + _bullets(p["highlights"]))
    head = p["title"]
    tail = ""
    if len(intents) == 1 and intents[0] != "season":
        tail = "\n\nBest time: " + p["season"].split(".")[0] + "."
    return head + "\n\n" + "\n\n".join(parts) + tail


def recommend(text):
    lt = text.lower()
    months = None
    for w, ms in SEASON_WORDS.items():
        if re.search(r"\b" + w + r"\b", lt):
            months = ms
            label = w
            break
    for name, num in MONTHS.items():
        if re.search(r"\b" + name + r"\b", lt):
            months = [num]
            label = name.capitalize()
            break
    wanted_tags = [t for t in ("family", "honeymoon", "adventure", "budget", "beach", "snow", "history", "food", "trekking", "camping", "culture", "lakes", "mountain", "photography")
                   if re.search(r"\b" + t + r"\b", lt) or (t == "lakes" and "lake" in lt) or (t == "history" and "historic" in lt)]
    if not months and not wanted_tags:
        return None
    scored = []
    order = {k: i for i, k in enumerate(PLACES)}
    for key, p in PLACES.items():
        s = 0
        if months and any(m in p["months"] for m in months):
            s += 2
            if len(months) == 1 and months[0] in p["months"]:
                s += 1
        elif months:
            continue
        s += sum(2 for t in wanted_tags if t in p["tags"])
        if wanted_tags and not any(t in p["tags"] for t in wanted_tags):
            continue
        scored.append((s, key))
    if not scored:
        return None
    scored.sort(key=lambda x: (-x[0], order[x[1]]))
    picks = [k for _, k in scored[:5]]
    why = []
    if months:
        why.append(label.lower() if label.islower() else label)
    if wanted_tags:
        why.append(", ".join(wanted_tags))
    lines = [f"• {PLACES[k]['title']}: {PLACES[k]['highlights'][0]}" for k in picks]
    return ("Good picks for " + " / ".join(why) + ":\n" + "\n".join(lines) +
            "\n\nAsk me about any of them (for example: \"best time to visit " + PLACES[picks[0]]["names"][0].title() +
            "\" or \"3 day plan for " + PLACES[picks[0]]["names"][0].title() + "\").")


GREETING = r"^(hi|hello|hey|salam|assalam|assalamualaikum|aoa|good (morning|afternoon|evening))\b"
THANKS = r"\b(thanks|thank you|shukriya|jazakallah)\b"


def intro():
    names = ", ".join(p["title"].split(" (")[0] for p in list(PLACES.values())[:10])
    return ("I'm Wander Hub AI, your Pakistan travel helper. I can help with when to visit, rough budgets, what to pack, "
            "safety, food, how to get there and day-by-day plans for places like " + names + " and more.\n\n"
            "Try: \"3 day plan for Hunza\", \"best time to visit Skardu\", \"budget for Murree weekend\", or \"best places in summer\". "
            "I can also check \"weather in Lahore\" or \"convert 100 usd to pkr\".")


def answer(text):
    """Return an answer string, or None if the question is not covered."""
    t = (text or "").strip()
    if not t:
        return None
    lt = t.lower()
    places = find_places(t)
    if places:
        if len(places) == 1:
            return answer_place(places[0], t)
        # more than one place: short comparison of the first two
        a, b = places[0], places[1]
        sa, sb = PLACES[a], PLACES[b]
        return (f"{sa['title']} vs {sb['title']}\n\n"
                f"Best time:\n• {sa['title'].split(' (')[0]}: {sa['season'].split('.')[0]}.\n• {sb['title'].split(' (')[0]}: {sb['season'].split('.')[0]}.\n\n"
                f"Budget:\n• {sa['title'].split(' (')[0]}: {sa['budget'].split(' (')[0]}\n• {sb['title'].split(' (')[0]}: {sb['budget'].split(' (')[0]}\n\n"
                "Ask about either one for a full plan.")
    rec = recommend(t)
    if rec:
        return rec
    if re.search(GREETING, lt):
        return "Hello! " + intro()
    if re.search(THANKS, lt):
        return "You're welcome! Ask me anything else about your trip."
    if re.search(r"\b(what can you do|help|who are you|about you)\b", lt):
        return intro()
    return None
