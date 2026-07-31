# New Zealand Geographic & Emergency Service Reference Data

This repository contains comprehensive datasets detailing New Zealand (Aotearoa) geographic entities compiled specifically for emergency services research, disaster response mapping, and geographic reference testing.

The datasets are split into clean, structured Markdown tables containing names (both English and Māori where applicable), latitude/longitude coordinates, administrative provinces (regions), and their associated NZ Police Districts.

---

## Directory and Data Structure

To ensure the highest accuracy and avoid token limitation issues, the reference data is broken down into specific directories and subfiles:

1. **Category 1: Towns and Cities** (`data/towns_cities/`)
   - [Towns and Cities A-G](data/towns_cities/towns_a_g.md)
   - [Towns and Cities H-N](data/towns_cities/towns_h_n.md)
   - [Towns and Cities O-Z](data/towns_cities/towns_o_z.md)

2. **Category 2: Provinces / Regions** (`data/provinces/`)
   - [Provinces & Regions](data/provinces/provinces_regions.md)

3. **Category 3: Roadways** (`data/roadways/`)
   - [State Highways](data/roadways/state_highways.md)
   - [Urban Arterials](data/roadways/urban_arterials.md)

4. **Category 4: Waterways** (`data/waterways/`)
   - [Major Lakes](data/waterways/lakes.md)
   - [Rivers and Harbors](data/waterways/rivers_harbors.md)

5. **Category 5: Landmarks** (`data/landmarks/`)
   - [Natural Landmarks](data/landmarks/natural_landmarks.md)
   - [Built & Cultural Landmarks](data/landmarks/built_cultural.md)

6. **Category 6: Police Districts** (`data/police_districts/`)
   - [Police Districts](data/police_districts/police_districts.md)

---

## Fields/Schema Details

Each dataset is organized according to the following fields to facilitate programmatic parsing and ingestion:
- **English Name**: The standard English/common name of the entity.
- **Māori Name**: The official or traditional Māori name (te reo Māori) of the entity where applicable (`-` or empty if none).
- **Latitude / Longitude**: WGS84 coordinates for accurate spatial mapping (decimal format).
- **Province (Region)**: The regional council territory/unitary authority area that the entity resides within.
- **Police District**: The active New Zealand Police District responsible for the area.

---

## High-Level Summary of NZ Police Districts

| District Name | Māori Name Representation | Headquarters / Central Station | Latitude | Longitude | Covered Provinces / Regions |
|---|---|---|---|---|---|
| **Northland** | Te Tai Tokerau | Whangārei | -35.7250 | 174.3236 | Northland |
| **Waitematā** | Waitematā | Henderson | -36.8583 | 174.6281 | Auckland |
| **Auckland City** | Tāmaki Makaurau | Auckland (College Hill) | -36.8485 | 174.7633 | Auckland |
| **Counties Manukau** | Counties Manukau | Manukau | -37.0000 | 174.8833 | Auckland |
| **Waikato** | Waikato | Hamilton | -37.7870 | 175.2793 | Waikato |
| **Bay of Plenty** | Toi Moana | Rotorua | -38.1368 | 176.2497 | Bay of Plenty |
| **Eastern** | Te Tai Rāwhiti | Napier | -39.4928 | 176.9120 | Gisborne, Hawke's Bay |
| **Central** | Central | Palmerston North | -40.3523 | 175.6082 | Taranaki, Manawatū-Whanganui |
| **Wellington** | Te Upoko o te Ika | Wellington | -41.2865 | 174.7762 | Wellington, Chatham Islands |
| **Tasman** | Tasman | Nelson | -41.2706 | 173.2840 | Tasman, Nelson, Marlborough, West Coast |
| **Canterbury** | Canterbury | Christchurch | -43.5321 | 172.6362 | Canterbury |
| **Southern** | Southern | Dunedin | -45.8788 | 170.5028 | Otago, Southland |

---

## Technical/Parsing Verification

You can verify the format and parse the files using standard Markdown tools or convert them into CSV format. For example, to read the first few rows of the Towns & Cities dataset using Python:

```python
import pandas as pd
import io

def parse_markdown_table(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Filter lines to locate the table
    table_lines = [line for line in lines if '|' in line]
    if len(table_lines) < 2:
        return None

    # Clean and load to DataFrame
    raw_data = "".join(table_lines)
    df = pd.read_csv(io.StringIO(raw_data), sep="|", skipinitialspace=True).dropna(how='all', axis=1)
    df.columns = [c.strip() for c in df.columns]
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    return df.iloc[1:] # Skip separator row

# Example usage
df_cities = parse_markdown_table('data/towns_cities/towns_a_g.md')
print(df_cities.head())
```

All coordinate data was validated against standard geocoding reference sources to ensure coordinates fall precisely within New Zealand territory bounds.
