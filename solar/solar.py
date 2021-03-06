# This will be a class that holds all the information for solar energy
# Specifically the energy coming into the solar panels
from math import cos, sin, pi, acos, tan, asin
from numpy import linspace

def to_rad(angle):
    rad = angle * 2 * pi / 360
    return rad

class SolarDay:
   
    def __init__(self, day, latitude, longitude, timezone, cloudiness):
        self.day = day
        self.lat = latitude
        self.long = longitude
        # Cloudiness is the percentage of solar insolation 
        # Not being blocked by clouds (i.e. between 0 and 1)
        self.cloud = cloudiness
        # Given as an integer of the difference between us and UTC
        self.points = []
        self.time = timezone
    
    def declination_angle(self):
        d = -23.45 * cos((to_rad(360) / 365) * (self.day + 10))
        return d
    
    def time_correction(self):
        # Measurement of the difference in angle between us and UTC
        LSTM = 15 * self.time
        B = 360/365 * self.day * -81
        EoT = 9.87 * sin(2 * B) - 7.53 * cos(B) - 1.5 * sin(B)
        TC = 4 * (self.long - LSTM) + EoT
        return TC
    
    def sunrise(self): 
        sunrise = 12 - (1 / to_rad(15)) * acos(-1 * tan(to_rad(self.declination_angle()))\
                * tan(to_rad(self.lat))) - self.time_correction() / 60
        return sunrise

    def sunset(self):
        sunset =  12 + (1 / to_rad(15)) * acos(-1 * tan(to_rad(self.declination_angle()))\
                * tan(to_rad(self.lat))) - self.time_correction() / 60
        return sunset

    def day_length(self):
        return self.sunset() - self.sunrise()
    
    def solar_insolation(self, HRA):
        # gives value in kW/m^2
        ID = 1.353 * 0.7 ** (self.AM(HRA) * 0.678)
        return ID

    def AM(self, HRA):
        elevation = asin(sin(to_rad(self.declination_angle())) * sin(to_rad(self.lat))\
                + cos(to_rad(self.declination_angle())) * cos(to_rad(self.lat)) * cos(HRA))
        azimuth = acos(sin(to_rad(self.declination_angle())) * cos(to_rad(self.lat))\
                - cos(to_rad(self.declination_angle()) * sin(to_rad(self.lat)) * cos(HRA))) / cos(elevation)
        if HRA > 0:
            azimuth = 2 * pi - azimuth
        zenith = (pi / 2) - elevation
        AM = 1 / cos(zenith)
        return AM
    
    def time_to_HRA(self,time):
        LST = time + self.time_correction() / 60
        HRA = to_rad(15) * (LST - 12)
        return HRA

    def energy_received(self):
       points = linspace(self.sunrise(), self.sunset(), 1000, endpoint = False).tolist()
       energy = []
       for i in range(len(points)):
           energy.append(self.solar_insolation(self.time_to_HRA(points[i])))
       return(energy, points)
