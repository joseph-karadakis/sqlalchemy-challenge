

#################################################
# Database Setup
#################################################

# Import SQLAlchemy dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Create engine to connect to the SQLite database.
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the existing database into a new model.
Base = automap_base()

# Reflect the tables.
Base.prepare(autoload_with=engine, reflect=True)

# Save references to each table.
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session (link) from Python to the database.
session = Session(engine)

#################################################
# Flask Routes
#################################################
# Import the dependencies.
from flask import Flask, jsonify

app = Flask(__name__)

# Define the homepage route.
@app.route("/")
def home():
    return (
        f"Welcome to the Climate App API!<br/><br/><br>"
        f"Available Routes:<br/><br>"
        f"Precipitation Data for last year: /api/v1.0/precipitation<br/><br>"
        f"Weather Stations Directory: /api/v1.0/stations<br/><br>"
        f"Most Active Station Temp Observations: /api/v1.0/tobs<br/><br>"
        f"Temp Metrics since start = YYYY-MM-DD: /api/v1.0/&lt;start&gt;<br/><br>"
        f"Temp Metrics from start= YYYY-MM-DD to end=YYYY-MM-DD: /api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# Define the /api/v1.0/precipitation route.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date 12 months ago from the most recent date in the database.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query the precipitation data for the last 12 months.
    results1 = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    session.close()
    
    # Convert the query results to a dictionary with date as the key and prcp as the value.
    precipitation_data = {date: prcp for date, prcp in results1}

     # Return the JSON representation of the precipitation data.
    return jsonify(precipitation_data)

# Define the /api/v1.0/stations route.
@app.route("/api/v1.0/stations")
def stations():
    # Query the list of stations with their names.
    results2 = session.query(Station.station, Station.name).all()
    session.close()

    # Create a list of dictionaries containing station and name information.
    station_list = []
    for result in results2:
        station_dict = {}
        station_dict['station'] = result[0]
        station_dict['name'] = result[1]
        station_list.append(station_dict)

    # Return the JSON representation of the station list.
    return jsonify(station_list)


# Define the /api/v1.0/tobs route.
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date 12 months ago from the most recent date in the database.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query the temperature observations for the most active station for the last 12 months.
    results3 = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= one_year_ago).\
        filter(Measurement.station == 'USC00519281').all()
    session.close()
    
    # Create a list of dictionaries containing the date and temperature observations.
    temperature_observations = []
    for date, tobs in results3:
        temperature_observations.append({'date': date, 'tobs': tobs})

    # Return the JSON representation of the temperature observations.
    return jsonify(temperature_observations)

# Define the /api/v1.0/<start> route.
@app.route("/api/v1.0/<start>")
def start_date_stats(start):
    #Convert the start dates to datetime object
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    # Query the minimum, average, and maximum temperature for all dates greater than or equal to the start date.
    results4 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    # Extract the temperature statistics from the query results.
    temperature_stats = {'TMIN': results4[0][0], 'TAVG': results4[0][1], 'TMAX': results4[0][2]}

    # Return the JSON representation of the temperature statistics.
    return jsonify(temperature_stats)

# Define the /api/v1.0/<start>/<end> route.
@app.route("/api/v1.0/<start>/<end>")
def start_end_date_stats(start, end):
    # Convert the start and end dates to datetime objects
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')

    # Query the minimum, average, and maximum temperature for dates from the start date to the end date (inclusive).
    results5 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()

    # Extract the temperature statistics from the query results.
    temperature_stats = {'TMIN': results5[0][0], 'TAVG': results5[0][1], 'TMAX': results5[0][2]}

    # Return the JSON representation of the temperature statistics.
    return jsonify(temperature_stats)


if __name__ == '__main__':
    app.run(debug=True)
