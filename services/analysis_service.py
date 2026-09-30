from __future__ import annotations

from services.image_service import ImageMetrics


class AnalysisService:
    @staticmethod
    def get_advice(crop_name: str, metrics: ImageMetrics) -> str:
        crop_name = crop_name or 'Selected crop'
        if metrics.status == 'Healthy':
            return (
                f'{crop_name} is performing well. Maintain balanced irrigation, '
                'continue field scouting, and keep nutrient supply stable.'
            )
        if metrics.status == 'Mild Stress':
            return (
                f'{crop_name} shows early stress symptoms. Check water schedule, '
                'inspect leaves for pests, and review nitrogen or micronutrient levels.'
            )
        return (
            f'{crop_name} appears diseased or severely stressed. Isolate affected plants, '
            'inspect for fungal or bacterial symptoms, and apply recommended treatment quickly.'
        )

    @staticmethod
    def get_classification_note(metrics: ImageMetrics) -> str:
        return (
            f'Health Score {metrics.health_score}/100 derived from green coverage, '
            f'disease region percentage, and leaf texture edge density.'
        )
