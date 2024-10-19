/*
 * Author: Meir Michanie  <meirm@riunx.com>
 * License: MIT
 * Creation Date: 2023-03-24
 * Modification Date: 2023-03-24
 * Description: This file contains a sample widget that demonstrates how to use the widgets 
 *              system. The sample widget, called ClockWidget, displays the current time at 
 *              regular intervals. It shows how to query for data, update the display, 
 *              and interact with other widgets using the core framework provided by widgets.js.
 * Filename: clock.js
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

import { Widget, $ } from '/static/js/widgets.js'; // No need to import wm, as it is globally available through window.wm

// Extend Date to format date and time
Date.prototype.today = function () { 
  return ((this.getDate() < 10)?"0":"") + this.getDate() +(((this.getMonth()+1) < 10)?"/0":"/") + (this.getMonth()+1) +"/"+ this.getFullYear();
}

Date.prototype.timeNow = function () {
  return ((this.getHours() < 10)?"0":"") + this.getHours() + ((this.getMinutes() < 10)?":0":":") + this.getMinutes() + ((this.getSeconds() < 10)?":0":":") + this.getSeconds();
}

class ClockWidget extends Widget {
  constructor(wm, name) {
    super(wm, name);
    this.currentdate = new Date(); 
    this.datetime = " " +  this.currentdate.today() + " @ " + this.currentdate.timeNow();
  }

  requestData() {
    this.currentdate = new Date(); 
    this.datetime = " " +  this.currentdate.today() + " @ " + this.currentdate.timeNow();
    this.updateDisplay();
    return;
  }

  requestCallback(payload, reference = null) {
    this.log(this.DEBUG, "We got back:");
    var txt = JSON.stringify(payload);
    this.log(this.DEBUG, txt);

    if (payload.hasOwnProperty("currentTime") && payload.hasOwnProperty("tz")) {
      this.currentTime = payload.currentTime;
      this.tz = payload.tz;
      this.updateDisplay();
    }
  }

  updateDisplay() {
    $("clock").textContent = this.datetime;
  }
}

// Create an instance of ClockWidget using the globally accessible window.wm
const clockWidget = new ClockWidget(window.wm, "Clock");
// Set the load interval to 1 second
clockWidget.settings["load_interval"] = 1000;
// Add the widget to the widget manager
window.wm.addWidget(clockWidget);