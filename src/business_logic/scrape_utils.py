import logging
import os
import re
import time

import requests
from RPA.Excel.Files import Files

from src.dtos.news_item_dto import NewsItemDto

logger = logging.getLogger(__name__)


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/107.0.0.0 Safari/537.36"
)


def download_image(image_url: str, image_folder_path: str, title: str) -> str:
    """Downloads an image and save it to a specified folder and return the image file name"""
    os.makedirs(image_folder_path, exist_ok=True)
    headers = {"User-Agent": USER_AGENT}
    image_response = requests.get(image_url, headers=headers)
    counter = 1

    if image_response.status_code == 200:
        image_name = _sanitize_string(title)
        image_file_path = f"{image_folder_path}/{image_name}.jpg"

        # Note: For optimization, we could first check if the file exists and skip the download if we already have it.
        while os.path.exists(image_file_path):
            image_file_path = f"{image_folder_path}/{image_name}_{counter}.jpg"
            counter += 1

        image_data = image_response.content
        with open(image_file_path, "wb") as image_file:
            image_file.write(image_data)
    else:
        image_name = "An error occurred while downloading the image. Please retry."
        logger.error("An error occurred when downloading image from url: %s", image_url)

    return image_name


def _sanitize_string(value: str) -> str:
    """Sanitize a string and remove all special characters"""
    return re.sub(r"[^A-Za-z0-9 ]+", "", value).replace(" ", "").strip()


def save_news_to_excel(
    file_name: str, file_path: str, news_items: list[NewsItemDto], search_phrase: str
) -> None:
    """Saves the news items to an excel document"""
    results_path = f"{file_path}/{file_name}"
    if os.path.exists(f"{results_path}.xlsx"):
        existing_file_creation_time = time.ctime(
            os.path.getctime(f"{results_path}.xlsx")
        )
        os.rename(
            f"{results_path}.xlsx", f"{results_path}_{existing_file_creation_time}.xlsx"
        )

    os.makedirs(file_path, exist_ok=True)
    excel = Files()
    excel.create_workbook()
    excel_data = []
    header_data = [
        "title",
        "date",
        "description",
        "picture filename",
        "count of search phrase",
        "news contains money",
    ]
    excel_data.append(header_data)

    for news_item in news_items:
        excel_data.append(
            [
                news_item.title,
                str(news_item.date),
                news_item.description,
                news_item.image_name,
                str(news_item.phrase_count_in_title_and_description(search_phrase)),
                str(news_item.title_or_description_contains_money()),
            ]
        )

    for row_index, row_data in enumerate(excel_data):
        for col_index, value in enumerate(row_data, start=1):
            excel.set_cell_value(row_index + 1, col_index, value)

    excel.save_workbook(f"{results_path}.xlsx")
    excel.close_workbook()
