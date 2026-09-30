from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


@dataclass
class ImageMetrics:
    green_pct: float
    disease_pct: float
    edge_density: float
    health_score: float
    status: str
    color: str


class ImageService:
    VIEW_MODES: Dict[str, str] = {
        'Enhanced': 'enhanced',
        'Grayscale': 'grayscale',
        'Edge Detection': 'edge',
        'Histogram Eq.': 'histogram',
        'Disease Highlight': 'disease',
    }

    @staticmethod
    def load_image(path: str, size=(300, 220)) -> Image.Image:
        img = Image.open(Path(path)).convert('RGB')
        return img.resize(size)

    @staticmethod
    def enhance_image(pil_img: Image.Image) -> Image.Image:
        img = ImageEnhance.Color(pil_img).enhance(1.12)
        img = ImageEnhance.Contrast(img).enhance(1.28)
        img = ImageEnhance.Sharpness(img).enhance(1.45)
        return img.filter(ImageFilter.SHARPEN)

    @staticmethod
    def grayscale(pil_img: Image.Image) -> Image.Image:
        return pil_img.convert('L').convert('RGB')

    @staticmethod
    def edge_detection(pil_img: Image.Image) -> Image.Image:
        arr = np.array(pil_img)
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 80, 160)
        return Image.fromarray(cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB))

    @staticmethod
    def histogram_equalization(pil_img: Image.Image) -> Image.Image:
        gray = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2GRAY)
        eq = cv2.equalizeHist(gray)
        return Image.fromarray(cv2.cvtColor(eq, cv2.COLOR_GRAY2RGB))

    @staticmethod
    def disease_highlight(pil_img: Image.Image) -> Image.Image:
        arr = np.array(pil_img)
        hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
        yellow_mask = cv2.inRange(hsv, np.array([15, 40, 40]), np.array([35, 255, 255]))
        brown_mask = cv2.inRange(hsv, np.array([5, 50, 20]), np.array([20, 255, 170]))
        mask = cv2.bitwise_or(yellow_mask, brown_mask)
        overlay = arr.copy()
        overlay[mask > 0] = [255, 0, 0]
        blended = cv2.addWeighted(arr, 0.78, overlay, 0.42, 0)
        return Image.fromarray(blended)

    @classmethod
    def process_for_view(cls, pil_img: Image.Image, view_name: str) -> Image.Image:
        mapping = {
            'Enhanced': cls.enhance_image,
            'Grayscale': cls.grayscale,
            'Edge Detection': cls.edge_detection,
            'Histogram Eq.': cls.histogram_equalization,
            'Disease Highlight': cls.disease_highlight,
        }
        return mapping.get(view_name, cls.enhance_image)(pil_img)

    @staticmethod
    def compute_metrics(pil_img: Image.Image) -> ImageMetrics:
        arr = np.array(pil_img)
        hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
        total_pixels = hsv.shape[0] * hsv.shape[1]

        green_mask = cv2.inRange(hsv, np.array([35, 35, 35]), np.array([90, 255, 255]))
        yellow_mask = cv2.inRange(hsv, np.array([15, 40, 40]), np.array([35, 255, 255]))
        brown_mask = cv2.inRange(hsv, np.array([5, 45, 15]), np.array([20, 255, 170]))
        disease_mask = cv2.bitwise_or(yellow_mask, brown_mask)

        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 70, 150)

        green_pct = round(float(np.sum(green_mask > 0)) / total_pixels * 100, 2)
        disease_pct = round(float(np.sum(disease_mask > 0)) / total_pixels * 100, 2)
        edge_density = round(float(np.sum(edges > 0)) / total_pixels * 100, 2)

        raw_score = green_pct - (0.65 * disease_pct) - (0.10 * edge_density)
        health_score = max(0.0, min(100.0, round(raw_score, 2)))

        if health_score >= 70:
            status, color = 'Healthy', '#2d936c'
        elif health_score >= 40:
            status, color = 'Mild Stress', '#e9a000'
        else:
            status, color = 'Diseased', '#c1121f'

        return ImageMetrics(
            green_pct=green_pct,
            disease_pct=disease_pct,
            edge_density=edge_density,
            health_score=health_score,
            status=status,
            color=color,
        )
