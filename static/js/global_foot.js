
// Initialize and subscribe widgets
import { wm } from '/static/js/global_head.js';

try {
    wm.initWidgets();
    wm.subscribeWidgets();
    wm.initScheduler();
} catch (error) {
    console.error('Widget initialization error:', error);
}