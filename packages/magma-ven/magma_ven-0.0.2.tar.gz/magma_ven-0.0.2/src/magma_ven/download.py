import json
import os
from typing import Self

import pandas as pd
import requests
from pandas.errors import EmptyDataError

import magma_ven
from magma_ven.const import URL_FILTER
from magma_ven.magma_ven import MagmaVen
from magma_ven.utils import (
    activity_level,
    extract_eruption_data,
    extract_instrument_data,
    save,
    translate_visual_description,
)


class Download(MagmaVen):
    def __init__(
        self,
        token: str,
        volcano_code: str,
        start_date: str,
        end_date: str,
        current_dir: str = None,
        locale: str = "id",
        url_filter: str = None,
        verbose: bool = False,
        debug: bool = False,
    ):
        super().__init__(
            volcano_code, start_date, end_date, current_dir, verbose, debug
        )

        self.dates = f"{start_date}_{end_date}"

        self.token = token
        self.headers: dict[str, str] = {}
        self.json_dir = os.path.join(self.ven_dir, "json")
        self.page_dir = os.path.join(self.json_dir, "pages", volcano_code, self.dates)
        self.daily_dir = os.path.join(self.json_dir, "daily", volcano_code)
        self.files: list[str] = []
        self.locale = locale
        self.url_filter = url_filter or URL_FILTER

        self.excel_dir = os.path.join(self.ven_dir, "excel", volcano_code, self.dates)
        self.csv_dir = os.path.join(self.ven_dir, "csv", volcano_code, self.dates)
        self.data = []

        print(f"Version: {magma_ven.__version__}")

    @property
    def df(self) -> pd.DataFrame:
        assert len(self.files) > 1, FileNotFoundError(
            f"❌ JSON per pages not found. Please download first."
        )

        os.makedirs(self.daily_dir, exist_ok=True)

        for file in self.files:
            response = json.load(open(file))
            for _data in response["data"]:
                data = {}
                extracted = extract_eruption_data(
                    _data["deskripsi"]["visual"], locale=self.locale
                )

                extracted_instrument = extract_instrument_data(
                    _data["deskripsi"]["instrumental"], locale=self.locale
                )

                column_height = extracted["column_height"]

                visual_description = _data["deskripsi"]["visual"]

                visual_description = (
                    translate_visual_description(
                        volcano_name=_data["nama_gunung_api"],
                        volcano_height=_data["elevation"],
                        iso_datetime=_data["iso_datetime"],
                        extracted_description=extracted,
                    )
                    if self.locale == "en"
                    else visual_description
                )

                data["ven_id"] = _data["id"]
                data["volcano_code"] = _data["code_ga"]
                data["volcano_name"] = _data["nama_gunung_api"]
                data["local_datetime"] = _data["local_datetime"]
                data["local_time_zone"] = _data["time_zone"]
                data["iso_datetime"] = _data["iso_datetime"]
                data["level"] = activity_level(_data["tingkat_aktivitas"])
                data["visually_observed"] = column_height > 0
                data["continuing_eruption"] = extracted_instrument["amplitude"] == 0
                data["column_height"] = column_height
                data["column_height_above_sea_level"] = (
                    column_height + _data["elevation"]
                )
                data["ash_color"] = extracted["ash_color"]
                data["ash_intensity"] = extracted["ash_intensity"]
                data["ash_direction"] = extracted["ash_direction"]
                data["max_amplitude_mm"] = extracted_instrument["amplitude"]
                data["duration_second"] = extracted_instrument["duration"]
                data["photo"] = _data["foto"] if column_height > 0 else None
                data[f"eruption_description_{self.locale}"] = visual_description
                data[f"instrument_description_{self.locale}"] = extracted_instrument[
                    "description"
                ]
                data["recommendation_id"] = _data["rekomendasi"]
                data["reported_by"] = _data["pelapor"]
                data["source"] = _data["share"]["url"]

                self.data.append(data)

        return pd.DataFrame(self.data)

    def download(self, params: dict = None) -> dict:
        """Download Volcanic Eruption Notice (VEN).

        Args:
            params (dict): code, start_date, and end_date.

        Returns:
            dict
        """

        if len(self.headers.keys()) == 0:
            raise ValueError(f"❌ Headers not found.")

        payload: str = json.dumps(
            {
                "code": self.volcano_code.upper(),
                "start_date": self.start_date,
                "end_date": self.end_date,
            }
        )

        try:
            response = requests.request(
                "GET",
                self.url_filter,
                headers=self.headers,
                data=payload,
                params=params,
            )

            success = response.ok
            response = response.json()

            if not success or "errors" in response.keys():
                raise ValueError(f'❌ Download Error :: {response["errors"]}')

            keys = ["data", "links", "meta"]

            for key in keys:
                if key not in response.keys():
                    raise KeyError(f"❌ '{key}' not found in response :: {response}")

            if len(response["data"]) == 0:
                raise ValueError(
                    f"❌ No data found for {self.volcano_code} :: {response}"
                )

            return response
        except Exception as e:
            raise ValueError(f"❌ Failed to download JSON :: {e}")

    def download_per_page(self, response: dict) -> list[str]:
        """Download Volcanic Eruption Notice (VEN) per page.

        Args:
            response (dict): Volcanic Eruption Notice response.

        Returns:
            list[str]
        """
        pages: list[str] = []
        last_page = response["meta"]["last_page"]

        if last_page == 1:
            pass

        if self.verbose:
            print(f"ℹ️ Downloading from page 2 to {last_page}")
            print("=" * 60)

        for page in range(2, last_page + 1):
            # code_startDate_endDate_page.json
            # example: AWU_2025-01-01_2025-01-31_1.json
            filename = f"{self.filename}_{page}.json"
            json_per_page = os.path.join(self.page_dir, filename)

            if os.path.exists(json_per_page):
                if self.verbose:
                    print(f"✅ Skip. JSON for page #{page} exists :: {json_per_page}")
                pages.append(json_per_page)
                continue

            response = self.download({"page": page})
            save(json_per_page, response)

            pages.append(json_per_page)

            if self.verbose:
                print(f"✅ JSON for page #{page} downloaded :: {json_per_page}")

        self.files = self.files + pages
        return pages

    def download_first_page(self, first_page_json: str = None) -> dict:
        """Download Volcanic Eruption Notice (VEN) first page.

        Args:
            first_page_json (str): First page JSON path.

        Returns:
            dict
        """
        os.makedirs(self.ven_dir, exist_ok=True)
        os.makedirs(self.json_dir, exist_ok=True)
        os.makedirs(self.page_dir, exist_ok=True)

        first_page_json = first_page_json or os.path.join(
            self.page_dir, f"{self.filename}_1.json"
        )

        if os.path.isfile(first_page_json):
            if self.verbose:
                print(f"✅ JSON First Page exists :: {first_page_json}")
            self.files.append(first_page_json)
            return json.load(open(first_page_json))

        if self.verbose:
            print(f"⌛ Downloading JSON First Page :: {first_page_json}")

        response = self.download()
        save(first_page_json, response)

        if self.verbose:
            total = response["meta"]["total"]
            print(f"ℹ️ Total Data :: {total}")
            print(f"✅ JSON First Page downloaded :: {first_page_json}")

        self.files.append(first_page_json)

        return response

    def ven(self, token: str = None) -> Self:
        """Get Volcanic Eruption Notice (VEN) API.

        Args:
            token (str, optional): MAGMA Token.

        Returns:
            MagmaVen
        """
        token = token or self.token
        self.headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        }

        response = self.download_first_page()
        self.download_per_page(response)

        if self.verbose:
            print("ℹ️ JSON Files :: ", len(self.files))

        return self

    def to_excel(self, output_path: str = None) -> str:
        """Convert Volcanic Eruption Notice (VEN) to Excel.

        Args:
            output_path (str, optional): Excel Output path.

        Returns:
            str: Excel Output path.
        """
        assert len(self.df) > 0, EmptyDataError(
            f"❌ Data not found. Try to redownload it once again"
        )

        if output_path is None:
            output_path = self.excel_dir
        os.makedirs(output_path, exist_ok=True)

        filename = f"{self.filename}.xlsx"
        filepath = os.path.join(output_path, filename)
        self.df.to_excel(filepath, index=False)

        return filepath

    def to_csv(self, output_path: str = None) -> str:
        """Convert Volcanic Eruption Notice (VEN) to Excel.

        Args:
            output_path (str, optional): CSV output path.

        Returns:
            str: CSV output path.
        """
        assert len(self.df) > 0, EmptyDataError(
            f"❌ Data not found. Try to redownload it once again"
        )

        if output_path is None:
            output_path = self.csv_dir
        os.makedirs(output_path, exist_ok=True)

        filename = f"{self.filename}.csv"
        filepath = os.path.join(output_path, filename)
        self.df.to_csv(filepath, index=False)

        return filepath
