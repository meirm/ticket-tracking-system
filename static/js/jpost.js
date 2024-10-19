export class JPost {
    constructor() {
      this.settings = {};
      this.settings["uri"] = "/api/get_data";
      this.settings["method"] = "POST";
      this.settings["timeout"] = 3000;
      this.log_level = ["CRITICAL", "MAJOR", "MINOR", "INFO", "DEBUG"];
      this.debug_level = 3; // 0 critical, 1 major, 2 minor, 3 info, 4 debug
      this.CRITICAL = 0;
      this.MAJOR = 1;
      this.MINOR = 2;
      this.INFO = 3;
      this.DEBUG = 4;
      this.settings["contentType"] = "application/json; charset=utf-8";
      this.settings["dataType"] = "json";
    }
  
    Log(level, msg) {
      if (level > this.DEBUG) {
        level = this.DEBUG;
      }
      if (this.debug_level >= level) {
        console.log(this.log_level[level] + " - " + "JPost(" + this.name + "): " + msg);
      }
    }
  
    async Callback(response) {
      const data = await response.json();
      this.Log(this.DEBUG, "got it");
      this.Log(this.DEBUG, "calling client...");
      this.Log(this.DEBUG, this.settings["client"].name);
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
      this.Log(this.DEBUG, "calling " + uri + " with data:" + txt);
    
      try {
        const response = await this.timeout(timeoutValue, fetch(uri, {
          method: method,
          headers: {
            "Content-Type": contentType,
            ...headers // spread the headers object
          },
          body: txt,
        }));
    
        if (response.ok) {
          this.Callback(response);
        } else {
          console.log("ERROR: We had an error posting.");
          console.log(response.status, response.statusText);
        }
      } catch (error) {
        if (error.message === "Request timed out") {
          console.log("Error:timeout");
          console.log(error);
        } else {
          console.error("Fetch error:", error);
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