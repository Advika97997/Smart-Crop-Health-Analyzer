from __future__ import annotations

from database.repositories import AnalysisRepository


class DashboardService:
    @staticmethod
    def get_summary():
        return AnalysisRepository.get_dashboard_summary()

    @staticmethod
    def get_status_distribution():
        return AnalysisRepository.get_status_distribution()

    @staticmethod
    def get_crop_distribution():
        return AnalysisRepository.get_crop_distribution()

    @staticmethod
    def get_recent_uploads():
        return AnalysisRepository.get_recent(6)
