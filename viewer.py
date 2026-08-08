import glob
import os
import re
import geopandas as gpd
import matplotlib.pyplot as plt
import mplcursors

# 1. Parse markdown files
md_files = glob.glob("./**/*.md", recursive=True)

pts_x, pts_y, pt_labels, pt_colors = [], [], [], []
line_artists = []
line_labels = []

COLOR_SCHEME = {
    "towns_cities": "#e74c3c",  # Red dots
    "natural_landmarks": "#2ecc71",  # Green dots
    "built_cultural": "#9b59b6",  # Purple dots
    "lakes": "#3498db",  # Light Blue dots
    "rivers_harbors": "#1b4f72",  # Dark Blue lines
    "roadways": "#f39c12",  # Orange lines
}


def parse_lat_lon(val_str):
    if not val_str or val_str in ["-", "None"]:
        return []
    matches = re.findall(r"(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)", val_str)
    return [(float(m[0]), float(m[1])) for m in matches]


for fpath in md_files:
    if "README" in fpath:
        continue

    category = fpath.split("/")[-2] if "/" in fpath else "other"
    subcat = os.path.basename(fpath).replace(".md", "")

    if category in ["provinces", "police_districts"]:
        continue

    with open(fpath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    headers = None
    for line in lines:
        line_str = line.strip()
        if not line_str.startswith("|"):
            continue
        cols = [c.strip() for c in line_str.split("|")[1:-1]]

        if (
            "Name" in cols[0]
            or "English Name" in cols[0]
            or "District Name" in cols[0]
        ):
            headers = cols
            continue
        if cols[0].startswith("---") or cols[0].startswith(":-"):
            continue

        if headers:
            item = dict(zip(headers, cols))

            name = (
                item.get("English Name")
                or item.get("District Name")
                or item.get("Name")
                or "Unknown"
            )
            maori = (
                item.get("Māori Name")
                or item.get("Māori Name Representation")
                or ""
            )
            title = (
                f"{name} ({maori})" if maori and maori != "-" else name
            )

            province = (
                item.get("Province")
                or item.get("Province(s)")
                or item.get("Province (Region)")
                or ""
            )
            district = (
                item.get("Police District")
                or item.get("Police District(s)")
                or item.get("Primary Police District(s)")
                or ""
            )

            location_meta = []
            if province and province != "-":
                location_meta.append(f"Prov: {province}")
            if district and district != "-":
                location_meta.append(f"Dist: {district}")

            meta_str = (
                f"\n[{', '.join(location_meta)}]" if location_meta else ""
            )
            full_label = f"{title}{meta_str}"

            # Point Features (Towns, Landmarks, Lakes)
            if "Latitude" in item and "Longitude" in item:
                try:
                    lat = float(
                        re.search(r"-?\d+\.\d+", item["Latitude"]).group()
                    )
                    lon = float(
                        re.search(r"\d+\.\d+", item["Longitude"]).group()
                    )
                    c_key = subcat if subcat in COLOR_SCHEME else category
                    pts_x.append(lon)
                    pts_y.append(lat)
                    pt_labels.append(full_label)
                    pt_colors.append(COLOR_SCHEME.get(c_key, "#7f8c8d"))
                except Exception:
                    pass

            # Line Features (Roadways & Rivers)
            elif category in ["roadways", "waterways"]:
                coords = []
                for key in [
                    "Start Coordinates",
                    "Mid Coordinates",
                    "End Coordinates",
                ]:
                    if key in item and item[key]:
                        coords.extend(parse_lat_lon(item[key]))

                if len(coords) >= 2:
                    lons = [c[1] for c in coords]
                    lats = [c[0] for c in coords]
                    color = (
                        COLOR_SCHEME["roadways"]
                        if category == "roadways"
                        else COLOR_SCHEME["rivers_harbors"]
                    )

                    # Create line plot
                    (line_art,) = plt.plot(
                        lons,
                        lats,
                        color=color,
                        alpha=0.75,
                        linewidth=2,
                        zorder=3,
                    )
                    line_artists.append(line_art)
                    line_labels.append(full_label)

# Setup Figure
fig, ax = plt.subplots(figsize=(9, 12))

# 2. Draw NZ Country Outline (Background)
try:
    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    nz_shape = world[world.name == "New Zealand"]
    nz_shape.plot(
        ax=ax, color="#eaeaea", edgecolor="#b0b0b0", linewidth=0.8, zorder=1
    )
except Exception:
    ax.set_facecolor("#f4f4f4")

# Draw Scatter Points
sc = ax.scatter(
    pts_x,
    pts_y,
    c=pt_colors,
    s=35,
    alpha=0.9,
    edgecolors="black",
    linewidth=0.4,
    zorder=4,
)

ax.set_title(
    "New Zealand Geography (Interactive Paths & Points)", fontsize=12
)
ax.set_aspect("equal")
ax.grid(True, linestyle=":", alpha=0.3)

# 3. Attach Hover Cursor to BOTH Scatter Points and Line Artists
all_targets = [sc] + line_artists
cursor = mplcursors.cursor(all_targets, hover=True)


@cursor.connect("add")
def on_add(sel):
    if sel.artist == sc:
        sel.annotation.set_text(pt_labels[sel.index])
    else:
        # Find index for the line artist hovered over
        idx = line_artists.index(sel.artist)
        sel.annotation.set_text(line_labels[idx])

    sel.annotation.get_bbox_patch().set(fc="white", alpha=0.95, boxstyle="round")


plt.show()
