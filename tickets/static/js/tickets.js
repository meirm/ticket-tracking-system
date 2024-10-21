import { wm } from '/static/js/global_head.js';
import { Widget, $ } from '/static/js/widgets.js';

class TicketsWidget extends Widget {
  constructor(wm, name) {
    super(wm, name);
    this.tickets = [];
    this.newTicketsCount = 0; // Counter for new tickets
    this.tag = null;
    this.settings.uri = '/tickets/pull/?action=get_info&source=open_issues'; // URI to fetch the list of tickets (or tickets)
    this.requestCallback = this.requestCallback.bind(this);
  }

  init() {
    // Get the notification tag element where the badge will be displayed
    this.tag = document.querySelector('.ticket_count');
  }

  run() {
    // Fetch the list of tickets (or tickets) from the server
    fetch(this.settings.uri)
      .then(response => response.json())
      .then(data => {
        this.requestCallback(data);
      })
      .catch(error => {
        console.error(error);
      });
  }

  requestCallback(data) {
    if (data.hasOwnProperty('tickets')) {
      // Filter new tickets (tickets) based on status or condition
      this.tickets = data.tickets;
      this.newTicketsCount = this.tickets.filter(ticket => ticket.status === 'new').length;
      // Update the badge based on new tickets count
      this.updateTag();
    }
  }

  updateTag() {
    // Show or hide the notification badge based on the newTicketsCount
    if (this.newTicketsCount > 0) {
      this.tag.textContent = this.newTicketsCount; // Display the number of new tickets
      this.tag.classList.add('show'); // Ensure the badge is visible
    } else {
      this.tag.textContent = ''; // Clear the text if no new tickets
      this.tag.classList.remove('show'); // Hide the badge
    }
  }
}

// Create an instance of TicketsWidget
const ticketsAlertWidget = new TicketsWidget(wm, "Tickets");
// Set the load interval to 5 seconds
ticketsAlertWidget.settings["load_interval"] = 5000;
// Add the widget to the widget manager
wm.addWidget(ticketsAlertWidget);

console.log("ticketsAlertWidget was here");