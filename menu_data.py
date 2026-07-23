# menu_data.py
MENU = {
    "Kopi": [
        {"nama": "Espresso",      "deskripsi": "Shot espresso murni, bold dan intens dari biji arabika pilihan.", "harga": 22000, "badge": None, "gambar" : "assets/espresso.jfif"},
        {"nama": "Americano",     "deskripsi": "Espresso dengan hot water, rasa bersih dan ringan.",              "harga": 25000, "badge": None, "gambar" : "assets/Americano.jfif"},
        {"nama": "Cappuccino",    "deskripsi": "Espresso, steamed milk, dan milk foam tebal yang lembut.",        "harga": 32000, "badge": None, "gambar" : "assets/Cappuccino.jfif"},
        {"nama": "Caramel Latte", "deskripsi": "Latte manis dengan drizzle karamel buatan sendiri.",             "harga": 38000, "badge": "new", "gambar" : "assets/Caramel_latte.jfif"},
        {"nama": "V60 Pour Over", "deskripsi": "Manual brew V60, menonjolkan karakter biji single origin.",      "harga": 42000, "badge": None, "gambar" : "assets/V60_pour_over.jfif"},
        {"nama": "Cold Brew",     "deskripsi": "Diseduh dingin 12 jam, smooth dan rendah asam.",                 "harga": 38000, "badge": "new", "gambar" : "assets/Cold_Brew.jfif"},
    ],
    "Non-Kopi": [
        {"nama": "Matcha Latte",       "deskripsi": "Matcha ceremonial dengan steamed oat milk.",        "harga": 38000, "badge": "new", "gambar" : "assets/Matcha_Latte.jfif"},
        {"nama": "Taro Latte",         "deskripsi": "Susu talas ungu, creamy dan manis alami.",          "harga": 35000, "badge": "new", "gambar" : "assets/taro_latte.jfif"},
        {"nama": "Chocolate Hazelnut", "deskripsi": "Coklat belgia dengan hazelnut syrup.",              "harga": 36000, "badge": None, "gambar" : "assets/Chocolate_Hazelnut.jfif"},
        {"nama": "Strawberry Fizz",    "deskripsi": "Soda segar dengan strawberry puree dan hint mint.", "harga": 30000, "badge": None, "gambar" : "assets/Strawberry_Soda.jfif"},
        {"nama": "Pandan Coconut",     "deskripsi": "Pandan segar dengan santan dan gula aren.",         "harga": 28000, "badge": "best", "gambar" : "assets/Pandan_Coconut.jfif"},
    ],
    "Makanan": [
        {"nama": "Croissant Butter", "deskripsi": "Croissant laminasi 27 layer, renyah di luar lembut di dalam.", "harga": 32000, "badge": "hot", "gambar" : "assets/Croissants_butter.jfif"},
        {"nama": "Avocado Toast",    "deskripsi": "Sourdough dengan alpukat, telur poach, dan chili flakes.",     "harga": 55000, "badge": None, "gambar" : "assets/avocado_toast.jfif"},
        {"nama": "French Toast",     "deskripsi": "Brioche tebal dengan maple syrup dan berry segar.",            "harga": 50000, "badge": "new", "gambar" : "assets/French_Toast.jfif"},
        {"nama": "Chicken Panini",   "deskripsi": "Ayam panggang, mozarella, pesto, dan sundried tomato.",        "harga": 58000, "badge": None, "gambar" : "assets/Chicken_Panini.jfif"},
        {"nama": "Granola Bowl",     "deskripsi": "Yogurt greek dengan granola homemade dan seasonal fruit.",     "harga": 45000, "badge": "new", "gambar" : "assets/granola_bowl.jfif"},
    ],
    "Dessert": [
        {"nama": "Tiramisu",      "deskripsi": "Klasik Italia dengan mascarpone, espresso, dan cocoa.",  "harga": 48000, "badge": None, "gambar" : "assets/Tiramisu.jfif"},
        {"nama": "Cheesecake NY", "deskripsi": "Creamy NY style cheesecake dengan blueberry compote.",  "harga": 45000, "badge": None, "gambar" : "assets/Cheesecake_ny.jfif"},
        {"nama": "Lava Cake",     "deskripsi": "Molten chocolate cake dengan vanilla ice cream.",        "harga": 52000, "badge": None, "gambar" : "assets/Lava_Cake.jfif"},
        {"nama": "Klepon Cake",   "deskripsi": "Pandan cake isi gula aren, topping kelapa parut.",      "harga": 42000, "badge": "new", "gambar" : "assets/Klepon_cake.jfif"},
    ],
}

BADGE_MAP = {
    "best": ("Best Seller", "badge-best"),
    "hot":  ("Terlaris",    "badge-hot"),
    "new":  ("Baru",        "badge-new"),
}