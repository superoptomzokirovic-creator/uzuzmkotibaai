import asyncio
import httpx
from datetime import datetime
from typing import Dict, Any

class CurrencyService:
    """Markaziy Bank API orqali valyuta kurslarini (CNY, USD) olib keladi."""

    CBU_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"
    _cache: Dict[str, Any] = {"rates": {}, "timestamp": None}

    @classmethod
    async def get_rates(cls) -> Dict[str, float]:
        now = datetime.now()
        # Agar kesh so'nggi 1 soat ichida olingan bo'lsa, undan foydalanamiz
        if cls._cache["timestamp"] and (now - cls._cache["timestamp"]).seconds < 3600 and cls._cache["rates"]:
            return cls._cache["rates"]

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(cls.CBU_URL)
                if response.status_code == 200:
                    data = response.json()
                    rates = {}
                    for item in data:
                        if item["Ccy"] in ["USD", "CNY"]:
                            rates[item["Ccy"]] = float(item["Rate"])

                    if rates:
                        cls._cache["rates"] = rates
                        cls._cache["timestamp"] = now
                        return rates
        except Exception:
            pass

        # Fallback standart kurslar (agar tarmoq ishlamasa)
        return {"USD": 12800.0, "CNY": 1780.0}


class CostCalculator:
    """Xitoydan tovar olib kelish va Uzumda sotish tannarxini deterministik hisoblaydi."""

    @staticmethod
    def calculate_item_cost(
        unit_price_cny: float,
        quantity: int,
        weight_kg: float,
        cargo_rate_per_kg: float,
        cny_rate: float,
        uzum_commission_percent: float,
        packaging_cost_uzs: float = 0.0
    ) -> Dict[str, float]:
        """
        Tannarx va foydani aniq hisoblash (AI aralashmaydi, sof Python arifmetikasi).
        """
        # Tovarning so'mdagi narxi
        total_item_cny = unit_price_cny * quantity
        total_item_uzs = total_item_cny * cny_rate

        # Kargo xarajati (so'mda)
        total_weight = weight_kg * quantity
        total_cargo_uzs = total_weight * cargo_rate_per_kg

        # Umumiy tannarx
        total_investment = total_item_uzs + total_cargo_uzs + (packaging_cost_uzs * quantity)
        unit_cost_uzs = total_investment / quantity if quantity > 0 else 0

        return {
            "total_item_uzs": round(total_item_uzs, 2),
            "total_cargo_uzs": round(total_cargo_uzs, 2),
            "total_investment": round(total_investment, 2),
            "unit_cost_uzs": round(unit_cost_uzs, 2)
        }
