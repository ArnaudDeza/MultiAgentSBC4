"""
Pre-defined debate topics for the multi-agent debate system.
"""

# Dictionary of debate topics organized by category
DEBATE_TOPICS = {
    # Technology & AI
    "ai_education": "Should artificial intelligence replace human teachers in classrooms?",
    "ai_jobs": "Will artificial intelligence ultimately create more jobs than it destroys?",
    "social_media": "Do social media platforms do more harm than good for society?",
    "privacy_surveillance": "Should governments have access to citizens' private digital communications for security purposes?",
    "autonomous_vehicles": "Should fully autonomous vehicles be allowed on public roads without human oversight?",
    "tech_regulation": "Should large technology companies be broken up to prevent monopolistic practices?",
    "digital_currency": "Should governments replace traditional currency with central bank digital currencies?",
    "internet_access": "Should internet access be considered a fundamental human right?",
    
    # Environment & Climate
    "nuclear_energy": "Is nuclear energy essential for combating climate change?",
    "carbon_tax": "Should there be a global carbon tax to address climate change?",
    "plastic_ban": "Should single-use plastics be banned worldwide?",
    "renewable_energy": "Should countries prioritize renewable energy over economic growth?",
    "geoengineering": "Should we pursue large-scale geoengineering projects to combat climate change?",
    "meat_consumption": "Should governments implement policies to reduce meat consumption for environmental reasons?",
    "electric_vehicles": "Should the sale of gasoline-powered vehicles be banned by 2035?",
    
    # Education & Society
    "standardized_testing": "Should standardized testing be eliminated from educational systems?",
    "college_free": "Should higher education be free for all students?",
    "remote_learning": "Is remote learning as effective as traditional in-person education?",
    "school_uniforms": "Should school uniforms be mandatory in all public schools?",
    "homework_ban": "Should homework be banned in elementary schools?",
    "year_round_school": "Should schools operate year-round instead of having long summer breaks?",
    "financial_literacy": "Should financial literacy be a required subject in high school?",
    
    # Healthcare & Medicine
    "universal_healthcare": "Should all countries implement universal healthcare systems?",
    "vaccine_mandates": "Should vaccination be mandatory for participation in public activities?",
    "mental_health": "Should mental health treatment be given equal priority to physical health treatment?",
    "drug_legalization": "Should all drugs be decriminalized and treated as a health issue rather than criminal issue?",
    "genetic_engineering": "Should genetic engineering be used to enhance human capabilities?",
    "organ_market": "Should there be a regulated market for organ donation?",
    "euthanasia": "Should physician-assisted death be legal for terminally ill patients?",
    
    # Economics & Politics
    "universal_income": "Should universal basic income be implemented globally?",
    "wealth_tax": "Should there be a wealth tax on the ultra-rich?",
    "minimum_wage": "Should the minimum wage be raised to a living wage in all countries?",
    "cryptocurrency": "Should cryptocurrency be regulated like traditional financial instruments?",
    "corporate_tax": "Should multinational corporations pay a global minimum tax rate?",
    "automation_tax": "Should companies be taxed for replacing human workers with automation?",
    "four_day_workweek": "Should the standard work week be reduced to four days?",
    
    # Ethics & Philosophy
    "animal_rights": "Should animals have the same legal rights as humans?",
    "death_penalty": "Should the death penalty be abolished worldwide?",
    "space_exploration": "Should space exploration funding be redirected to solving Earth's problems?",
    "artificial_consciousness": "If AI develops consciousness, should it have rights equal to humans?",
    "genetic_privacy": "Should genetic information be private or available for research and law enforcement?",
    "cultural_preservation": "Should globalization be limited to preserve local cultures?",
    
    # Fun & Lifestyle
    "pineapple_pizza": "Should pineapple be an acceptable pizza topping?",
    "daylight_saving": "Should daylight saving time be permanently abolished?",
    "video_games": "Do video games have a positive or negative impact on society?",
    "fast_fashion": "Should fast fashion be banned to protect workers and the environment?",
    "social_credit": "Should countries implement social credit scoring systems?",
    "space_colonization": "Should humanity prioritize colonizing Mars over fixing Earth's problems?",
    
    # Sports & Competition
    "college_athletes": "Should college athletes be paid for their participation in sports?",
    "performance_drugs": "Should performance-enhancing drugs be allowed in professional sports?",
    "esports_olympics": "Should esports be included in the Olympic Games?",
    "youth_sports": "Should competitive sports be eliminated from elementary schools?",
    
    # Media & Entertainment
    "cancel_culture": "Is cancel culture a necessary form of accountability or harmful censorship?",
    "streaming_monopoly": "Should streaming services be prevented from producing exclusive content?",
    "news_bias": "Should news organizations be required to present balanced viewpoints on controversial topics?",
    "content_moderation": "Should social media platforms be responsible for moderating user-generated content?",
}

# Categories for easy browsing
TOPIC_CATEGORIES = {
    "technology": ["ai_education", "ai_jobs", "social_media", "privacy_surveillance", "autonomous_vehicles", "tech_regulation", "digital_currency", "internet_access"],
    "environment": ["nuclear_energy", "carbon_tax", "plastic_ban", "renewable_energy", "geoengineering", "meat_consumption", "electric_vehicles"],
    "education": ["standardized_testing", "college_free", "remote_learning", "school_uniforms", "homework_ban", "year_round_school", "financial_literacy"],
    "healthcare": ["universal_healthcare", "vaccine_mandates", "mental_health", "drug_legalization", "genetic_engineering", "organ_market", "euthanasia"],
    "economics": ["universal_income", "wealth_tax", "minimum_wage", "cryptocurrency", "corporate_tax", "automation_tax", "four_day_workweek"],
    "ethics": ["animal_rights", "death_penalty", "space_exploration", "artificial_consciousness", "genetic_privacy", "cultural_preservation"],
    "lifestyle": ["pineapple_pizza", "daylight_saving", "video_games", "fast_fashion", "social_credit", "space_colonization"],
    "sports": ["college_athletes", "performance_drugs", "esports_olympics", "youth_sports"],
    "media": ["cancel_culture", "streaming_monopoly", "news_bias", "content_moderation"],
}


def get_topic(topic_key: str) -> str:
    """
    Get a debate topic by its key.
    
    Args:
        topic_key: The key for the desired topic
        
    Returns:
        The debate topic question, or None if not found
    """
    return DEBATE_TOPICS.get(topic_key)


def list_topics() -> None:
    """Print all available topics organized by category."""
    print("Available Debate Topics:")
    print("=" * 50)
    
    for category, topic_keys in TOPIC_CATEGORIES.items():
        print(f"\n{category.upper()}:")
        for key in topic_keys:
            if key in DEBATE_TOPICS:
                print(f"  {key}: {DEBATE_TOPICS[key]}")
    
    print(f"\nTotal topics available: {len(DEBATE_TOPICS)}")


def list_topic_keys() -> None:
    """Print just the topic keys for easy reference."""
    print("Available Topic Keys:")
    print("=" * 30)
    
    for category, topic_keys in TOPIC_CATEGORIES.items():
        print(f"\n{category.upper()}:")
        for key in topic_keys:
            print(f"  {key}")


if __name__ == "__main__":
    list_topics() 