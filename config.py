OLLAMA_BASE_URL = "http://localhost:11434"
LLM_MODEL = "llama3.2"
EMBED_MODEL = "nomic-embed-text"

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "stardew_wiki"

WIKI_BASE = "https://stardewvalleywiki.com"

# Páginas prioritárias para scraping
WIKI_PAGES = [
    # Bundles / Community Center
    "/Bundles",
    "/Community_Center",

    # Crops por estação
    "/Crops",
    "/Spring_Seeds", "/Summer_Seeds", "/Fall_Seeds",

    # Crops individuais mais importantes
    "/Strawberry", "/Blueberry", "/Starfruit", "/Cranberries", "/Ancient_Fruit",
    "/Pumpkin", "/Corn", "/Sunflower", "/Coffee_Bean", "/Hops",

    # Animais e produtos
    "/Animals", "/Artisan_Goods", "/Animal_Products_Profitability",

    # Pesca
    "/Fish", "/Fishing",

    # Mineração
    "/Mining", "/Minerals", "/Gems",

    # NPCs
    "/Villagers", "/Penny", "/Abigail", "/Emily", "/Leah", "/Maru", "/Haley",
    "/Alex", "/Elliott", "/Harvey", "/Sam", "/Sebastian", "/Shane",
    "/Gus", "/Willy", "/Clint", "/Robin", "/Pierre", "/Marnie",
    "/Linus", "/Wizard", "/Evelyn", "/George", "/Jodi", "/Kent",
    "/Demetrius", "/Caroline", "/Lewis", "/Pam", "/Sandy",

    # Calendário e eventos
    "/Calendar", "/Festivals", "/Spring", "/Summer", "/Fall", "/Winter",

    # Skills e mecânicas
    "/Skills", "/Farming", "/Foraging", "/Combat",
    "/Professions",

    # Construções
    "/Buildings", "/Greenhouse", "/Shed",

    # Outros
    "/Gold", "/Energy", "/Friendship", "/Quests",
    "/Secret_Notes", "/Junimo_Kart",
]
