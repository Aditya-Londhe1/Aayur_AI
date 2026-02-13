# backend/app/services/ayurvedic_remedies_service.py
"""
Ayurvedic Home Remedies Service
Provides authentic, traditional homemade remedies for each dosha imbalance
"""
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class AyurvedicRemediesService:
    """Service for generating homemade Ayurvedic remedies"""
    
    def __init__(self):
        self.remedies_database = self._initialize_remedies()
        logger.info("AyurvedicRemediesService initialized")
    
    def _initialize_remedies(self) -> Dict[str, Any]:
        """Initialize comprehensive remedies database"""
        return {
            "vata": {
                "description": "Vata imbalance causes dryness, anxiety, and irregular digestion. Warm, grounding remedies are recommended.",
                "home_remedies": [
                    {
                        "name": "Warm Sesame Oil Massage (Abhyanga)",
                        "ingredients": ["Sesame oil (100ml)", "Optional: 2-3 drops lavender essential oil"],
                        "preparation": "Warm the sesame oil slightly (not hot). Add essential oil if desired.",
                        "usage": "Massage entire body before bath, leave for 15-20 minutes. Do daily or 3-4 times per week.",
                        "benefits": "Calms nervous system, improves circulation, reduces dryness and anxiety",
                        "time": "Morning or evening",
                        "difficulty": "Easy"
                    },
                    {
                        "name": "Ginger-Cinnamon Tea",
                        "ingredients": ["Fresh ginger (1 inch, grated)", "Cinnamon stick (1)", "Water (2 cups)", "Honey (1 tsp)"],
                        "preparation": "Boil water with ginger and cinnamon for 10 minutes. Strain and add honey when warm (not hot).",
                        "usage": "Drink 2-3 times daily, especially morning and evening",
                        "benefits": "Improves digestion, warms body, reduces gas and bloating",
                        "time": "Morning and evening",
                        "difficulty": "Easy"
                    },
                    {
                        "name": "Ashwagandha Milk",
                        "ingredients": ["Ashwagandha powder (1/2 tsp)", "Warm milk (1 cup)", "Honey or jaggery (1 tsp)", "Cardamom powder (pinch)"],
                        "preparation": "Mix ashwagandha powder in warm milk. Add honey/jaggery and cardamom. Stir well.",
                        "usage": "Drink before bedtime",
                        "benefits": "Reduces stress and anxiety, improves sleep, strengthens nervous system",
                        "time": "Before bed",
                        "difficulty": "Easy"
                    },
                    {
                        "name": "Triphala Powder",
                        "ingredients": ["Triphala powder (1/2 tsp)", "Warm water (1 cup)"],
                        "preparation": "Mix triphala powder in warm water. Let it sit for 5 minutes.",
                        "usage": "Drink before bedtime on empty stomach",
                        "benefits": "Regulates digestion, cleanses colon, balances all doshas",
                        "time": "Before bed",
                        "difficulty": "Easy"
                    },
                    {
                        "name": "Warm Spiced Milk with Nutmeg",
                        "ingredients": ["Milk (1 cup)", "Nutmeg powder (1/4 tsp)", "Cardamom (pinch)", "Saffron (2-3 strands)"],
                        "preparation": "Warm milk, add spices. Simmer for 2-3 minutes. Strain if needed.",
                        "usage": "Drink 30 minutes before sleep",
                        "benefits": "Promotes deep sleep, calms mind, nourishes nervous system",
                        "time": "Before bed",
                        "difficulty": "Easy"
                    },
                    {
                        "name": "Cumin-Coriander-Fennel Tea (CCF Tea)",
                        "ingredients": ["Cumin seeds (1 tsp)", "Coriander seeds (1 tsp)", "Fennel seeds (1 tsp)", "Water (3 cups)"],
                        "preparation": "Boil all seeds in water for 10 minutes. Strain and store in thermos.",
                        "usage": "Sip throughout the day",
                        "benefits": "Improves digestion, reduces gas, balances Vata",
                        "time": "Throughout day",
                        "difficulty": "Easy"
                    },
                    {
                        "name": "Ghee with Warm Water",
                        "ingredients": ["Pure cow ghee (1 tsp)", "Warm water (1 cup)"],
                        "preparation": "Mix ghee in warm water. Drink immediately.",
                        "usage": "First thing in morning on empty stomach",
                        "benefits": "Lubricates intestines, improves digestion, reduces constipation",
                        "time": "Morning (empty stomach)",
                        "difficulty": "Very Easy"
                    }
                ],
                "dietary_remedies": [
                    {
                        "name": "Warm Oatmeal with Ghee",
                        "ingredients": ["Oats (1/2 cup)", "Milk or water (1 cup)", "Ghee (1 tsp)", "Dates or raisins (5-6)", "Cinnamon (pinch)"],
                        "preparation": "Cook oats in milk/water. Add ghee, dates, and cinnamon.",
                        "usage": "Breakfast",
                        "benefits": "Grounding, nourishing, easy to digest"
                    },
                    {
                        "name": "Kitchari (Mung Dal Rice)",
                        "ingredients": ["Mung dal (1/2 cup)", "Rice (1/2 cup)", "Ghee (2 tsp)", "Cumin, ginger, turmeric", "Vegetables (optional)"],
                        "preparation": "Cook dal and rice together with spices and ghee until soft.",
                        "usage": "Lunch or dinner",
                        "benefits": "Complete protein, easy to digest, balancing for all doshas"
                    }
                ],
                "lifestyle_remedies": [
                    "Maintain regular daily routine (wake, eat, sleep at same times)",
                    "Practice gentle yoga: forward bends, child's pose, legs up the wall",
                    "Oil pulling with sesame oil (10 minutes daily)",
                    "Warm baths with Epsom salt before bed",
                    "Avoid cold, raw foods and drinks",
                    "Keep warm, especially feet and head"
                ]
            },
            "pitta": {
                "description": "Pitta imbalance causes heat, inflammation, and acidity. Cooling, soothing remedies are recommended.",
                "home_remedies": [
                    {
                        "name": "Coconut Water with Mint",
                        "ingredients": ["Fresh coconut water (1 cup)", "Fresh mint leaves (5-6)", "Lime juice (1/2 tsp)"],
                        "preparation": "Mix coconut water with crushed mint leaves and lime juice. Chill if desired.",
                        "usage": "Drink 2-3 times daily, especially mid-morning and afternoon",
                        "benefits": "Cools body, reduces acidity, hydrates, calms inflammation",
                        "time": "Mid-morning and afternoon",
                        "difficulty": "Very Easy"
                    },
                    {
                        "name": "Aloe Vera Juice",
                        "ingredients": ["Fresh aloe vera gel (2 tbsp)", "Water (1 cup)", "Honey (1 tsp, optional)"],
                        "preparation": "Blend aloe gel with water. Add honey if desired. Strain if needed.",
                        "usage": "Drink on empty stomach in morning",
                        "benefits": "Cools digestive system, reduces acidity, anti-inflammatory",
                        "time": "Morning (empty stomach)",
                        "difficulty": "Easy"
                    },
                    {
                        "name": "Coriander Seed Water",
                        "ingredients": ["Coriander seeds (1 tbsp)", "Water (2 cups)"],
                        "preparation": "Soak coriander seeds in water overnight. Strain in morning.",
                        "usage": "Drink throughout the day",
                        "benefits": "Cooling, reduces burning sensation, improves digestion",
                        "time": "Throughout day",
                        "difficulty": "Very Easy"
                    },
                    {
                        "name": "Rose Water Drink",
                        "ingredients": ["Rose water (2 tsp)", "Water (1 cup)", "Sugar or honey (1 tsp)", "Cardamom (pinch)"],
                        "preparation": "Mix rose water in cool water. Add sweetener and cardamom.",
                        "usage": "Drink 1-2 times daily",
                        "benefits": "Cooling, calms mind, reduces heat and anger",
                        "time": "Afternoon",
                        "difficulty": "Very Easy"
                    },
                    {
                        "name": "Fennel Seed Tea",
                        "ingredients": ["Fennel seeds (1 tsp)", "Water (1 cup)"],
                        "preparation": "Boil fennel seeds in water for 5 minutes. Strain.",
                        "usage": "After meals",
                        "benefits": "Cooling, improves digestion, reduces acidity and heartburn",
                        "time": "After meals",
                        "difficulty": "Easy"
                    },
                    {
                        "name": "Cucumber-Mint Cooler",
                        "ingredients": ["Cucumber (1, peeled)", "Mint leaves (10)", "Lime juice (1 tbsp)", "Water (1 cup)", "Rock salt (pinch)"],
                        "preparation": "Blend cucumber, mint, lime, and water. Add salt. Strain if desired.",
                        "usage": "Drink during hot weather or when feeling heated",
                        "benefits": "Extremely cooling, hydrating, reduces body heat",
                        "time": "Afternoon",
                        "difficulty": "Easy"
                    },
                    {
                        "name": "Neem Leaf Tea",
                        "ingredients": ["Fresh neem leaves (5-6) or dried (1 tsp)", "Water (1 cup)", "Honey (1 tsp)"],
                        "preparation": "Boil neem leaves in water for 5 minutes. Strain and add honey.",
                        "usage": "Once daily in morning",
                        "benefits": "Purifies blood, reduces skin inflammation, cooling",
                        "time": "Morning",
                        "difficulty": "Easy"
                    },
                    {
                        "name": "Coconut Oil Massage",
                        "ingredients": ["Coconut oil (100ml)", "Optional: sandalwood essential oil (2-3 drops)"],
                        "preparation": "Use coconut oil at room temperature. Add essential oil if desired.",
                        "usage": "Massage body before bath, especially scalp and feet",
                        "benefits": "Cooling, reduces body heat, calms mind",
                        "time": "Evening",
                        "difficulty": "Easy"
                    }
                ],
                "dietary_remedies": [
                    {
                        "name": "Cooling Breakfast Bowl",
                        "ingredients": ["Soaked oats (1/2 cup)", "Coconut milk (1/2 cup)", "Fresh fruits (berries, melon)", "Coconut flakes", "Cardamom"],
                        "preparation": "Mix soaked oats with coconut milk. Top with fruits and coconut.",
                        "usage": "Breakfast",
                        "benefits": "Cooling, light, easy to digest"
                    },
                    {
                        "name": "Mung Dal Soup",
                        "ingredients": ["Split mung dal (1 cup)", "Coriander, cumin, fennel", "Coconut (grated)", "Curry leaves"],
                        "preparation": "Cook dal with cooling spices. Add coconut and curry leaves.",
                        "usage": "Lunch or dinner",
                        "benefits": "Cooling, protein-rich, easy to digest"
                    }
                ],
                "lifestyle_remedies": [
                    "Avoid excessive heat and sun exposure",
                    "Practice cooling pranayama: Sheetali and Sheetkari",
                    "Moonlight walks in evening",
                    "Avoid spicy, oily, and fried foods",
                    "Practice meditation to calm mind",
                    "Wear light, breathable cotton clothes"
                ]
            },
            "kapha": {
                "description": "Kapha imbalance causes heaviness, lethargy, and congestion. Stimulating, warming remedies are recommended.",
                "home_remedies": [
                    {
                        "name": "Ginger-Honey Tea",
                        "ingredients": ["Fresh ginger (1 inch, grated)", "Water (1 cup)", "Raw honey (1 tsp)", "Black pepper (pinch)"],
                        "preparation": "Boil ginger in water for 10 minutes. Let cool slightly, add honey and pepper.",
                        "usage": "Drink 2-3 times daily, especially morning",
                        "benefits": "Stimulates metabolism, reduces congestion, improves digestion",
                        "time": "Morning and afternoon",
                        "difficulty": "Easy"
                    },
                    {
                        "name": "Trikatu Powder Mix",
                        "ingredients": ["Dry ginger powder (1 part)", "Black pepper (1 part)", "Long pepper/Pippali (1 part)", "Honey (1 tsp)"],
                        "preparation": "Mix equal parts of three spices. Take 1/4 tsp with honey.",
                        "usage": "Before meals, twice daily",
                        "benefits": "Kindles digestive fire, reduces mucus, stimulates metabolism",
                        "time": "Before meals",
                        "difficulty": "Easy"
                    },
                    {
                        "name": "Turmeric-Ginger Milk",
                        "ingredients": ["Turmeric powder (1/2 tsp)", "Ginger powder (1/4 tsp)", "Warm milk (1 cup)", "Black pepper (pinch)", "Honey (1 tsp)"],
                        "preparation": "Mix spices in warm milk. Add honey when slightly cool.",
                        "usage": "Once daily, preferably evening",
                        "benefits": "Anti-inflammatory, reduces congestion, boosts immunity",
                        "time": "Evening",
                        "difficulty": "Easy"
                    },
                    {
                        "name": "Lemon-Honey Water",
                        "ingredients": ["Warm water (1 cup)", "Fresh lemon juice (1/2 lemon)", "Raw honey (1 tsp)", "Ginger juice (1/4 tsp)"],
                        "preparation": "Mix all ingredients in warm (not hot) water.",
                        "usage": "First thing in morning on empty stomach",
                        "benefits": "Detoxifies, stimulates metabolism, reduces mucus",
                        "time": "Morning (empty stomach)",
                        "difficulty": "Very Easy"
                    },
                    {
                        "name": "Mustard Oil Massage",
                        "ingredients": ["Mustard oil (100ml)", "Optional: eucalyptus oil (2-3 drops)"],
                        "preparation": "Warm mustard oil slightly. Add essential oil if desired.",
                        "usage": "Vigorous massage before bath, 2-3 times per week",
                        "benefits": "Stimulating, reduces stiffness, improves circulation",
                        "time": "Morning",
                        "difficulty": "Easy"
                    },
                    {
                        "name": "Clove-Cinnamon Tea",
                        "ingredients": ["Cloves (3-4)", "Cinnamon stick (1)", "Cardamom (2 pods)", "Water (2 cups)", "Honey (1 tsp)"],
                        "preparation": "Boil spices in water for 10 minutes. Strain and add honey.",
                        "usage": "2-3 times daily",
                        "benefits": "Warming, reduces congestion, improves circulation",
                        "time": "Morning and afternoon",
                        "difficulty": "Easy"
                    },
                    {
                        "name": "Dry Ginger Powder with Warm Water",
                        "ingredients": ["Dry ginger powder (1/4 tsp)", "Warm water (1 cup)", "Honey (1 tsp)"],
                        "preparation": "Mix ginger powder in warm water. Add honey.",
                        "usage": "Before breakfast",
                        "benefits": "Kindles digestive fire, reduces heaviness, stimulates metabolism",
                        "time": "Morning",
                        "difficulty": "Very Easy"
                    },
                    {
                        "name": "Steam Inhalation with Eucalyptus",
                        "ingredients": ["Hot water (bowl)", "Eucalyptus oil (3-4 drops) or fresh leaves", "Towel"],
                        "preparation": "Add eucalyptus to hot water. Cover head with towel and inhale steam.",
                        "usage": "Once daily, especially if congested",
                        "benefits": "Clears respiratory congestion, opens sinuses",
                        "time": "Evening",
                        "difficulty": "Easy"
                    }
                ],
                "dietary_remedies": [
                    {
                        "name": "Spiced Vegetable Soup",
                        "ingredients": ["Mixed vegetables", "Ginger, garlic, black pepper", "Turmeric", "Minimal oil", "Lemon juice"],
                        "preparation": "Cook vegetables with warming spices. Keep it light and brothy.",
                        "usage": "Lunch or dinner",
                        "benefits": "Light, warming, easy to digest, reduces heaviness"
                    },
                    {
                        "name": "Barley Water",
                        "ingredients": ["Barley (2 tbsp)", "Water (3 cups)", "Lemon juice (1 tbsp)", "Honey (1 tsp)"],
                        "preparation": "Boil barley in water for 30 minutes. Strain, add lemon and honey.",
                        "usage": "Throughout day",
                        "benefits": "Cooling, diuretic, reduces water retention"
                    }
                ],
                "lifestyle_remedies": [
                    "Wake up early (before 6 AM)",
                    "Practice vigorous exercise: running, cycling, dynamic yoga",
                    "Avoid daytime napping",
                    "Reduce heavy, oily, and sweet foods",
                    "Practice energizing pranayama: Bhastrika, Kapalabhati",
                    "Stay active throughout the day"
                ]
            }
        }
    
    def get_remedies_for_dosha(self, dominant_dosha: str, imbalance_level: str = "moderate") -> Dict[str, Any]:
        """
        Get comprehensive remedies for a specific dosha
        
        Args:
            dominant_dosha: The imbalanced dosha (vata, pitta, kapha)
            imbalance_level: Severity (mild, moderate, severe)
        
        Returns:
            Dictionary with categorized remedies
        """
        dosha = dominant_dosha.lower()
        
        if dosha not in self.remedies_database:
            logger.warning(f"Unknown dosha: {dosha}, defaulting to vata")
            dosha = "vata"
        
        remedies = self.remedies_database[dosha]
        
        # Adjust number of remedies based on imbalance level
        num_remedies = {
            "mild": 3,
            "moderate": 5,
            "severe": 7
        }.get(imbalance_level, 5)
        
        return {
            "dosha": dosha.capitalize(),
            "imbalance_level": imbalance_level,
            "description": remedies["description"],
            "home_remedies": remedies["home_remedies"][:num_remedies],
            "dietary_remedies": remedies["dietary_remedies"],
            "lifestyle_remedies": remedies["lifestyle_remedies"],
            "total_remedies": len(remedies["home_remedies"]),
            "note": "These are traditional Ayurvedic home remedies. Consult an Ayurvedic practitioner for personalized treatment."
        }
    
    def get_remedy_by_symptom(self, symptom: str) -> List[Dict[str, Any]]:
        """Get specific remedies for a symptom"""
        symptom_remedies = {
            "headache": [
                {
                    "name": "Ginger Paste Application",
                    "preparation": "Make paste of fresh ginger with water. Apply on forehead.",
                    "benefits": "Reduces headache, improves circulation"
                }
            ],
            "acidity": [
                {
                    "name": "Coconut Water",
                    "preparation": "Drink fresh coconut water",
                    "benefits": "Neutralizes acid, cools stomach"
                }
            ],
            "constipation": [
                {
                    "name": "Triphala with Warm Water",
                    "preparation": "Mix 1/2 tsp triphala in warm water before bed",
                    "benefits": "Natural laxative, regulates bowel movements"
                }
            ],
            "insomnia": [
                {
                    "name": "Nutmeg Milk",
                    "preparation": "Add pinch of nutmeg to warm milk before bed",
                    "benefits": "Promotes deep sleep, calms mind"
                }
            ]
        }
        
        return symptom_remedies.get(symptom.lower(), [])
    
    def get_seasonal_remedies(self, season: str, dosha: str) -> List[str]:
        """Get season-specific remedies"""
        seasonal_tips = {
            "summer": {
                "vata": ["Stay hydrated", "Avoid excessive sun"],
                "pitta": ["Use cooling foods", "Avoid spicy foods", "Stay in shade"],
                "kapha": ["Light exercise", "Avoid cold drinks"]
            },
            "winter": {
                "vata": ["Keep warm", "Oil massage daily", "Warm foods"],
                "pitta": ["Moderate heating", "Balanced diet"],
                "kapha": ["Vigorous exercise", "Avoid heavy foods", "Stay active"]
            },
            "monsoon": {
                "vata": ["Warm, cooked foods", "Avoid cold, raw foods"],
                "pitta": ["Moderate cooling", "Avoid fermented foods"],
                "kapha": ["Light, warm foods", "Avoid dairy", "Stay dry"]
            }
        }
        
        return seasonal_tips.get(season.lower(), {}).get(dosha.lower(), [])

# Global instance
ayurvedic_remedies_service = AyurvedicRemediesService()
