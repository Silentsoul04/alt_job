import re

class AddKeywordMatchesPipeline(object):

    # English and French keywords
    matches=list(set([   
        
        "climate", "animal", "wildlife", "biomass", "pollution", "conservation", "biodiversity", 
        "nature", "ecotourism", "sustainable", "renewable", "energy", "environment", "education", "food",
        "agriculture", "organic", "farming", "forest", "green", "social",  "business", "entrepreneurship", 
        "leadership", "media", "journalism", "food security", "health", "ocean", "bike", "recycle", "waste",
        
        "climat", "animal", "faune", "biomasse", "pollution", "conservation", "biodiversité", 
        "nature", "écotourisme", "durable", "renouvelable", "énergie", "environnement", "éducation", "alimentation",
        "agriculture", "biologique", "agriculture", "forêt", "vert", "social", "entreprise", "esprit d'entreprise", 
        "leadership", "médias", "journalisme", "sécurité alimentaire", "santé", "océan", "vélo", "recyclage", "déchets"

    ]))
    
    def process_item(self, item, spider):
        
        item['keywords_matched'] = [m for m in self.matches if m in item.get_text()]
        
        return item