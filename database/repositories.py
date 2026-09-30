from __future__ import annotations

from core.helpers import hash_password
from database.db import execute, fetch_all, fetch_one


class UserRepository:
    @staticmethod
    def authenticate(username: str, password: str):
        query = '''
            SELECT user_id, username, full_name, role
            FROM users
            WHERE username = %s AND password_hash = %s
        '''
        return fetch_one(query, (username, hash_password(password)), dictionary=True)


class CropRepository:
    @staticmethod
    def get_all():
        return fetch_all(
            '''
            SELECT crop_id, crop_name, species, created_at
            FROM crops
            ORDER BY crop_name
            ''',
            dictionary=True,
        )

    @staticmethod
    def get_name_map():
        rows = fetch_all(
            '''
            SELECT crop_id, crop_name
            FROM crops
            ORDER BY crop_name
            ''',
            dictionary=True,
        )
        return {row['crop_name']: row['crop_id'] for row in rows}

    @staticmethod
    def insert(crop_name: str, species: str):
        return execute(
            '''
            INSERT INTO crops (crop_name, species)
            VALUES (%s, %s)
            ''',
            (crop_name, species),
        )

    @staticmethod
    def update(crop_id: int, crop_name: str, species: str):
        execute(
            '''
            UPDATE crops
            SET crop_name=%s, species=%s
            WHERE crop_id=%s
            ''',
            (crop_name, species, crop_id),
        )

    @staticmethod
    def delete(crop_id: int):
        execute(
            '''
            DELETE FROM crops
            WHERE crop_id=%s
            ''',
            (crop_id,),
        )


class FarmerRepository:
    @staticmethod
    def get_all():
        return fetch_all(
            '''
            SELECT farmer_id, full_name, location, phone, farm_size, crop_focus, joined_date
            FROM farmers
            ORDER BY full_name
            ''',
            dictionary=True,
        )

    @staticmethod
    def insert(full_name: str, location: str, phone: str, farm_size: float, crop_focus: str):
        return execute(
            '''
            INSERT INTO farmers (full_name, location, phone, farm_size, crop_focus)
            VALUES (%s, %s, %s, %s, %s)
            ''',
            (full_name, location, phone, farm_size, crop_focus),
        )

    @staticmethod
    def update(
        farmer_id: int,
        full_name: str,
        location: str,
        phone: str,
        farm_size: float,
        crop_focus: str,
    ):
        execute(
            '''
            UPDATE farmers
            SET full_name=%s, location=%s, phone=%s, farm_size=%s, crop_focus=%s
            WHERE farmer_id=%s
            ''',
            (full_name, location, phone, farm_size, crop_focus, farmer_id),
        )

    @staticmethod
    def delete(farmer_id: int):
        execute(
            '''
            DELETE FROM farmers
            WHERE farmer_id=%s
            ''',
            (farmer_id,),
        )


class AnalysisRepository:
    @staticmethod
    def save_image(crop_id: int, image_path: str):
        return execute(
            '''
            INSERT INTO images (crop_id, image_path)
            VALUES (%s, %s)
            ''',
            (crop_id, image_path),
        )

    @staticmethod
    def save_result(
        image_id: int,
        health_status: str,
        health_score: float,
        green_pct: float,
        disease_pct: float,
        edge_density: float,
        advice: str,
        notes: str,
    ):
        return execute(
            '''
            INSERT INTO analysis_results
            (
                image_id,
                health_status,
                health_score,
                green_percentage,
                disease_area_percentage,
                edge_density,
                advice,
                notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''',
            (
                image_id,
                health_status,
                health_score,
                green_pct,
                disease_pct,
                edge_density,
                advice,
                notes,
            ),
        )

    @staticmethod
    def get_all(filter_text: str = '', crop_name: str = ''):
        base_query = '''
            SELECT
                r.result_id,
                c.crop_name,
                i.image_path,
                r.health_status,
                r.health_score,
                r.green_percentage,
                r.disease_area_percentage,
                r.edge_density,
                r.advice,
                r.notes,
                r.analyzed_on
            FROM analysis_results r
            JOIN images i ON r.image_id = i.image_id
            JOIN crops c ON i.crop_id = c.crop_id
        '''

        conditions = []
        params = []

        if filter_text:
            needle = f'%{filter_text}%'
            conditions.append('''
                (
                    c.crop_name LIKE %s
                    OR r.health_status LIKE %s
                    OR i.image_path LIKE %s
                    OR COALESCE(r.notes, '') LIKE %s
                )
            ''')
            params.extend([needle, needle, needle, needle])

        if crop_name and crop_name != 'All Crops':
            conditions.append('c.crop_name = %s')
            params.append(crop_name)

        if conditions:
            base_query += ' WHERE ' + ' AND '.join(conditions)

        base_query += ' ORDER BY r.analyzed_on DESC'
        return fetch_all(base_query, tuple(params), dictionary=True)

    @staticmethod
    def get_one(result_id: int):
        return fetch_one(
            '''
            SELECT
                r.result_id,
                r.image_id,
                i.crop_id,
                c.crop_name,
                i.image_path,
                r.health_status,
                r.health_score,
                r.green_percentage,
                r.disease_area_percentage,
                r.edge_density,
                r.advice,
                r.notes,
                r.analyzed_on
            FROM analysis_results r
            JOIN images i ON r.image_id = i.image_id
            JOIN crops c ON i.crop_id = c.crop_id
            WHERE r.result_id = %s
            ''',
            (result_id,),
            dictionary=True,
        )

    @staticmethod
    def update_record(result_id: int, crop_id: int, notes: str, advice: str):
        row = fetch_one(
            '''
            SELECT image_id
            FROM analysis_results
            WHERE result_id=%s
            ''',
            (result_id,),
            dictionary=True,
        )

        if not row:
            return False

        image_id = row['image_id']

        execute(
            '''
            UPDATE images
            SET crop_id=%s
            WHERE image_id=%s
            ''',
            (crop_id, image_id),
        )

        execute(
            '''
            UPDATE analysis_results
            SET notes=%s, advice=%s
            WHERE result_id=%s
            ''',
            (notes, advice, result_id),
        )
        return True

    @staticmethod
    def delete(result_id: int):
        execute(
            '''
            DELETE FROM analysis_results
            WHERE result_id=%s
            ''',
            (result_id,),
        )

    @staticmethod
    def get_recent(limit: int = 6):
        return fetch_all(
            '''
            SELECT
                c.crop_name,
                r.health_status,
                r.health_score,
                r.analyzed_on
            FROM analysis_results r
            JOIN images i ON r.image_id = i.image_id
            JOIN crops c ON i.crop_id = c.crop_id
            ORDER BY r.analyzed_on DESC
            LIMIT %s
            ''',
            (limit,),
            dictionary=True,
        )

    @staticmethod
    def get_dashboard_summary():
        row = fetch_one(
            '''
            SELECT
                COUNT(*) AS total_analyses,
                ROUND(COALESCE(AVG(health_score), 0), 2) AS avg_health_score,
                SUM(CASE WHEN health_status = 'Healthy' THEN 1 ELSE 0 END) AS healthy_count
            FROM analysis_results
            ''',
            dictionary=True,
        ) or {}

        total_crops = fetch_one(
            '''
            SELECT COUNT(*) AS total_crops
            FROM crops
            ''',
            dictionary=True,
        ) or {}

        total_farmers = fetch_one(
            '''
            SELECT COUNT(*) AS total_farmers
            FROM farmers
            ''',
            dictionary=True,
        ) or {}

        row.update(total_crops)
        row.update(total_farmers)
        return row

    @staticmethod
    def get_status_distribution():
        rows = fetch_all(
            '''
            SELECT health_status, COUNT(*) AS total
            FROM analysis_results
            GROUP BY health_status
            ''',
            dictionary=True,
        )
        return {row['health_status']: row['total'] for row in rows}

    @staticmethod
    def get_crop_distribution():
        rows = fetch_all(
            '''
            SELECT
                c.crop_name,
                COUNT(r.result_id) AS total
            FROM crops c
            LEFT JOIN images i ON c.crop_id = i.crop_id
            LEFT JOIN analysis_results r ON i.image_id = r.image_id
            GROUP BY c.crop_name
            ORDER BY total DESC, c.crop_name
            ''',
            dictionary=True,
        )
        return {row['crop_name']: row['total'] for row in rows}