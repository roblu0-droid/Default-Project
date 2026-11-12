"""Static catalog and delivery-zone configuration for Hatod Akean."""

from __future__ import annotations

DELIVERY_ZONES: dict[str, dict] = {
    "Kalibo": {
        "hub": "Kalibo Heritage Hub",
        "fee": 39.0,
        "eta": "25–35 min",
        "barangays": [
            "Poblacion", "Andagaw", "Bachao Norte", "Bachao Sur", "Buscay",
            "Estancia", "Linabuan Norte", "Linabuan Sur", "Mabilo", "Mobo",
            "Nalook", "New Buswang", "Old Buswang", "Pook", "Siniba-an",
            "Tigayon", "Tinigaw",
        ],
    },
    "Numancia": {
        "hub": "Kalibo Heritage Hub",
        "fee": 49.0,
        "eta": "30–40 min",
        "barangays": [
            "Poblacion", "Albasan", "Aliputos", "Badio", "Bubog", "Bulwang",
            "Camanci Norte", "Camanci Sur", "Joyao-Joyao", "Laguinbanua East",
            "Laguinbanua West", "Marianos", "Navitas", "Pusiw", "Tabangka",
        ],
    },
    "Banga": {
        "hub": "Kalibo Heritage Hub",
        "fee": 59.0,
        "eta": "35–45 min",
        "barangays": [
            "Poblacion", "Agbanawan", "Bacan", "Badiangan", "Cerrudo", "Cupang",
            "Daguitan", "Daja", "Caluya", "Mangalcal", "Mangga", "Polo",
            "Sigcay", "Taba-ao", "Tabayon",
        ],
    },
    "Ibajay": {
        "hub": "Northern Aklan Hub",
        "fee": 79.0,
        "eta": "45–60 min",
        "barangays": [
            "Poblacion", "Agbago", "Agdugayan", "Antipolo", "Aparicio", "Aquino",
            "Aslum", "Bagacay", "Batuan", "Buenavista", "Bugtongbato", "Cabugao",
            "Capilijan", "Colongcolong", "Laguinbanua", "Mabusao", "Malindog",
            "Maloco", "Mina-a", "Monlaque", "Naile", "Naisud", "Naligusan",
            "Ondoy", "Regador", "Rivera", "Rizal", "San Isidro", "San Jose",
            "Sta. Cruz", "Tagbaya", "Tul-ang", "Unat", "Yawan",
        ],
    },
    "Malay": {
        "hub": "Boracay & Malay Hub",
        "fee": 99.0,
        "eta": "50–70 min",
        "barangays": [
            "Poblacion", "Argao", "Balabag", "Balusbos", "Cabulihan",
            "Caticlan", "Cogon", "Cubay Norte", "Cubay Sur", "Dumlog",
            "Manoc-Manoc", "Motag", "Naasug", "Nabaoy", "Napaan", "Sambiray",
            "Yapak",
        ],
    },
}

MUNICIPALITIES = list(DELIVERY_ZONES.keys())
CATEGORIES = ["Main Dishes", "Native Delicacies", "Beverages"]

CATEGORY_LANES = {
    "Main Dishes": "hot-kitchen",
    "Native Delicacies": "kakanin-counter",
    "Beverages": "cellar",
}

# Aklanon food photography is sourced from Wikimedia Commons; see README credits.
MENU_SEED: list[dict] = [
    {
        "name": "Inubaran nga Manok",
        "category": "Main Dishes",
        "description": (
            "Native chicken slow-simmered with banana pith (ubad), lemongrass, "
            "and fresh coconut milk. A comforting Aklanon heirloom dish."
        ),
        "price_php": 285.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/ginataang-manok.jpg",
        "ingredients": "Native chicken, ubad (banana pith), coconut milk, lemongrass, ginger, garlic, onion, patis, black pepper",
        "cooking_notes": "Tenderise ubad first, then simmer with seared native chicken, gata, and lemongrass until the broth is silky.",
        "allergens": "Fish (patis); coconut",
        "prep_minutes": 35,
        "stock_qty": 18,
        "is_signature": 1,
    },
    {
        "name": "Binakoe nga Manok",
        "category": "Main Dishes",
        "description": (
            "Native chicken cooked in bamboo with lemongrass, ginger, and "
            "coconut water — smoky, herby, and deeply Aklanon."
        ),
        "price_php": 320.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/binakoe.jpg",
        "ingredients": "Native chicken, young coconut water, coconut meat, lemongrass, ginger, garlic, onion, chili leaves, salt",
        "cooking_notes": "Seal chicken and aromatics in a bamboo node and cook over open flame until the broth smells of lemongrass and smoke.",
        "allergens": "None declared; prepared in a kitchen that handles fish and shellfish",
        "prep_minutes": 45,
        "stock_qty": 14,
        "is_signature": 1,
    },
    {
        "name": "Linapay / Tinamuk",
        "category": "Main Dishes",
        "description": (
            "Freshwater shrimp pounded with coconut, ginger, and chili, wrapped "
            "in taro leaves and simmered in gata."
        ),
        "price_php": 245.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/laing.jpg",
        "ingredients": "Freshwater shrimp, grated coconut, taro leaves, coconut milk, ginger, garlic, shallots, chili",
        "cooking_notes": "Wrap the shrimp-coconut mixture in taro leaves; simmer gently in gata without stirring so the parcels hold.",
        "allergens": "Crustacean shellfish; coconut",
        "prep_minutes": 30,
        "stock_qty": 16,
        "is_signature": 1,
    },
    {
        "name": "Tinumis",
        "category": "Main Dishes",
        "description": (
            "Aklanon pork blood stew with native vinegar, garlic, and lemongrass "
            "— tangy, savory, and slow-cooked."
        ),
        "price_php": 230.0,
        "municipality": "Banga",
        "image_url": "/static/img/tinumis.jpg",
        "ingredients": "Pork, pork blood, native vinegar, garlic, onion, ginger, lemongrass, bay leaf, chili",
        "cooking_notes": "Cook the pork until tender, add blood and vinegar, then reduce slowly until glossy and deeply savoury.",
        "allergens": "Pork; sulfites may be present in vinegar",
        "prep_minutes": 40,
        "stock_qty": 20,
        "is_signature": 0,
    },
    {
        "name": "Lechon de Kalibo",
        "category": "Main Dishes",
        "description": (
            "Crispy local roast pork seasoned with lemongrass and Aklanon "
            "spices. Served with tangy liver sauce."
        ),
        "price_php": 650.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/lechon.jpg",
        "ingredients": "Native pork, lemongrass, garlic, calamansi, sea salt, black pepper, liver sauce",
        "cooking_notes": "Roast over charcoal until the skin is glass-crisp; rest for ten minutes before chopping.",
        "allergens": "Pork; liver sauce may contain dairy",
        "prep_minutes": 55,
        "stock_qty": 10,
        "is_signature": 1,
    },
    {
        "name": "Latik",
        "category": "Native Delicacies",
        "description": (
            "Chewy rice cake bathed in sweet coconut caramel and toasted latik "
            "curds."
        ),
        "price_php": 95.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/latik.jpg",
        "ingredients": "Glutinous rice, coconut milk, muscovado sugar, toasted coconut curds",
        "cooking_notes": "Steam the rice cake, then blanket with thick coconut caramel and latik.",
        "allergens": "Coconut",
        "prep_minutes": 20,
        "stock_qty": 30,
        "is_signature": 0,
    },
    {
        "name": "Inday-Inday",
        "category": "Native Delicacies",
        "description": (
            "Soft steamed glutinous rice rolls with coconut and muscovado — a "
            "market-day favorite."
        ),
        "price_php": 85.0,
        "municipality": "Banga",
        "image_url": "/static/img/kakanin.jpg",
        "ingredients": "Glutinous rice, coconut, muscovado sugar, banana leaf",
        "cooking_notes": "Steam until the rice is translucent and the coconut sugar has melted through.",
        "allergens": "Coconut",
        "prep_minutes": 20,
        "stock_qty": 28,
        "is_signature": 0,
    },
    {
        "name": "Alupi",
        "category": "Native Delicacies",
        "description": (
            "Cassava and coconut cake, steamed in banana leaf with a tender, "
            "fragrant crumb."
        ),
        "price_php": 90.0,
        "municipality": "Numancia",
        "image_url": "/static/img/puto.jpg",
        "ingredients": "Grated cassava, coconut milk, sugar, banana leaf, a pinch of salt",
        "cooking_notes": "Fold the cassava batter gently and steam until a skewer comes out clean.",
        "allergens": "Coconut",
        "prep_minutes": 25,
        "stock_qty": 24,
        "is_signature": 0,
    },
    {
        "name": "Ibos",
        "category": "Native Delicacies",
        "description": (
            "Sticky rice wrapped in young coconut leaves, gently sweetened with "
            "coconut sugar."
        ),
        "price_php": 75.0,
        "municipality": "Ibajay",
        "image_url": "/static/img/ibos.jpg",
        "ingredients": "Glutinous rice, coconut milk, coconut sugar, young coconut leaves",
        "cooking_notes": "Bundle the rice tightly, boil until set, and serve at room temperature.",
        "allergens": "Coconut",
        "prep_minutes": 30,
        "stock_qty": 26,
        "is_signature": 0,
    },
    {
        "name": "Baye-Baye",
        "category": "Native Delicacies",
        "description": (
            "Pounded young rice, corn, and coconut baked into a nutty, chewy "
            "heritage treat."
        ),
        "price_php": 110.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/suman-latik.jpg",
        "ingredients": "Young rice, sweet corn, coconut, muscovado sugar, banana leaf",
        "cooking_notes": "Pound the rice while warm, fold through corn and coconut, then bake until caramelised at the edges.",
        "allergens": "Coconut",
        "prep_minutes": 30,
        "stock_qty": 18,
        "is_signature": 0,
    },
    {
        "name": "Ampaw",
        "category": "Native Delicacies",
        "description": (
            "Airy puffed rice sweets glazed with muscovado — crisp, crackly, "
            "and nostalgic."
        ),
        "price_php": 65.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/ampaw.jpg",
        "ingredients": "Puffed rice, muscovado syrup, peanuts (optional), coconut oil",
        "cooking_notes": "Toss puffed rice in warm muscovado syrup and press into bars before it cools.",
        "allergens": "May contain peanuts",
        "prep_minutes": 10,
        "stock_qty": 40,
        "is_signature": 0,
    },
    {
        "name": "Tuba",
        "category": "Beverages",
        "description": (
            "Fresh coconut sap tapped at dawn — lightly sweet, tart, and best "
            "served chilled."
        ),
        "price_php": 120.0,
        "municipality": "Ibajay",
        "image_url": "/static/img/palm-wine.jpg",
        "ingredients": "Fresh coconut sap (tuba), a squeeze of calamansi",
        "cooking_notes": "Serve very cold. Best within the same day it is tapped.",
        "allergens": "Coconut",
        "prep_minutes": 5,
        "stock_qty": 12,
        "is_signature": 0,
    },
    {
        "name": "Bahalina",
        "category": "Beverages",
        "description": (
            "Aged coconut wine with deep amber notes of caramel and citrus. A "
            "true Aklanon pour."
        ),
        "price_php": 180.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/toddy.jpg",
        "ingredients": "Aged coconut sap wine, coconut bark tannin",
        "cooking_notes": "Pour gently and serve at cellar temperature. Contains alcohol.",
        "allergens": "Coconut; contains alcohol",
        "prep_minutes": 5,
        "stock_qty": 8,
        "is_signature": 0,
    },
]

VIDEOS = [
    {
        "title": "Rural cooking: Binakoe & Inubaran",
        "eyebrow": "From the bamboo fire",
        "description": "Follow Aklanon home cooks as native chicken, lemongrass, and coconut are transformed into Binakoe and Inubaran.",
        "youtube_id": "nzKirJj7fOo",
        "thumbnail": "/static/img/video-cooking.jpg",
    },
    {
        "title": "Kalibo Ati-Atihan Festival",
        "eyebrow": "The street is the stage",
        "description": "Drums, soot, feathers, and devotion — the Ati-Atihan energy that gives Hatod Akean its heartbeat.",
        "youtube_id": "RjAlHrpg-cs",
        "thumbnail": "/static/img/video-festival.jpg",
    },
    {
        "title": "Taste of Kalibo & beyond",
        "eyebrow": "Culinary heritage",
        "description": "A local food journey through Kalibo's markets and nearby towns, from kakanin to lechon.",
        "youtube_id": "YO5fl4Tpd0w",
        "thumbnail": "/static/img/video-kalibo.jpg",
    },
]
