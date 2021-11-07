"""
Run this file as

python -m demo
"""


import trickortreat.app
import trickortreat.attom
import trickortreat.geocoding
import trickortreat.path

location = "15 E Lane Ave, Columbus OH 43201"
radius = 0.2

lat, long = trickortreat.geocoding.lat_long(location)

areacodes = trickortreat.attom.area_codes(lat, long)

breakpoint()

properties, assessments = trickortreat.attom.all_in_radius(lat, long, radius)

houses = [
    trickortreat.app.House.from_property(p, a)
    for p, a in zip(properties, assessments)
    if trickortreat.app.House.is_house(p)
]
