/*
 * Author: Meir Michanie  <meirm@riunx.com>
 * License: MIT
 * Creation Date: 2023-03-24
 * Modification Date: 2023-03-24
 * Description: This file contains the core implementation for a flexible and extensible widgets system.
 *              It provides a framework for creating, managing, and communicating between various widget 
 *              instances. The framework enables easy customization, event handling, and subscription-based 
 *              messaging between widgets.
 * Filename: widgets.js
 * Version: 1.0.0
 *
 * Copyright (C) 2023 Meir Michanie  <meirm@riunx.com>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */
import {JPost} from '/static/js/jpost.js';
 
class WidgetBase {
    constructor(name) {
      this.name = name;
      this.identifier = name;
      this.status = 0; // ( running, scheduled, initialized) 1,2,4
      this.logLevel = ["CRITICAL", "MAJOR", "MINOR", "INFO", "DEBUG"];
      this.debugLevel = 3; // 0 critical, 1 major, 2 minor, 3 info, 4 debug
      this.CRITICAL = 0;
      this.MAJOR = 1;
      this.MINOR = 2;
      this.INFO = 3;
      this.DEBUG = 4;
      this.description = 'Simple Widget';
      this.settings = {};
    }

    init(){}
  
    updateSettings(options) {
      this.log(this.DEBUG, "Updating settings.");
      for (let item in options) {
        this.settings[item] = options[item];
      }
    }

    log(level, msg) {
      if (level > this.DEBUG) {
        level = this.DEBUG;
      }
      if (this.debugLevel >= level) {
        console.log(this.logLevel[level] + " - " + "Widget(" + this.name + "): " + msg);
      }
    }
  }
  
export class Widget extends WidgetBase {
    constructor(wm, name) {
      super(name);
      this.wm = wm;
      this.settings.priority = 10;
      this.settings.auto_start = true;
      this.settings.auto_subscribe = ['/radar'];
      this.settings.load_data = false;
      this.settings.load_interval = 0;
      this.settings.init_delay = 0;
      this.settings.enabled = false;
      this.settings.outgoing_data = {"source": this.name, 'action': 'refresh'};
      this.settings.uri = "/demo/demo_data"; // Fixme: we need to get this from the object or from parameter.
      this.settings.on_event_run = {};
      this.settings.on_event_emit = {};
      this.subscriptions = {};
    }
  
    init(options = null) {
      if (options !== null) {
        this.updateSettings(options);
      }
      this.log(this.INFO, "Initializing");
      if (this.settings.load_data) {
        this.requestData();
      }
    }
  
    getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
          const cookies = document.cookie.split(';');
          this.cookies = cookies;
          for (let i = 0; i < cookies.length; i++) {
              const cookie = cookies[i].trim();
              // Does this cookie string begin with the name we want?
              if (cookie.substring(0, name.length + 1) === (name + '=')) {
                  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                  break;
              }
          }
      }
      return cookieValue;
    }
    
    run() {
      this.requestData();
    }
  
    requestData() {
      console.log(this.name + " is requesting new data");
      const jpost = new JPost();
      jpost.setCallback(this);
      jpost.settings.uri = this.settings.uri;
      jpost.Submit(this.settings.outgoing_data);
    }
  
    requestLoad(payload) {
      for (let i = 0; i < payload.length; i++) {
        this.log(this.DEBUG, "loading record:" + payload[i]);
      }
    }
  
    requestCallback(payload, reference = null) {
      this.log(this.DEBUG, "We got back:");
      let txt = JSON.stringify(payload);
      this.log(this.DEBUG, txt);
    }
  
    onEvent(event) {
      if (event in this.settings.on_event_run) {
        this.settings.on_event_run[event].call(this);
      }
    }
  
    onEventEmit(event) {
      if (event in this.settings.on_event_emit) {
        let event_obj = this.settings.on_event_emit[event];
        if ('channel' in event_obj && 'msg' in event_obj) {
          this.queueEmit(event_obj.channel, event_obj.msg);
        }
      }
    }
  
    queueEmit(channel, msg) {
      this.wm.queueEmit(this, channel, msg);
    }
  
    queueSubscribe(channel) {
      this.wm.queueSubscribe(this, channel);
    }
  
    ping(target) {
      this.wm.queueEmit(this, '/radar', 'Ping ' + target);
    }
  
    pong() {
      this.queueEmit('/radar', 'Pong');
    }
  
    processMessage(sender, channel, msg) {
      this.log(this.DEBUG, "Pending process of msg:(" + msg + ") from:(" + sender +") on channel:(" + channel + ")");
      eval(this.subscriptions[channel]);
    }
    
    queueReceive(sender, channel, msg) {
      this.log(this.DEBUG, "Got msg:(" + msg + ") from:(" + sender +") on channel:(" + channel + ")");
      if (channel == "/radar" && msg.startsWith("Ping ")) {
        if (msg == "Ping " + this.name) {
          this.pong();
          return;
        } else {
          return;
        }
      }
      if (typeof (this.subscriptions[channel]) != "undefined") {
        this.processMessage(sender, channel, msg);
      }
    }
  
  
    processMessage(sender, channel, msg) {
    this.log(this.DEBUG, "Pending process of msg:(" + msg + ") from:(" + sender +") on channel:(" + channel + ")");
    eval(this.subscriptions[channel]);
    }
  
    queueReceive(sender, channel, msg) {
    this.log(this.DEBUG, "Got msg:(" + msg + ") from:(" + sender +") on channel:(" + channel + ")");
    if (channel == "/radar" && msg.startsWith("Ping ")) {
      if (msg == "Ping " + this.name) {
        this.pong();
        return;
      } else {
        return;
      }
    }
    if (typeof(this.subscriptions[channel]) != "undefined") {
      this.processMessage(sender, channel, msg);
    }
    }

}
  

export class WidgetManager extends WidgetBase {
    constructor(name) {
      super(name);
      this.settings.auto_start = true;
      this.settings.enabled = true;
      this.settings.scheduler_enabled = true;
      this.channels = { '/radar': [] }; // each channel has an array of subscribers instances.
      this.subscribers = {};
      this.widgets = [];
    }
  
    init() {
      super.init();
      this.log(this.DEBUG, "WidgetManager started.");
    }
  
    queueSubscribe(subscriber, channel) {
      if (typeof this.subscribers[subscriber.name] === "undefined") {
        this.subscribers[subscriber.name] = subscriber;
      }
      if (typeof this.channels[channel] !== "undefined") {
        this.channels[channel].push(subscriber);
      } else {
        this.channels[channel] = [subscriber];
      }
      this.log(
        this.DEBUG,
        `Subscriber: ${subscriber.name} subscribed to channel: ${channel}`
      );
    }
  
    addWidget(new_widget) {
      this.widgets.push(new_widget);
      this.log(this.DEBUG, "Widget added.");
    }
  
    initWidgets() {
      for (const current_widget of this.widgets) {
        // Init widget
        console.log(`Initializing for real ${current_widget.name}`);
        current_widget.init();
      }
    }
  
    subscribeWidgets() {
      for (const current_widget of this.widgets) {
        if (typeof current_widget.settings.auto_subscribe !== "undefined") {
          for (const [key, value] of Object.entries(current_widget.settings.auto_subscribe)) {
            this.log(
              this.INFO,
              `Subscribing ${current_widget.name} to ${value}`
            );
            current_widget.queueSubscribe(value);
          }
          current_widget.queueSubscribe(`/${current_widget.name}`);
          this.ping(current_widget.name);
        } else {
          this.log(this.DEBUG, `Failed Subscribing ${current_widget.name}`);
        }
      }
    }
  
    broadcast(message) {
      for (const current_widget of this.widgets) {
        current_widget.queueReceive(this.name, `/${current_widget.name}`, message, 'Init done');
      }
    }
  
    runWidgets(cmd, params = "") {
      for (const current_widget of this.widgets) {
        this.log(
          this.DEBUG,
          `${current_widget.name} ########## will run current_widget.${cmd}(${params});`
        );
        eval(`current_widget.${cmd}(${params});`);
      }
    }
  
    runSchedule() {
      if (this.settings.scheduler_enabled) {
        this.settings.interval_counter++;
        this.log(this.DEBUG, "Running scheduler.");
        for (const current_widget of this.widgets) {
          if (current_widget.settings.load_interval > 0) {
            const period = current_widget.settings.load_interval / 1000;
            if (
              this.settings.interval_counter % period == 0 &&
              this.settings.enabled
            ) {
              this.log(this.DEBUG, `Updating ${current_widget.name}`);
              current_widget.run();
            } else {
              this.log(
                this.DEBUG,
                `With Counter: ${this.settings.interval_counter} and Period:${period} Not updating: ${
                  period % this.settings.interval_counter
                }`
              );
            }
          }
        }
      } else {
        // disable scheduler
        this.log(
          this.DEBUG,
          `!!!! Should never get here Disabling interval, to re-enable run ${this.name}.scheduler(true);`
        );
        clearInterval(this.settings.interval_counter);
      }
    }
  
    initScheduler() {
      this.settings.interval_counter = 0; // may be needed when setting it to on.
      this.settings.interval_obj = setInterval(
        () => this.runSchedule(),1000);
    }

    scheduler(on_off) {
        if (this.settings['scheduler_enabled'] !== on_off ){
            this.settings['scheduler_enabled'] = on_off;
            if (on_off){
                this.log(this.DEBUG, 'Enabling interval, to stop ' + this.name + '.scheduler(false);');
                this.initScheduler();
            }else{
                this.log(this.DEBUG, 'Disabling interval, to stop ' + this.name + '.scheduler(true);');
                clearInterval(this.settings['interval_obj']);
            }
        }
    }

    queueEmit(sender, channel, msg) {
        if (typeof (this.channels[channel]) == "undefined"){
            this.channels[channel] = [];
            // return as nobody is subscribed so far.
            return;
        }
        this.log(this.DEBUG, "Subscriber: " + sender.name +" sent msg:(" + msg + ") on channel:(" + channel + ")");

        for (var i=0; i < this.channels[channel].length; i++){
            var target = this.channels[channel][i];
            if(target.name == sender.name){
                continue;
            }
        target.queueReceive(sender.name, channel, msg);
        }
    }

    sendMessage(channel, msg) {
        if (typeof (this.channels[channel]) == "undefined"){
            this.channels[channel] = [];
            // return as nobody is subscribed so far.
            this.log(this.DEBUG, "return as nobody is subscribed so far to channel: " + channel);
            return;
        }
        this.log(this.DEBUG, "WidgetManager sending msg:(" + msg + ") on channel:(" + channel + ")");
        for (var j=0; j < this.channels[channel].length; j++){
            var target = this.channels[channel][j];
            if(target.name == this.name){
                continue;
            }
            target.queueReceive(this.name, channel, msg);
            }
    }

    ping(target_name) {
        if (typeof(this.subscribers[target_name]) == "undefined"){
            this.log(this.MAJOR, 'Pinging invalid target(' + target_name + ')');
            return;
        }
        var target = this.subscribers[target_name];
        var channel = "/radar";
        target.queueReceive(this.name, channel, 'Ping ' + target_name);
    }
}

export function $(id) {
    return document.getElementById(id);
  }

console.log("widgets was here");