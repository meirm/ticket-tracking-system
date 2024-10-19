import {WidgetManager} from '/static/js/widgets.js';
export const wm = new WidgetManager("Widget Manager");
wm.init();
window.wm = wm;