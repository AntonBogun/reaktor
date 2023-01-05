const express = require("express");
const app = express();
const axios = require("axios");
const parseString = require("xml2js").parseString;
app.use(express.static("build"));

const NEST_CENTER = { x: 250000, y: 250000 }; //milimeters
const MIN_DIST = 100 * 1000; //100 meters
const API_ENDPOINT = "https://assignments.reaktor.com/birdnest/drones"; //XML
const PILOT_ENDPOINT = "https://assignments.reaktor.com/birdnest/pilots/"; //JSON
const TTL_LENGTH = 1000 * 60 * 10; //10 minutes
// const TTL_LENGTH = 1000 * 10; //!DEBUG
const INTERVAL_LENGTH = 1000; // if updates at api happen once around 2 seconds, this should never miss an update

function dist_to_nest(x, y) {
  return Math.sqrt((x - NEST_CENTER.x) ** 2 + (y - NEST_CENTER.y) ** 2);
}

class Parser {
  static parse_drones(xml_text) {
    return new Promise((resolve, reject) => {
      parseString(xml_text, (err, result) => {
        if (err) {
          reject(err);
        } else {
          try {
            resolve(this.strip_drones(result));
          } catch (error) {
            reject(error);
          }
        }
      });
    });
  }
  static strip_drones(result) {
    return result.report.capture[0].drone.map((drone) => {
      return {
        x: drone.positionX[0],
        y: drone.positionY[0],
        serial_number: drone.serialNumber[0],
      };
    });
  }

  static parse_pilot(json) {
    // return this.strip_pilot(JSON.parse(json_text));
    return this.strip_pilot(json);
  }
  static strip_pilot(result) {//maybe there's a better name...
    return {
      firstName: result.firstName,
      lastName: result.lastName,
      email: result.email,
      phone: result.phoneNumber,
    };
  }
}

function request_pilot_info_promise(serial_number, closest_dist, cancel_token) {
  if (closest_dist > MIN_DIST) {
    console.error("query of information despite not violating NDZ");
    return undefined;
  }
  return new Promise((resolve, reject) => {
    axios
      .get(PILOT_ENDPOINT + serial_number, {}, { cancelToken: cancel_token })
      .then((response) => {
        try {
          resolve(Parser.parse_pilot(response.data));
        } catch (error) {
          reject(error);
        }
      })
      .catch((error) => {
        reject(error);
      });
  });
}
function request_drones_promise() {
  return new Promise((resolve, reject) => {
    axios
      .get(API_ENDPOINT)
      .then(async (response) => {
        try {
          resolve(await Parser.parse_drones(response.data));
        } catch (error) {
          reject(error);
        }
      })
      .catch((error) => {
        reject(error);
      });
  });
}

function process_drones(drones) {
  return drones.map((drone) => {
    return {
      ...drone,
      closest_dist: dist_to_nest(drone.x, drone.y),
    };
  });
}

class Pilot {
  constructor(closest_dist, serial_number) {
    this.closest_dist = closest_dist; //expected to be below MIN_DIST
    this.serial_number = serial_number;
    this.pilot_info = undefined;
    this.request_promise = undefined;
    this.cancel_token = undefined;
    this.TTL = new Date().getTime() + TTL_LENGTH;
  }

  async update_pilot_info() {
    //in case of request error, keep requesting until success, then stop
    if (this.pilot_info === undefined && this.request_promise === undefined) {
      this.cancel_token = axios.CancelToken.source();
      this.request_promise = request_pilot_info_promise(this.serial_number, this.closest_dist, this.cancel_token.token);
      try {
        this.pilot_info = await this.request_promise;
      } catch (error) {
        console.error(error);
      }
      this.request_promise = undefined;
      this.cancel_token = undefined;
    }
  }

  format_return_info() {
    //undefined is supposed to be filtered out on reply
    if (this.pilot_info === undefined) {
      return undefined;
    }
    //from Parser.parse_pilot: { firstName, lastName, email, phone }
    // return { ...this.pilot_info, closest_dist: this.closest_dist };
    return { ...this.pilot_info, closest_dist: this.closest_dist, TTL: this.TTL };
  }

  update(new_dist) {
    this.closest_dist = Math.min(this.closest_dist, new_dist);
    this.TTL = new Date().getTime() + TTL_LENGTH;
  }

  is_expired() {
    return new Date().getTime() > this.TTL;
  }

  cancel() {
    if (this.cancel_token !== undefined) {
      this.cancel_token.cancel();
    }
  }
}

class Pilots {
  constructor() {
    this.pilots = {};
  }

  update_pilots(processed_drones) {
    //handles inserting new pilots, updating existing pilots and removing expired pilots
    processed_drones.forEach((drone) => {
      this.update_pilot(drone.serial_number, drone.closest_dist);
    });
    this.remove_expired_pilots();
    this.update_pilot_info();
  }

  update_pilot(serial_number, new_dist) {
    if (serial_number in this.pilots) {
      this.pilots[serial_number].update(new_dist);
    } else {
      if (new_dist < MIN_DIST)
        //only insert if below MIN_DIST
        this.pilots[serial_number] = new Pilot(new_dist, serial_number);
    }
  }

  remove_expired_pilots() {
    Object.keys(this.pilots).forEach((serial_number) => {
      if (this.pilots[serial_number].is_expired()) {
        this.pilots[serial_number].cancel();
        delete this.pilots[serial_number];
      }
    });
  }

  update_pilot_info() {
    Object.keys(this.pilots).forEach((serial_number) => {
      this.pilots[serial_number].update_pilot_info();
    });
  }

  get_pilots_info() {
    return Object.values(this.pilots)
      .map((pilot) => {
        return pilot.format_return_info();
      })
      .filter((pilot) => {
        return pilot !== undefined;
      });
  }
}

const pilots = new Pilots();

function runRequest() {
  request_drones_promise()
    .then((drones) => {
      pilots.update_pilots(process_drones(drones));
    })
    .catch((error) => {
      console.error(error);
    });
}

setInterval(runRequest, INTERVAL_LENGTH);

app.get("/api", (req, res) => {
  res.json(pilots.get_pilots_info());
});

const PORT = process.env.PORT || 3001;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
