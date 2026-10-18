import pandas as pd
import io

class UzumExcelExporter:
    """
    Uzum Seller ommaviy yuklash (mass upload) uchun Excel faylini yaratadi.
    Uzumning standart andozasiga mos keladi.
    """

    @staticmethod
    def create_excel(card_data: dict) -> io.BytesIO:
        """
        Berilgan kartochka ma'lumotlari asosida Uzum Seller uchun Excel fayl yaratadi.
        """
        # Uzum Seller uchun minimal ustunlar (standart template asosida)
        data = {
            "Наименование": [card_data.get("title_ru")],
            "Наименование (уз)": [card_data.get("title_uz")],
            "Описание": [card_data.get("description_ru")],
            "Описание (уз)": [card_data.get("description_uz")],
            "Цена": [card_data.get("price", 0)],
            "Категория": [card_data.get("category_suggestion")],
            "Бренд": ["Generic"], # Standart qiymat
            "Страна производства": [card_data.get("attributes", {}).get("Ishlab chiqarilgan mamlakat", "Китай")],
            "Цвет": [card_data.get("attributes", {}).get("Rang", "-")],
            "Материал": [card_data.get("attributes", {}).get("Material", "-")]
        }

        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Товары')

        output.seek(0)
        return output
