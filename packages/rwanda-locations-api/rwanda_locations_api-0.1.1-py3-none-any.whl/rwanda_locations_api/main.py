from fastapi import FastAPI
from .locs import get_location_data

app = FastAPI()

locations = get_location_data()

@app.get("/")
def root():
    return {"message": "Rwanda Locations API"}

@app.get("/provinces")
def list_provinces():
    return list(locations.keys())

@app.get("/districts/{province}")
def list_districts(province: str):
    return list(locations.get(province.capitalize(), {}).keys())

@app.get("/sectors/{province}/{district}")
def list_sectors(province: str, district: str):
    return list(locations.get(province.capitalize(), {}).get(district.capitalize(), {}).keys())

@app.get("/cells/{province}/{district}/{sector}")
def list_cells(province: str, district: str, sector: str):
    return list(locations.get(province.capitalize(), {}).get(district.capitalize(), {}).get(sector.capitalize(), {}).keys())

@app.get("/villages/{province}/{district}/{sector}/{cell}")
def list_villages(province: str, district: str, sector: str, cell: str):
    return locations.get(province.capitalize(), {}).get(district.capitalize(), {}).get(sector.capitalize(), {}).get(cell.capitalize(), [])
