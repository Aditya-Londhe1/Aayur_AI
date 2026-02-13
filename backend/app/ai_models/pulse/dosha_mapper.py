"""
Ayurvedic knowledge base for pulse analysis (Nadi Pariksha)
Mapping modern pulse features to traditional Ayurvedic concepts
"""

class AyurvedicPulseMapper:
    """Maps pulse characteristics to Ayurvedic doshas and prakriti"""
    
    # Traditional Ayurvedic pulse characteristics
    TRADITIONAL_NADI_TYPES = {
        'vata': {
            'gati': 'sarpa_gati',  # serpentine movement
            'speed': 'fast',
            'force': 'weak',
            'volume': 'low',
            'rhythm': 'irregular',
            'temperature': 'cold',
            'character': 'light, thin, rapid',
            'season_affinity': 'autumn',
            'time_of_day': 'sunset, early morning',
            'emotional_state': 'anxious, creative, variable'
        },
        'pitta': {
            'gati': 'manduka_gati',  # frog-like jumping
            'speed': 'moderate',
            'force': 'strong',
            'volume': 'medium',
            'rhythm': 'regular',
            'temperature': 'hot',
            'character': 'sharp, bounding, warm',
            'season_affinity': 'summer',
            'time_of_day': 'midday, midnight',
            'emotional_state': 'focused, intense, transformative'
        },
        'kapha': {
            'gati': 'hansa_gati',  # swan-like
            'speed': 'slow',
            'force': 'steady',
            'volume': 'high',
            'rhythm': 'regular',
            'temperature': 'cool',
            'character': 'broad, smooth, steady',
            'season_affinity': 'spring',
            'time_of_day': 'morning, evening',
            'emotional_state': 'calm, stable, nurturing'
        },
        'balanced': {
            'gati': 'sama_gati',  # balanced movement
            'speed': 'moderate',
            'force': 'moderate',
            'volume': 'balanced',
            'rhythm': 'regular',
            'temperature': 'warm',
            'character': 'smooth, rhythmic, harmonious',
            'season_affinity': 'all seasons',
            'time_of_day': 'all times',
            'emotional_state': 'balanced, content, healthy'
        }
    }
    
    # Dosha combination mappings
    DOSHA_COMBINATIONS = {
        'vata_pitta': {
            'description': 'Creative energy with metabolic intensity',
            'characteristics': ['irregular rhythm', 'sharp peaks', 'variable amplitude'],
            'health_implications': ['digestive sensitivity', 'variable energy', 'heat intolerance'],
            'balancing_recommendations': ['regular routine', 'cooling foods', 'moderate exercise']
        },
        'vata_kapha': {
            'description': 'Creative potential with structural stability',
            'characteristics': ['slow irregularity', 'moderate amplitude', 'cool temperature'],
            'health_implications': ['joint concerns', 'respiratory sensitivity', 'metabolic variability'],
            'balancing_recommendations': ['warm foods', 'gentle movement', 'consistent schedule']
        },
        'pitta_kapha': {
            'description': 'Metabolic intensity with structural stability',
            'characteristics': ['regular rhythm', 'strong amplitude', 'steady pace'],
            'health_implications': ['inflammatory tendencies', 'weight management', 'heat accumulation'],
            'balancing_recommendations': ['cooling practices', 'light foods', 'moderate exercise']
        },
        'tridoshic': {
            'description': 'All three doshas in dynamic balance',
            'characteristics': ['adaptable rhythm', 'balanced amplitude', 'harmonious flow'],
            'health_implications': ['good resilience', 'balanced metabolism', 'stable energy'],
            'balancing_recommendations': ['seasonal adjustments', 'varied diet', 'balanced lifestyle']
        }
    }
    
    # Pulse positions and their meanings
    PULSE_POSITIONS = {
        'vata_position': {
            'finger': 'index',
            'location': 'superficial',
            'organ_association': ['colon', 'nervous system', 'ears', 'bones'],
            'element': 'air/ether',
            'qualities': ['mobile', 'dry', 'light', 'cold', 'rough', 'subtle']
        },
        'pitta_position': {
            'finger': 'middle',
            'location': 'middle',
            'organ_association': ['small intestine', 'liver', 'spleen', 'eyes'],
            'element': 'fire/water',
            'qualities': ['hot', 'sharp', 'light', 'liquid', 'spreading', 'oily']
        },
        'kapha_position': {
            'finger': 'ring',
            'location': 'deep',
            'organ_association': ['stomach', 'lungs', 'sinuses', 'lymph'],
            'element': 'earth/water',
            'qualities': ['heavy', 'slow', 'cool', 'oily', 'smooth', 'dense', 'soft']
        }
    }
    
    @classmethod
    def map_features_to_dosha(cls, features: dict) -> dict:
        """Map pulse features to Ayurvedic dosha characteristics"""
        
        # Determine dominant dosha
        dosha_scores = {
            'vata': cls._calculate_vata_score(features),
            'pitta': cls._calculate_pitta_score(features),
            'kapha': cls._calculate_kapha_score(features)
        }
        
        dominant_dosha = max(dosha_scores, key=dosha_scores.get)
        confidence = dosha_scores[dominant_dosha]
        
        # Get traditional characteristics
        traditional = cls.TRADITIONAL_NADI_TYPES.get(dominant_dosha, {})
        
        # Determine secondary dosha if significant
        secondary_dosha = None
        sorted_doshas = sorted(dosha_scores.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_doshas) > 1:
            if sorted_doshas[1][1] > 0.3:  # Threshold for secondary influence
                secondary_dosha = sorted_doshas[1][0]
        
        # Create combination if secondary exists
        combination = None
        if secondary_dosha and secondary_dosha != dominant_dosha:
            combination = f"{dominant_dosha}_{secondary_dosha}"
            if combination not in cls.DOSHA_COMBINATIONS:
                combination = f"{secondary_dosha}_{dominant_dosha}"
        
        # Generate Ayurvedic interpretation
        interpretation = cls._generate_interpretation(
            dominant_dosha, secondary_dosha, features
        )
        
        # Health recommendations
        recommendations = cls._generate_recommendations(
            dominant_dosha, secondary_dosha, features
        )
        
        return {
            'dominant_dosha': dominant_dosha,
            'secondary_dosha': secondary_dosha,
            'dosha_combination': combination,
            'confidence': confidence,
            'dosha_scores': dosha_scores,
            'traditional_characteristics': traditional,
            'interpretation': interpretation,
            'recommendations': recommendations,
            'pulse_positions': cls.PULSE_POSITIONS,
            'ayurvedic_insights': cls._generate_ayurvedic_insights(features)
        }
    
    @classmethod
    def _calculate_vata_score(cls, features: dict) -> float:
        """Calculate Vata score from features"""
        score = 0.0
        
        # Rhythm irregularity - strong Vata indicator
        if features.get('rhythm_type') == 'irregular':
            score += 0.5
        
        # Heart rate variability - higher HRV indicates Vata
        hrv = features.get('hrv', 0)
        score += min(hrv / 30, 0.3)  # Adjusted normalization
        
        # Signal complexity - higher entropy indicates Vata
        entropy = features.get('sample_entropy', 0)
        score += min(entropy / 1.5, 0.3)  # Adjusted normalization
        
        # Fast heart rate - Vata tends to be faster
        hr = features.get('heart_rate', 70)
        if hr > 85:
            score += min((hr - 85) / 30, 0.3)
        
        return min(score, 1.0)
    
    @classmethod
    def _calculate_pitta_score(cls, features: dict) -> float:
        """Calculate Pitta score from features"""
        score = 0.0
        
        # Strong amplitude - Pitta has strong, bounding pulse
        amplitude = features.get('mean_peak_amplitude', 0)
        score += min(amplitude / 10, 0.3)  # Adjusted normalization
        
        # Moderate to high heart rate - Pitta range
        hr = features.get('heart_rate', 70)
        if 75 <= hr <= 90:
            score += 0.3  # Peak score in Pitta range
        elif hr > 90:
            score += max(0, 0.3 - (hr - 90) / 50)  # Decrease above 90
        
        # Signal sharpness - adjusted to prevent over-scoring
        sharpness = features.get('pitta_score', 0)
        score += min(sharpness / 500, 0.2)  # Increased denominator
        
        # Regular rhythm - but less weight than Kapha
        if features.get('rhythm_type') == 'regular':
            score += 0.15
        
        return min(score, 1.0)
    
    @classmethod
    def _calculate_kapha_score(cls, features: dict) -> float:
        """Calculate Kapha score from features"""
        score = 0.0
        
        # Slow heart rate - strong Kapha indicator
        hr = features.get('heart_rate', 70)
        if hr < 65:
            score += min((65 - hr) / 15, 0.4)  # Stronger weight for slow HR
        
        # Signal stability - low variability indicates Kapha
        std_rr = features.get('std_rr', 0)
        if std_rr < 0.1:
            score += 0.3  # Very stable
        elif std_rr < 0.2:
            score += 0.15  # Moderately stable
        
        # High power in very low frequencies - Kapha indicator
        vlf_power = features.get('vlf_power', 0)
        score += min(vlf_power / 800, 0.3)  # Adjusted normalization
        
        # Smooth, regular rhythm - strong Kapha indicator
        if features.get('rhythm_type') == 'regular':
            score += 0.25  # Higher weight for Kapha
        
        return min(score, 1.0)
    
    @classmethod
    def _generate_interpretation(cls, dominant_dosha: str, 
                               secondary_dosha: str, 
                               features: dict) -> str:
        """Generate Ayurvedic interpretation"""
        
        interpretations = {
            'vata': "The pulse exhibits Vata characteristics - light, quick, and irregular "
                   "like the movement of a serpent. This suggests creative energy, adaptability, "
                   "and variable physiological rhythms. When balanced, Vata promotes creativity "
                   "and movement; when imbalanced, it may lead to anxiety or irregularity.",
            
            'pitta': "The pulse shows Pitta qualities - sharp, strong, and penetrating "
                    "like the leap of a frog. This indicates metabolic intensity, transformation, "
                    "and thermal regulation. Balanced Pitta supports digestion and intellect; "
                    "imbalanced it may create excess heat or inflammation.",
            
            'kapha': "The pulse demonstrates Kapha nature - slow, steady, and nourishing "
                    "like the glide of a swan. This represents structural stability, lubrication, "
                    "and physiological reserve. Balanced Kapha provides strength and endurance; "
                    "imbalanced it may lead to stagnation or heaviness.",
            
            'balanced': "The pulse reveals a balanced state - harmonious, rhythmic, and adaptable. "
                       "This indicates optimal dosha balance, supporting overall health, "
                       "resilience, and homeostasis."
        }
        
        interpretation = interpretations.get(dominant_dosha, "")
        
        # Add combination information
        if secondary_dosha:
            combination = f"{dominant_dosha}_{secondary_dosha}"
            if combination in cls.DOSHA_COMBINATIONS:
                combo_info = cls.DOSHA_COMBINATIONS[combination]
                interpretation += f"\n\nWith secondary influence of {secondary_dosha.capitalize()}: "
                interpretation += combo_info['description']
        
        # Add specific observations
        hr = features.get('heart_rate', 70)
        if hr > 85:
            interpretation += " The elevated heart rate suggests increased metabolic activity."
        elif hr < 60:
            interpretation += " The slower rhythm indicates a calm, steady constitution."
        
        rhythm = features.get('rhythm_type', '')
        if rhythm == 'irregular':
            interpretation += " Irregular rhythm suggests adaptability and responsiveness."
        
        return interpretation
    
    @classmethod
    def _generate_recommendations(cls, dominant_dosha: str,
                                secondary_dosha: str,
                                features: dict) -> dict:
        """Generate Ayurvedic recommendations"""
        
        base_recommendations = {
            'vata': {
                'diet': ['Warm, cooked foods', 'Nourishing soups', 'Healthy fats', 
                        'Root vegetables', 'Sweet fruits'],
                'lifestyle': ['Regular routine', 'Adequate rest', 'Gentle exercise', 
                             'Warm oil massage', 'Meditation'],
                'avoid': ['Cold foods', 'Excessive raw foods', 'Irregular eating', 
                         'Over-stimulation', 'Excessive travel'],
                'herbs': ['Ashwagandha', 'Brahmi', 'Shatavari', 'Ginger', 'Cinnamon']
            },
            'pitta': {
                'diet': ['Cooling foods', 'Sweet fruits', 'Bitter greens', 
                        'Coconut', 'Mint'],
                'lifestyle': ['Moderate exercise', 'Cool environments', 
                            'Mindful work pace', 'Water activities', 'Moon gazing'],
                'avoid': ['Spicy foods', 'Excessive heat', 'Competitive situations', 
                         'Alcohol', 'Overwork'],
                'herbs': ['Amalaki', 'Neem', 'Brahmi', 'Coriander', 'Fennel']
            },
            'kapha': {
                'diet': ['Light, warm foods', 'Bitter greens', 'Spices', 
                        'Legumes', 'Honey'],
                'lifestyle': ['Vigorous exercise', 'Stimulating activities', 
                            'Variety in routine', 'Dry massage', 'Early rising'],
                'avoid': ['Heavy foods', 'Excessive sleep', 'Sedentary habits', 
                         'Cold drinks', 'Dairy'],
                'herbs': ['Turmeric', 'Ginger', 'Triphala', 'Pippali', 'Mustard']
            },
            'balanced': {
                'diet': ['Varied, seasonal foods', 'All six tastes', 'Fresh ingredients'],
                'lifestyle': ['Balanced routine', 'Varied exercise', 'Mind-body practices'],
                'avoid': ['Excess of any quality', 'Extreme behaviors', 'Toxins'],
                'herbs': ['Adaptogens', 'Rasayanas', 'Seasonal herbs']
            }
        }
        
        # Get base recommendations for dominant dosha
        rec = base_recommendations.get(dominant_dosha, {}).copy()
        
        # Adjust for secondary dosha influence
        if secondary_dosha:
            secondary_rec = base_recommendations.get(secondary_dosha, {})
            
            # Merge recommendations
            for category in ['diet', 'lifestyle', 'avoid', 'herbs']:
                if category in secondary_rec:
                    rec[category] = rec.get(category, []) + [
                        f"(for {secondary_dosha} influence): " + item 
                        for item in secondary_rec[category][:2]
                    ]
        
        # Add personalized recommendations based on features
        personalized = []
        
        hr = features.get('heart_rate', 70)
        if hr > 85:
            personalized.append("Practice cooling pranayama like Sheetali")
        elif hr < 60:
            personalized.append("Include invigorating spices in diet")
        
        rhythm = features.get('rhythm_type', '')
        if rhythm == 'irregular':
            personalized.append("Establish regular daily routine")
        
        if features.get('has_stress_indicator', False):
            personalized.append("Incorporate stress-reduction practices")
        
        if personalized:
            rec['personalized'] = personalized
        
        # Add seasonal considerations
        rec['seasonal_advice'] = cls._get_seasonal_advice(dominant_dosha)
        
        return rec
    
    @classmethod
    def _get_seasonal_advice(cls, dosha: str) -> dict:
        """Get seasonal balancing advice"""
        
        seasonal_mapping = {
            'vata': {
                'autumn': 'Grounding practices, warm foods, oil massage',
                'winter': 'Stay warm, nourishing soups, adequate rest',
                'spring': 'Gentle detox, light foods, gradual activity increase',
                'summer': 'Stay cool, hydrate, moderate exercise'
            },
            'pitta': {
                'summer': 'Maximum cooling, avoid sun, sweet fruits',
                'autumn': 'Moderate cooling, bitter greens, evening walks',
                'winter': 'Warm but not spicy foods, avoid overheating',
                'spring': 'Light detox, cooling herbs, water activities'
            },
            'kapha': {
                'spring': 'Vigorous detox, light foods, stimulating exercise',
                'summer': 'Light cooling, bitter tastes, swimming',
                'autumn': 'Warm spicy foods, dry massage, varied activities',
                'winter': 'Stay active, warm spices, avoid heavy foods'
            }
        }
        
        return seasonal_mapping.get(dosha, {})
    
    @classmethod
    def _generate_ayurvedic_insights(cls, features: dict) -> list:
        """Generate specific Ayurvedic insights from features"""
        
        insights = []
        
        # Heart rate insights
        hr = features.get('heart_rate', 70)
        if hr > 85:
            insights.append("Elevated pulse suggests increased Agni (digestive fire)")
        elif hr < 60:
            insights.append("Slower rhythm indicates strong Ojas (vitality reserve)")
        
        # Rhythm insights
        rhythm = features.get('rhythm_type', '')
        if rhythm == 'irregular':
            insights.append("Variable rhythm reflects Vata's mobile nature")
        elif rhythm == 'regular':
            insights.append("Steady rhythm shows doshic balance")
        
        # Amplitude insights
        amplitude = features.get('mean_peak_amplitude', 0)
        if amplitude > 4:
            insights.append("Strong pulse waves indicate robust Prana (life force)")
        
        # Complexity insights
        entropy = features.get('sample_entropy', 0)
        if entropy > 1.5:
            insights.append("Complex pattern suggests adaptability and responsiveness")
        
        # Seasonal correlation
        vlf_power = features.get('vlf_power', 0)
        if vlf_power > 500:
            insights.append("Strong low-frequency power correlates with Kapha qualities")
        
        return insights