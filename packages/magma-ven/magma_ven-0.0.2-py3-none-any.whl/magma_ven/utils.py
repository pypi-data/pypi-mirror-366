import datetime
import json
import os
import re
from typing import Tuple

import numpy as np


def check_directory(current_dir: str) -> Tuple[str, str, str]:
    """Checking existing directory

    Args:
        current_dir (str): Current directory

    Returns:
        Tuple[str, str, str]: Directory name, directory path, and file path
    """
    output_dir = os.path.join(current_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    figures_dir = os.path.join(output_dir, "figures")
    os.makedirs(figures_dir, exist_ok=True)

    magma_dir = os.path.join(output_dir, "magma")
    os.makedirs(magma_dir, exist_ok=True)

    return output_dir, figures_dir, magma_dir


def save(filename: str, response: dict) -> str:
    """Save response to file

    Args:
        filename (str): Filename
        response (dict): Response

    Returns:
        str: Saved response location
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(response, f, ensure_ascii=False, indent=4)

    return filename


def activity_level(level: str) -> int:
    """Transform activity text into level.

    Args:
        level (str): Level Activity text. Eg: Level I (Normal), Level II (Waspada)

    Returns:
        int: Level
    """
    if "IV" in level:
        return 4
    if "III" in level:
        return 3
    if "II" in level:
        return 2
    return 1


def translate_ash_color(color: str) -> str:
    """Translate ash color

    Args:
        color (str): Color

    Returns:
        color (str): Translated color
    """
    color = (
        color.replace("putih", "white")
        .replace("kelabu", "gray")
        .replace("coklat", "brown")
        .replace("hitam", "black")
    )

    return color


def translate_intensity(intensity: str) -> str:
    """Translate ash intensity

    Args:
        intensity (str): Intensity

    Returns:
        str: Translated intensity
    """
    intensity = (
        intensity.replace("tipis", "thin")
        .replace("sedang", "medium")
        .replace("tebal", "thick")
    )

    return intensity


def translate_wind_direction(wind_direction: str) -> str:
    """Translate wind direction

    Args:
        wind_direction (str): Wind direction

    Returns:
        str: Translated wind direction
    """
    wind_direction = (
        wind_direction.replace("utara", "north")
        .replace("timur laut", "northeast")
        .replace("barat daya", "southwest")
        .replace("barat laut", "northwest")
        .replace("timur", "east")
        .replace("tenggara", "southeast")
        .replace("selatan", "south")
        .replace("barat", "west")
    )

    return wind_direction


def ash_directions_text(directions: str) -> str:
    """Transform ash directions

    Args:
        directions (str): Ash directions separated by ", "

    Returns:
        str: Ash directions text
    """
    directions = directions.split(", ")

    if len(directions) == 1:
        return directions[0]

    if len(directions) == 2:
        return directions[0] + " and " + directions[1]

    length = len(directions)

    _directions = directions[0]
    for i in range(length):
        if i == 0:
            continue

        if i == length - 1:
            _directions = f"{_directions}, and {directions[i]}"

        _directions = f"{_directions}, {directions[i]}"

    return _directions


def translate_visual_description(
    volcano_name: str,
    volcano_height: int | float,
    iso_datetime: str,
    extracted_description: dict,
) -> str:
    """Translate visual description

    Args:
        volcano_name (str): Volcano name
        iso_datetime (str): Datetime of eruption
        volcano_height (int): Volcano height in meter
        extracted_description (dict): Extracted description including
                    'column_height','ash_color','ash_intensity','ash_direction'

    Returns:
        str: Translated visual description in english
    """
    column_height = extracted_description["column_height"]

    local_datetime = datetime.datetime.fromisoformat(iso_datetime)
    local_datetime_str = local_datetime.strftime("%A, %B %d, %Y, at %H:%M %Z")

    column_height_above_sea_level = (
        column_height + volcano_height if column_height > 0 else None
    )

    ash_observed = (
        (
            f"with an ash column observed reaching {column_height} meters above the summit "
            f"({column_height_above_sea_level} meters above sea level)"
        )
        if column_height > 0
        else "the eruption was not visually observed."
    )

    if column_height is np.nan:
        return f"An eruption of Mt. {volcano_name} occurred on {local_datetime_str}, {ash_observed}."

    ash_colors = extracted_description["ash_color"].split(", ")
    ash_colors_text = (
        ash_colors[0] if len(ash_colors) == 1 else f"{ash_colors[0]} to {ash_colors[1]}"
    )

    ash_intensities = extracted_description["ash_intensity"].split(", ")
    ash_intensities_text = (
        ash_intensities[0]
        if len(ash_intensities) == 1
        else f"{ash_intensities[0]} to {ash_intensities[1]}"
    )

    ash_direction = ash_directions_text(extracted_description["ash_direction"])
    ash_information = (
        f"The ash column was observed to be {ash_colors_text} in color, "
        f"with {ash_intensities_text} intensity, heading toward the {ash_direction}"
    )

    description = f"An eruption of Mt. {volcano_name} occurred on {local_datetime_str}, {ash_observed}. {ash_information}."

    return description


def extract_eruption_data(text: str, locale: str = "id") -> dict:
    """Extract eruption data

    Args:
        text (str): Text to extract
        locale (str, optional): Locale. Defaults to "id".

    Returns:
        dict: Extracted data
    """
    locale = locale.lower()

    if "Visual letusan tidak teramati" in text:
        return {
            "column_height": np.nan,
            "ash_color": None,
            "ash_intensity": None,
            "ash_direction": None,
        }

    text = text.replace("&plusmn; ", "")

    column_height = re.search(r"tinggi kolom abu teramati (\d+)\s*m", text)
    column_height = float(column_height.group(1)) if column_height else np.nan

    ash_color = re.search(r"berwarna ([\w\s]+?) dengan", text)
    ash_intensity = re.search(r"dengan intensitas (\w+)", text)
    ash_direction = re.search(r"ke arah ([\w\s]+)[.,]", text)

    if ash_color is not None:
        ash_color = ash_color.group(1).replace(" hingga ", ", ")
        ash_color = translate_ash_color(ash_color) if locale == "en" else ash_color

    if ash_intensity is not None:
        ash_intensity = ash_intensity.group(1).replace(" hingga ", ", ")
        ash_intensity = (
            translate_intensity(ash_intensity) if locale == "en" else ash_intensity
        )

    if ash_direction is not None:
        ash_direction = ash_direction.group(1).replace(" dan ", ", ")
        ash_direction = (
            translate_wind_direction(ash_direction) if locale == "en" else ash_direction
        )

    data = {
        "column_height": column_height,
        "ash_color": ash_color,
        "ash_intensity": ash_intensity,
        "ash_direction": ash_direction,
    }

    return data


def extract_instrument_data(text: str, locale: str = "id") -> dict:
    """Extract instrument data

    Args:
        text (str): Text to extract
        locale (str, optional): Locale. Defaults to "id".

    Returns:
        dict: Extracted data
    """
    locale = locale.lower()

    amplitude = re.search(r"amplitudo maksimum (\d+)\s*mm", text)
    amplitude = float(amplitude.group(1)) if amplitude else np.nan

    duration = re.search(r"durasi (\d+)\s*detik", text)
    duration = float(duration.group(1)) if duration else np.nan

    if locale == "en":
        text = (
            f"This eruption was recorded on a seismograph with a maximum amplitude of "
            f"{amplitude} mm and a duration of {duration} seconds."
        )

    data = {
        "amplitude": amplitude,
        "duration": duration,
        "description": text if amplitude > 0.0 else None,
    }

    return data
