"""Seed the database with initial hairstyle catalog data."""

from db.engine import get_session
from db.models import Hairstyle, HairstyleCategory


SEED_DATA = {
    "men": {
        "categories": [
            {"name": "Fades", "description": "Gradual taper from short to long"},
            {"name": "Classic Cuts", "description": "Timeless men's hairstyles"},
            {"name": "Modern Styles", "description": "Trendy contemporary looks"},
        ],
        "hairstyles": [
            {
                "name": "Classic Fade",
                "category": "Fades",
                "length": "short",
                "style_type": "fade",
                "sd_prompt": "short classic fade haircut, clean taper fade, natural hair texture, professional barbershop cut, photorealistic",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic, bad anatomy",
            },
            {
                "name": "High Skin Fade",
                "category": "Fades",
                "length": "short",
                "style_type": "fade",
                "sd_prompt": "high skin fade haircut, bald fade, sharp clean lines, modern barbershop, photorealistic hair",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic",
            },
            {
                "name": "Textured Crop",
                "category": "Modern Styles",
                "length": "short",
                "style_type": "crop",
                "sd_prompt": "textured crop haircut, short messy fringe, modern men's hairstyle, natural texture, photorealistic",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic",
            },
            {
                "name": "Pompadour",
                "category": "Classic Cuts",
                "length": "medium",
                "style_type": "pompadour",
                "sd_prompt": "classic pompadour hairstyle, slicked back volume on top, short sides, elegant men's hair, photorealistic",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic",
            },
            {
                "name": "Buzz Cut",
                "category": "Classic Cuts",
                "length": "short",
                "style_type": "buzz",
                "sd_prompt": "clean buzz cut, very short uniform length, military style haircut, photorealistic hair",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic",
            },
            {
                "name": "Quiff",
                "category": "Modern Styles",
                "length": "medium",
                "style_type": "quiff",
                "sd_prompt": "modern quiff hairstyle, volumized front swept up, tapered sides, stylish men's hair, photorealistic",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic",
            },
            {
                "name": "Side Part",
                "category": "Classic Cuts",
                "length": "medium",
                "style_type": "side_part",
                "sd_prompt": "classic side part hairstyle, clean hard part line, combed over, gentleman's haircut, photorealistic",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic",
            },
            {
                "name": "Undercut",
                "category": "Modern Styles",
                "length": "medium",
                "style_type": "undercut",
                "sd_prompt": "disconnected undercut hairstyle, long on top short buzzed sides, modern edgy men's hair, photorealistic",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic",
            },
        ],
    },
    "female": {
        "categories": [
            {"name": "Short Styles", "description": "Pixie cuts and short bobs"},
            {"name": "Medium Styles", "description": "Shoulder-length versatile looks"},
            {"name": "Long Styles", "description": "Long flowing hairstyles"},
        ],
        "hairstyles": [
            {
                "name": "Pixie Cut",
                "category": "Short Styles",
                "length": "short",
                "style_type": "pixie",
                "sd_prompt": "elegant pixie cut, short textured women's hairstyle, layered and chic, photorealistic hair",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic",
            },
            {
                "name": "Bob Cut",
                "category": "Short Styles",
                "length": "short",
                "style_type": "bob",
                "sd_prompt": "classic bob cut, chin-length straight hair, clean blunt ends, women's hairstyle, photorealistic",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic",
            },
            {
                "name": "Layered Lob",
                "category": "Medium Styles",
                "length": "medium",
                "style_type": "lob",
                "sd_prompt": "layered long bob lob hairstyle, shoulder length with soft layers, women's hair, photorealistic",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic",
            },
            {
                "name": "Beach Waves",
                "category": "Medium Styles",
                "length": "medium",
                "style_type": "waves",
                "sd_prompt": "beach waves hairstyle, soft tousled wavy hair, natural beachy texture, women's hair, photorealistic",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic",
            },
            {
                "name": "Straight Long",
                "category": "Long Styles",
                "length": "long",
                "style_type": "straight",
                "sd_prompt": "long straight sleek hair, flowing smooth silky hair, women's hairstyle, photorealistic",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic",
            },
            {
                "name": "Curly Long",
                "category": "Long Styles",
                "length": "long",
                "style_type": "curly",
                "sd_prompt": "long curly voluminous hair, bouncy defined curls, women's natural curly hairstyle, photorealistic",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic",
            },
            {
                "name": "Braided Updo",
                "category": "Long Styles",
                "length": "long",
                "style_type": "braids",
                "sd_prompt": "elegant braided updo hairstyle, intricate braids swept up, formal women's hair, photorealistic",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic",
            },
            {
                "name": "Curtain Bangs",
                "category": "Medium Styles",
                "length": "medium",
                "style_type": "bangs",
                "sd_prompt": "curtain bangs hairstyle, face-framing center-parted bangs, medium length hair, women's hair, photorealistic",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic",
            },
        ],
    },
    "children": {
        "categories": [
            {"name": "Boys Styles", "description": "Fun and easy styles for boys"},
            {"name": "Girls Styles", "description": "Cute styles for girls"},
        ],
        "hairstyles": [
            {
                "name": "Boys Crew Cut",
                "category": "Boys Styles",
                "length": "short",
                "style_type": "crew",
                "sd_prompt": "kid's crew cut hairstyle, short neat boys haircut, clean and simple, child's hair, photorealistic",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic, adult",
                "gender_override": "male",
            },
            {
                "name": "Boys Mohawk",
                "category": "Boys Styles",
                "length": "short",
                "style_type": "mohawk",
                "sd_prompt": "kid's faux mohawk hairstyle, fun spiked up center, short sides, child's hair, photorealistic",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic, adult",
                "gender_override": "male",
            },
            {
                "name": "Girls Bob",
                "category": "Girls Styles",
                "length": "short",
                "style_type": "bob",
                "sd_prompt": "cute girl's bob haircut, chin-length straight hair, child's hairstyle, photorealistic",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic, adult",
                "gender_override": "female",
            },
            {
                "name": "Girls Pigtails",
                "category": "Girls Styles",
                "length": "medium",
                "style_type": "pigtails",
                "sd_prompt": "cute pigtails hairstyle, two ponytails with ribbons, child's hairstyle, photorealistic",
                "sd_negative_prompt": "blurry, deformed, cartoon, anime, unrealistic, adult",
                "gender_override": "female",
            },
        ],
    },
}


def seed_hairstyles() -> None:
    """Populate the database with initial hairstyle catalog."""
    with get_session() as session:
        # Check if already seeded
        existing = session.query(Hairstyle).count()
        if existing > 0:
            return

        for gender_key, data in SEED_DATA.items():
            # Create categories
            cat_map = {}
            for cat_data in data["categories"]:
                cat_gender = gender_key if gender_key != "children" else "other"
                cat = HairstyleCategory(
                    name=f"{cat_data['name']} ({gender_key})",
                    gender=cat_gender,
                    description=cat_data["description"],
                )
                session.add(cat)
                session.flush()
                cat_map[cat_data["name"]] = cat

            # Create hairstyles
            for style_data in data["hairstyles"]:
                cat = cat_map[style_data["category"]]
                gender = style_data.get("gender_override", gender_key)
                if gender == "children":
                    gender = "other"

                hairstyle = Hairstyle(
                    name=style_data["name"],
                    category_id=cat.id,
                    gender=gender,
                    length=style_data["length"],
                    style_type=style_data["style_type"],
                    reference_image_path=f"assets/hairstyles/{gender_key}/{style_data['style_type']}.png",
                    sd_prompt=style_data["sd_prompt"],
                    sd_negative_prompt=style_data.get("sd_negative_prompt"),
                    is_active=True,
                )
                session.add(hairstyle)

        session.commit()
        print(f"Seeded {session.query(Hairstyle).count()} hairstyles")
