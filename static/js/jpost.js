class Levels {
  constructor() {
    this.CRITICAL = 0;
    this.MAJOR = 1;
    this.MINOR = 2;
    this.INFO = 3;
    this.DEBUG = 4;
  }
  get_level(level) {
    switch (level) {
      case "CRITICAL":
        return this.CRITICAL;
      case "MAJOR":
        return this.MAJOR;
      case "MINOR":
        return this.MINOR;
      case "INFO":
        return this.INFO;
      case "DEBUG":
        return this.DEBUG;
      default:
        return this.INFO;
    }
  }
  get_level_name(level) {
    switch (level) {
      case this.CRITICAL:
        return "CRITICAL";
      case this.MAJOR:
        return "MAJOR";
      case this.MINOR:
        return "MINOR";
      case this.INFO:
        return "INFO";
      case this.DEBUG:
        return "DEBUG";
      default:
        return "INFO";
    }
  }

}

function Log(caller, level, msg) {
  if (level > Levels.DEBUG) {
    level = Levels.DEBUG;
  }
  if (caller.debug_level >= level) {
    console.log(Levels.get_level_name[level] + " - " +  caller.name + ": " + msg);
  }
}

class HttpGetter {
  constructor(settings) {
    this.settings = settings || {};
    this.settings["timeout"] = this.settings["timeout"] || 3000;
    this.debug_level = this.settings["debug_level"] || Levels.INFO;
    this.name = this.settings["name"] || "HttpGetter";
  }

  async Post(uri, data, headers = {}) {
    try {
      const response = await this.timeout(this.settings["timeout"], fetch.Post(uri, {
        headers: {
          ...headers
        },
        body: data,
      }));
      return response;
    } catch (error) {
      if (error.message === "Request timed out") {
        Log(this, Levels.CRITICAL, "Timeout");
        Log(this, Levels.CRITICAL, error);
      } else {
        Log(this, Levels.CRITICAL, "Fetch error");
        Log(this, Levels.CRITICAL, error);
      }
      return null;
    }
  }

  async Get(uri, headers = {}) {
    try {
      const response = await this.timeout(this.settings["timeout"], fetch.Get(uri, {
        headers: {
          ...headers
        },
      }));
      return response;
    } catch (error) {
      if (error.message === "Request timed out") {
        Log(this, Levels.CRITICAL, "Timeout");
        Log(this, Levels.CRITICAL, error);
      } else {
        Log(this, Levels.CRITICAL, "Fetch error");
        Log(this, Levels.CRITICAL, error);
      }
      return null;
    }
  }

  async Put(uri, data_out, headers = {}) {
    try {
      const response = await this.timeout(this.settings["timeout"], fetch.Put(uri, {
        headers: {
          ...headers
        },
        body: data_out,
      }));
      return response;
    }
    catch (error) {
      if (error.message === "Request timed out") {
        Log(this, Levels.CRITICAL, "Timeout");
        Log(this, Levels.CRITICAL, error);
      } else {
        Log(this, Levels.CRITICAL, "Fetch error");
        Log(this, Levels.CRITICAL, error);
      }
      return null;
    }
  }

  async Delete(uri, headers = {}) {
    try {
      const response = await this.timeout(this.settings["timeout"], fetch.Delete(uri, {
        headers: {
          ...headers
        },
      }));
      return response;
    } catch (error) {
      if (error.message === "Request timed out") {
        Log(this, Levels.CRITICAL, "Timeout");
        Log(this, Levels.CRITICAL, error);
      } else {
        Log(this, Levels.CRITICAL, "Fetch error");
        Log(this, Levels.CRITICAL, error);
      }
      return null;
    }
  }

  async Head(uri, headers = {}) {
    try {
      const response = await this.timeout(this.settings["timeout"], fetch.Head(uri, {
        headers: {
          ...headers
        },
      }));
      return response;
    } catch (error) {
      if (error.message === "Request timed out") {
        Log(this, Levels.CRITICAL, "Timeout");
        Log(this, Levels.CRITICAL, error);
      } else {
        Log(this, Levels.CRITICAL, "Fetch error");
        Log(this, Levels.CRITICAL, error);
      }
      return null;
    }
  }

  timeout(ms, promise) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error("Request timed out"));
      }, ms);

      promise
        .then((value) => {
          clearTimeout(timer);
          resolve(value);
        })
        .catch((reason) => {
          clearTimeout(timer);
          reject(reason);
        });
    });
  }
}

export class JPost {
  constructor() {
    this.settings = {};
    this.settings["uri"] = "/api/get_data";
    this.settings["method"] = "POST";
    this.settings["timeout"] = 3000;
    this.debug_level = Levels.INFO;
    this.settings["contentType"] = "application/json; charset=utf-8";
    this.settings["dataType"] = "json";
    this.name = "JPost";
    this.httpGetter = new HttpGetter({
      timeout: this.settings["timeout"],
      debug_level: this.debug_level,
      name: this.name
    });
  }

  async Callback(response) {
    const data = await response.json();
    Log(this, Levels.DEBUG, "got it");
    Log(this, Levels.DEBUG, "calling client...");
    Log(this, Levels.DEBUG, this.settings["client"].name);
    this.settings["client"].Request_callback(data);
  }

  setCallback(obj) {
    this.settings["client"] = obj;
  }

  async Submit(data_out, reference = null, headers = {}) {
    if (reference !== null) {
      data_out["reference"] = reference;
    }
    const txt = JSON.stringify(data_out);
    const method = this.settings["method"];
    const contentType = this.settings["contentType"];
    const uri = this.settings["uri"];
    const timeoutValue = this.settings["timeout"];
    Log(this, Levels.DEBUG, "calling " + uri + " with data:" + txt);

    try {
      let response;
      switch (method) {
        case "POST":
          response = await this.httpGetter.Post(uri, txt, headers);
          break;
        case "GET":
          response = await this.httpGetter.Get(uri, headers);
          break;
        case "PUT":
          response = await this.httpGetter.Put(uri, txt, headers);
          break;
        case "DELETE":
          response = await this.httpGetter.Delete(uri, headers);
          break;
        case "HEAD":
          response = await this.httpGetter.Head(uri, headers);
          break;
        default:
          throw new Error("Unsupported HTTP method");
      }

      if (response && response.ok) {
        this.Callback(response);
      } else {
        Log(this, Levels.CRITICAL, "ERROR: We had an error posting.");
        Log(this, Levels.CRITICAL, response.status + " " + response.statusText);
      }
    } catch (error) {
      if (error.message === "Request timed out") {
        Log(this, Levels.CRITICAL, "Error:timeout");
        Log(this, Levels.CRITICAL, error);
      } else {
        Log(this, Levels.CRITICAL, "Fetch error");
        Log(this, Levels.CRITICAL, error);
      }
    }
  }

  timeout(ms, promise) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error("Request timed out"));
      }, ms);

      promise
        .then((value) => {
          clearTimeout(timer);
          resolve(value);
        })
        .catch((reason) => {
          clearTimeout(timer);
          reject(reason);
        });
    });
  }
}

// The remaining utility functions remain unchanged.
function timeout(ms, promise) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error("Request timed out"));
    }, ms);

    promise
      .then((value) => {
        clearTimeout(timer);
        resolve(value);
      })
      .catch((reason) => {
        clearTimeout(timer);
        reject(reason);
      });
  });
}

function jsonToFormattedTxt(data_out) {
  return(JSON.stringify(data_out, null, 2));
}

function api_build_query(path, data_out, callback){
  let uri = path;
   if(typeof api_secret !== 'undefined' && typeof api_key !== 'undefined'){
      uri+= '?api_secret=' + api_secret + '&api_key=' + api_key;
   }
  json_post(uri,data_out,callback);
}

function formatedTxt(txt) {
  txt = txt.split('\\n').join("\n");
  var data_out = JSON.parse(txt);
  return(JSON.stringify(data_out, null, 2));
}

function txtToJson(txt) {
  var data_out = JSON.parse(txt);
  return(data_out);
}

function objectifyForm(formArray) {//serialize data function
    var returnArray = {};
    for (var i = 0; i < formArray.length; i++){
      var var_name = formArray[i]['name'];
      var var_type = typeof returnArray[var_name];
      var value = formArray[i]['value'];
      //console.log("Processing: " + var_name + " with value:" + value );
      if (value == "#boolean(true)"){
          value = true;
      }
      if (value == "#boolean(false)"){
          value = false;
      }
      if (var_type == 'string'){
          returnArray[var_name] = [returnArray[var_name], value];
      }else if (var_type == 'undefined'){
          returnArray[var_name] = value;
      }else{
          returnArray[var_name].push(value);
      }
    }
    return returnArray;
  }