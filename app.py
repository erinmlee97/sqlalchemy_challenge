# import dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

######################################################
# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

######################################################
# Flask Setup
app = Flask(__name__)

######################################################
# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
         f"Welcome to Hawaii Climate Page<br/> "
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date (please use 'yyyy-mm-dd' format): /api/v1.0/min_max_avg/&lt;start date&gt;<br/>"
        f"Temperature stat from start to end dates(please use 'yyyy-mm-dd'/'yyyy-mm-dd' format for start and end values) /api/v1.0/min_max_avg/&lt;start date&gt;/&lt;end date&gt;<br/>"
    )


@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    sel = [Measurement.date, Measurement.prcp]
    query_result = session.query(*sel).all()
    
    session.close()

    precipitation_list = []
    for date, prcp in query_result:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation_list.append(prcp_dict)
    
    return jsonify(precipitation_list)


@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    query_result = session.query(*sel).all()
    
    session.close()

    station_list = []
    for station, name, latitude, longitude, elevation in query_result:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = latitude
        station_dict["Lon"] = longitude
        station_dict["Elevation"] = elevation
        station_list.append(station_dict)
    
    return jsonify(station_list)


@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_year_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    query_date = dt.date(last_year_date.year -1, last_year_date.month, last_year_date.day)
    sel = [Measurement.date, Measurement.tobs]
    query_result = session.query(*sel).filter(Measurement.date >= query_date).all()
    
    session.close()

    tobs_list = []
    for date, tobs in query_result:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_list.append(tobs_dict)
    
    return jsonify(tobs_list)


@app.route("/api/v1.0/min_max_avg/<start>")
def start(start):
    session = Session(engine)
    query_result = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start).\
                    group_by(Measurement.date).all()

    session.close()

    start_list = []
    for date, min, avg, max in query_result:
        start_dict = {}
        start_dict["Date"] = date
        start_dict["TMIN"] = min
        start_dict["TAVG"] = avg
        start_dict["TMAX"] = max
        start_list.append(start_dict)

    return jsonify(start_list)

@app.route('//api/v1.0/min_max_avg/<start>/<stop>')
def start_stop(start,stop):
    session = Session(engine)
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= stop).all()
    session.close()

    start_stop_list = []
    for min,avg,max in query_result:
        start_stop_dict = {}
        start_stop_dict["Min"] = min
        start_stop_dict["Average"] = avg
        start_stop_dict["Max"] = max
        start_stop_list.append(start_stop_dict)

    return jsonify(start_stop_list)

if __name__ == '__main__':
    app.run(debug=True)