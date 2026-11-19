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
CATEGORIES = ["Breakfast", "Lunch", "Dinner", "Drinks & Desserts"]

CATEGORY_LANES = {
    "Breakfast": "morning-kitchen",
    "Lunch": "hot-kitchen",
    "Dinner": "grill-station",
    "Drinks & Desserts": "kakanin-counter",
}

# Aklanon food photography is sourced from Wikimedia Commons; see static/img/CREDITS.md.
MENU_SEED: list[dict] = [
    {
        "name": "Inubaran nga Manok",
        "category": "Lunch",
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
        "category": "Dinner",
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
        "category": "Lunch",
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
        "category": "Lunch",
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
        "category": "Dinner",
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
        "category": "Drinks & Desserts",
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
        "category": "Drinks & Desserts",
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
        "category": "Drinks & Desserts",
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
        "category": "Drinks & Desserts",
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
        "category": "Drinks & Desserts",
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
        "category": "Drinks & Desserts",
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
        "category": "Drinks & Desserts",
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
        "category": "Drinks & Desserts",
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
    {
        "name": "Pandesal at Sikwate",
        "category": "Breakfast",
        "description": (
            "Warm pan de sal straight from the oven with a cup of thick native "
            "chocolate — the classic Filipino morning pair."
        ),
        "price_php": 95.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/pandesal.jpg",
        "ingredients": "Wheat flour, yeast, salt, sugar, native cacao, milk, water",
        "cooking_notes": "Bake the pandesal until the crust crackles, then serve with sikwate whisked from pure cacao tablets.",
        "allergens": "Gluten (wheat); milk",
        "prep_minutes": 15,
        "stock_qty": 40,
        "is_signature": 0,
    },
    {
        "name": "Arroz Caldo",
        "category": "Breakfast",
        "description": (
            "Creamy ginger rice porridge with native chicken, kasubha, and a "
            "squeeze of calamansi on top."
        ),
        "price_php": 145.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/arroz-caldo.jpg",
        "ingredients": "Glutinous rice, native chicken, ginger, garlic, onion, kasubha, patis, calamansi",
        "cooking_notes": "Sauté ginger and garlic first, then simmer the rice with chicken stock until the grains bloom.",
        "allergens": "Fish (patis)",
        "prep_minutes": 30,
        "stock_qty": 22,
        "is_signature": 0,
    },
    {
        "name": "Chicken Adobo",
        "category": "Lunch",
        "description": (
            "Native chicken braised in soy, cane vinegar, garlic, and bay leaf — "
            "the national classic, cooked the slow way."
        ),
        "price_php": 265.0,
        "municipality": "Banga",
        "image_url": "/static/img/chicken-adobo.jpg",
        "ingredients": "Native chicken, cane vinegar, soy sauce, garlic, onion, bay leaf, peppercorn",
        "cooking_notes": "Brown the chicken, add vinegar without stirring, then reduce with soy and garlic until glossy.",
        "allergens": "Soy; gluten (soy sauce)",
        "prep_minutes": 35,
        "stock_qty": 20,
        "is_signature": 1,
    },
    {
        "name": "Sinigang na Hipon",
        "category": "Lunch",
        "description": (
            "Tamarind-soured broth with fresh shrimp, kangkong, radish, and long "
            "chili — bright, tangy, and comforting."
        ),
        "price_php": 295.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/sinigang-na-hipon.jpg",
        "ingredients": "Fresh shrimp, tamarind, kangkong, radish, tomato, onion, long chili, patis",
        "cooking_notes": "Simmer the tamarind first and strain, then add vegetables and shrimp last so they stay sweet.",
        "allergens": "Crustacean shellfish; fish (patis)",
        "prep_minutes": 30,
        "stock_qty": 16,
        "is_signature": 0,
    },
    {
        "name": "Crispy Pata",
        "category": "Dinner",
        "description": (
            "Deep-fried pork leg with shatter-crisp skin and tender meat, served "
            "with a soy-vinegar dipping sauce."
        ),
        "price_php": 420.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/crispy-pata.jpg",
        "ingredients": "Pork leg, garlic, bay leaf, peppercorn, salt, cane vinegar, soy sauce",
        "cooking_notes": "Boil until fork-tender, dry the skin completely, then fry hot until it blisters.",
        "allergens": "Pork; soy",
        "prep_minutes": 60,
        "stock_qty": 8,
        "is_signature": 1,
    },
    {
        "name": "Halo-Halo",
        "category": "Drinks & Desserts",
        "description": (
            "Shaved ice layered with sweet beans, nata, leche flan, and ube "
            "halaya, finished with evaporated milk."
        ),
        "price_php": 135.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/halo-halo.jpg",
        "ingredients": "Shaved ice, sweet red beans, nata de coco, saba banana, ube halaya, leche flan, evaporated milk",
        "cooking_notes": "Layer the sweets in a tall glass, pack shaved ice on top, and pour milk just before serving.",
        "allergens": "Milk; may contain nuts",
        "prep_minutes": 12,
        "stock_qty": 30,
        "is_signature": 1,
    },
    # ---------------------------------------------------------------- Breakfast
    {
        "name": "Tapsilog",
        "category": "Breakfast",
        "description": (
            "Cured beef tapa seared until the edges caramelise, served with "
            "garlic rice and a sunny egg — the everyday Filipino morning classic."
        ),
        "price_php": 165.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/tapsilog.jpg",
        "ingredients": "Beef, cane vinegar, soy sauce, garlic, brown sugar, rice, egg",
        "cooking_notes": "Marinate the beef overnight, pan-fry until sticky at the edges, and serve over garlic rice with a fried egg.",
        "allergens": "Soy; gluten (soy sauce); egg",
        "prep_minutes": 25,
        "stock_qty": 18,
        "is_signature": 1,
    },
    {
        "name": "Longsilog",
        "category": "Breakfast",
        "description": (
            "Native longganisa snapped from its casing and fried until glossy, "
            "paired with garlic rice and egg."
        ),
        "price_php": 155.0,
        "municipality": "Banga",
        "image_url": "/static/img/longsilog.jpg",
        "ingredients": "Pork, garlic, cane vinegar, soy sauce, brown sugar, native spices, rice, egg",
        "cooking_notes": "Prick the sausages before frying so they cook evenly, then rest them before plating with rice and egg.",
        "allergens": "Soy; gluten; egg",
        "prep_minutes": 20,
        "stock_qty": 20,
        "is_signature": 0,
    },
    {
        "name": "Bangsilog",
        "category": "Breakfast",
        "description": (
            "Butterflied milkfish fried until the skin crackles, with garlic "
            "rice, egg and a wedge of calamansi."
        ),
        "price_php": 185.0,
        "municipality": "Ibajay",
        "image_url": "/static/img/bangsilog.jpg",
        "ingredients": "Milkfish, garlic, soy sauce, cane vinegar, rice, egg, calamansi",
        "cooking_notes": "Score the fish so it fries evenly, then serve with garlic rice and a dip of soy and calamansi.",
        "allergens": "Fish; soy; egg",
        "prep_minutes": 25,
        "stock_qty": 14,
        "is_signature": 0,
    },
    {
        "name": "Tosilog",
        "category": "Breakfast",
        "description": (
            "Sweet-cured pork tocino with a lacquered crust, garlic rice, egg "
            "and a spoon of atchara."
        ),
        "price_php": 160.0,
        "municipality": "Numancia",
        "image_url": "/static/img/tosilog.jpg",
        "ingredients": "Pork belly, sugar, salt, annatto, garlic, rice, egg, atchara",
        "cooking_notes": "Fry the tocino in a little oil over low heat so the sugar glazes instead of burning.",
        "allergens": "Egg",
        "prep_minutes": 20,
        "stock_qty": 18,
        "is_signature": 0,
    },
    {
        "name": "Champorado",
        "category": "Breakfast",
        "description": (
            "Filipino chocolate rice porridge stirred from native cacao, rich "
            "and warm — good with a side of tuyo."
        ),
        "price_php": 110.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/champorado.jpg",
        "ingredients": "Glutinous rice, native cacao, milk, sugar, salted dried fish (tuyo)",
        "cooking_notes": "Simmer the rice until it bursts, then whisk in cacao and milk until glossy and thick.",
        "allergens": "Milk; fish (tuyo)",
        "prep_minutes": 25,
        "stock_qty": 24,
        "is_signature": 0,
    },
    {
        "name": "Tortang Talong",
        "category": "Breakfast",
        "description": (
            "Charred eggplant flattened into an egg omelette — smoky, soft "
            "and surprisingly filling."
        ),
        "price_php": 135.0,
        "municipality": "Malay",
        "image_url": "/static/img/tortang-talong.jpg",
        "ingredients": "Eggplant, egg, onion, garlic, salt, pepper",
        "cooking_notes": "Char the eggplant until the skin blisters, peel, flatten, then dip in beaten egg and pan-fry.",
        "allergens": "Egg",
        "prep_minutes": 20,
        "stock_qty": 16,
        "is_signature": 0,
    },
    {
        "name": "Tinapang Bangus",
        "category": "Breakfast",
        "description": (
            "Bamboo-smoked milkfish with a deep amber colour, served with "
            "garlic rice and egg."
        ),
        "price_php": 175.0,
        "municipality": "Ibajay",
        "image_url": "/static/img/tinapang-bangus.jpg",
        "ingredients": "Milkfish, bamboo smoke, salt, rice, egg, calamansi",
        "cooking_notes": "Smoke the fish slowly over bamboo until the flesh sets, then pan-fry briefly before serving.",
        "allergens": "Fish; egg",
        "prep_minutes": 20,
        "stock_qty": 12,
        "is_signature": 0,
    },
    {
        "name": "Bibingka",
        "category": "Breakfast",
        "description": (
            "Soft rice cake baked in a banana leaf, brushed with butter and "
            "topped with salted egg and cheese."
        ),
        "price_php": 125.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/bibingka.jpg",
        "ingredients": "Rice flour, coconut milk, egg, sugar, salted egg, cheese, banana leaf",
        "cooking_notes": "Line the pan with banana leaf, pour the batter, and bake until the top is set and lightly browned.",
        "allergens": "Egg; coconut; milk",
        "prep_minutes": 30,
        "stock_qty": 20,
        "is_signature": 0,
    },
    # ------------------------------------------------------------------- Lunch
    {
        "name": "Kare-Kare",
        "category": "Lunch",
        "description": (
            "Oxtail and vegetables in a velvety peanut sauce, served the "
            "proper way with bagoong."
        ),
        "price_php": 345.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/kare-kare.jpg",
        "ingredients": "Oxtail, ground peanuts, annatto, eggplant, sitaw, banana heart, bagoong",
        "cooking_notes": "Simmer the oxtail until tender, then finish with peanut sauce and vegetables; serve bagoong on the side.",
        "allergens": "Peanuts; crustacean/shrimp (bagoong)",
        "prep_minutes": 60,
        "stock_qty": 10,
        "is_signature": 1,
    },
    {
        "name": "Lechon Kawali",
        "category": "Lunch",
        "description": (
            "Pork belly boiled until tender then fried hard until the skin "
            "crackles, with lechon dipping sauce."
        ),
        "price_php": 295.0,
        "municipality": "Banga",
        "image_url": "/static/img/lechon-kawali.jpg",
        "ingredients": "Pork belly, garlic, bay leaf, peppercorn, salt, soy sauce, lechon sauce",
        "cooking_notes": "Boil, dry the skin completely, then fry in hot oil until it blisters and crackles.",
        "allergens": "Pork; soy; gluten",
        "prep_minutes": 45,
        "stock_qty": 14,
        "is_signature": 0,
    },
    {
        "name": "Pinakbet",
        "category": "Lunch",
        "description": (
            "Ilocano-style mixed vegetables simmered with shrimp bagoong — "
            "savoury, earthy and honest."
        ),
        "price_php": 215.0,
        "municipality": "Numancia",
        "image_url": "/static/img/pinakbet.jpg",
        "ingredients": "Squash, eggplant, okra, sitaw, tomato, onion, shrimp bagoong",
        "cooking_notes": "Sauté the bagoong first, add the harder vegetables, then finish with the softer ones.",
        "allergens": "Crustacean/shrimp (bagoong)",
        "prep_minutes": 25,
        "stock_qty": 18,
        "is_signature": 0,
    },
    {
        "name": "Sisig",
        "category": "Lunch",
        "description": (
            "Sizzling chopped pork with onion, chili and calamansi — loud, "
            "sharp and made for sharing."
        ),
        "price_php": 285.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/sisig.jpg",
        "ingredients": "Pork cheek, onion, garlic, chili, mayonnaise, calamansi, soy sauce",
        "cooking_notes": "Boil and grill the pork first for smokiness, then chop, season and serve on a hot plate.",
        "allergens": "Egg (mayonnaise); soy",
        "prep_minutes": 30,
        "stock_qty": 12,
        "is_signature": 1,
    },
    {
        "name": "Pancit Bihon",
        "category": "Lunch",
        "description": (
            "Fine rice noodles tossed with chicken, shrimp and garden "
            "vegetables — a fiesta-table staple."
        ),
        "price_php": 235.0,
        "municipality": "Malay",
        "image_url": "/static/img/pancit-bihon.jpg",
        "ingredients": "Rice noodles, chicken, shrimp, cabbage, carrot, onion, soy sauce, calamansi",
        "cooking_notes": "Soften the noodles first, then stir-fry with the aromatics and add stock so they finish silky.",
        "allergens": "Crustacean shellfish; soy; gluten",
        "prep_minutes": 30,
        "stock_qty": 20,
        "is_signature": 0,
    },
    # ------------------------------------------------------------------ Dinner
    {
        "name": "Chicken Inasal",
        "category": "Dinner",
        "description": (
            "Native chicken grilled over coals with annatto, lemongrass and "
            "garlic — smoky, juicy and golden."
        ),
        "price_php": 275.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/chicken-inasal.jpg",
        "ingredients": "Native chicken, annatto, lemongrass, garlic, cane vinegar, soy sauce, oil",
        "cooking_notes": "Marinate overnight, baste with annatto oil while grilling, and rest before carving.",
        "allergens": "Soy",
        "prep_minutes": 35,
        "stock_qty": 16,
        "is_signature": 1,
    },
    {
        "name": "Pork Barbecue",
        "category": "Dinner",
        "description": (
            "Pork skewers marinated in vinegar, soy and garlic, grilled until "
            "the edges char and caramelise."
        ),
        "price_php": 195.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/pork-barbecue.jpg",
        "ingredients": "Pork, cane vinegar, soy sauce, garlic, sugar, banana ketchup, bamboo skewers",
        "cooking_notes": "Marinate overnight and grill close to the coals, turning often and basting with the marinade.",
        "allergens": "Soy; gluten",
        "prep_minutes": 30,
        "stock_qty": 25,
        "is_signature": 0,
    },
    {
        "name": "Inihaw na Bangus",
        "category": "Dinner",
        "description": (
            "Whole milkfish stuffed with lemongrass and salt, grilled until "
            "the skin is smoky and crisp."
        ),
        "price_php": 265.0,
        "municipality": "Ibajay",
        "image_url": "/static/img/inihaw-na-bangus.jpg",
        "ingredients": "Milkfish, lemongrass, salt, tomato, onion, soy-vinegar dip",
        "cooking_notes": "Stuff the cavity with herbs, salt the skin, and grill over medium coals so it cooks through.",
        "allergens": "Fish; soy",
        "prep_minutes": 30,
        "stock_qty": 12,
        "is_signature": 0,
    },
    {
        "name": "Bulalo",
        "category": "Dinner",
        "description": (
            "Beef shank simmered for hours until the marrow is soft, with "
            "corn, cabbage and a clear, sweet broth."
        ),
        "price_php": 395.0,
        "municipality": "Numancia",
        "image_url": "/static/img/bulalo.jpg",
        "ingredients": "Beef shank, marrow, corn, cabbage, lemongrass, onion, peppercorn",
        "cooking_notes": "Skim the broth as it boils, then simmer low and slow until the shank gives way.",
        "allergens": "None",
        "prep_minutes": 90,
        "stock_qty": 8,
        "is_signature": 0,
    },
    {
        "name": "Sinigang na Baboy",
        "category": "Dinner",
        "description": (
            "Pork in tamarind broth with taro, radish and kangkong — sour, "
            "warm and deeply comforting."
        ),
        "price_php": 285.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/sinigang-na-baboy.jpg",
        "ingredients": "Pork belly, tamarind, taro, radish, kangkong, tomato, onion",
        "cooking_notes": "Simmer the pork first, add the tamarind and root vegetables, and finish with the greens.",
        "allergens": "None",
        "prep_minutes": 40,
        "stock_qty": 14,
        "is_signature": 0,
    },
    {
        "name": "Beef Nilaga",
        "category": "Dinner",
        "description": (
            "Clear beef broth with taro, chayote, cabbage and carrots; simply "
            "seasoned with peppercorn and onion."
        ),
        "price_php": 325.0,
        "municipality": "Banga",
        "image_url": "/static/img/beef-nilaga.jpg",
        "ingredients": "Beef, taro, chayote, cabbage, carrot, onion, peppercorn, salt",
        "cooking_notes": "Simmer the beef until tender, then add the vegetables in order of how long they take to cook.",
        "allergens": "None",
        "prep_minutes": 75,
        "stock_qty": 10,
        "is_signature": 0,
    },
    {
        "name": "Kansi",
        "category": "Dinner",
        "description": (
            "Western Visayas beef soup with shank, lemongrass and cane "
            "vinegar — sour, hearty and slow-cooked."
        ),
        "price_php": 365.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/kansi.jpg",
        "ingredients": "Beef shank, lemongrass, garlic, cane vinegar, sitaw, onion, peppercorn",
        "cooking_notes": "Brown the shank, then simmer low with lemongrass and vinegar until the meat is fork-tender.",
        "allergens": "None",
        "prep_minutes": 90,
        "stock_qty": 8,
        "is_signature": 1,
    },
    # ------------------------------------------------------- Drinks & Desserts
    {
        "name": "Buko Pandan",
        "category": "Drinks & Desserts",
        "description": (
            "Young coconut strips and pandan jelly folded into sweet cream — "
            "cool, fragrant and purely Pinoy."
        ),
        "price_php": 115.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/buko-pandan.jpg",
        "ingredients": "Young coconut, pandan jelly, cream, sugar, pandan extract",
        "cooking_notes": "Chill the coconut and jelly first, then fold together with sweetened cream just before serving.",
        "allergens": "Milk",
        "prep_minutes": 15,
        "stock_qty": 28,
        "is_signature": 0,
    },
    {
        "name": "Taho",
        "category": "Drinks & Desserts",
        "description": (
            "Silken tofu in warm arnibal syrup with sago pearls — the "
            "street-corner dessert many grew up with."
        ),
        "price_php": 85.0,
        "municipality": "Kalibo",
        "image_url": "/static/img/taho.jpg",
        "ingredients": "Silken tofu, cane syrup (arnibal), sago pearls, vanilla",
        "cooking_notes": "Warm the tofu gently, then ladle over syrup and pearls; never boil the tofu or it will break.",
        "allergens": "Soy",
        "prep_minutes": 10,
        "stock_qty": 30,
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
