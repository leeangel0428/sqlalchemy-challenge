# Import the dependencies.
from matplotlib import style
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///SurfsUp/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

# Start at the homepage.
# List all the available routes.

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<h1><b> Hawaii Weather Data </b></h1>"
        f"<h2><b> Available routes:</b></h2> </br>"
        f"<b> Precipitation Data: </b> /api/v1.0/precipitation </br>"
        f"<b> Observed Stations: </b> /api/v1.0/stations </br>"
        f"<b> Temperature Observations: </b> /api/v1.0/tobs </br>"
        f"<b> Input date for Temperature Data (YYYY-MM-DD):</b> /api/v1.0/<start> </br>"
        f"<b> Input range of dates for Temperature data (YYYY-MM-DD/YYYY-MM-DD): </b> /api/v1.0/<start><end>"
    )

#Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= '2016-08-23').all()
    session.close()
    precipitation_list = []

    for date, prcp in data:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        precipitation_list.append(precipitation_dict)
     
    return jsonify(precipitation_list)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(station.station).all()
    session.close()

    stations_list = list(np.ravel(results))
    return jsonify(stations_list)

# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    station_data = session.query(measurement.tobs).filter(measurement.station=='USC00519281').filter(measurement.date >= '2016-08-23').all()
    session.close()

    station_data_list = list(np.ravel(station_data))
    return jsonify(station_data_list)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    results = (session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs))\
               .filter(measurement.date >= start)\
               .all()
               )
    (min, max, avg) = results[0]
    session.close()

    return jsonify(f"Start date: {start}", f"Lowest Temperature: {min} degrees", f"Average Temperature: {avg} degrees", f"Highest Temperature:  {max} degrees")

# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>/<end>")
def temp_summary(start, end):
    session = Session(engine)
    query_result = session.query(
            func.min(measurement.tobs),
            func.avg(measurement.tobs),
            func.max(measurement.tobs))\
            .filter(measurement.date >= start)\
            .filter(measurement.date <= end)\
            .all()
    (min, avg, max) = query_result[0]
    session.close()

    return jsonify(f"Start date: {start}", 
                   f"End date: {end}", 
                   f"Lowest Temperature: {min} degrees", f"Average Temperature: {avg} degrees", f"Highest Temperature: {max} degrees")


if __name__ == '__main__':
    app.run(debug=True)