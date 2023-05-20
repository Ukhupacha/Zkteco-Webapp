const NodeHelper = require("node_helper");
const {PythonShell} = requrie('python-shell');
var pyshell;

module.exports = NodeHelper.create( {

    config: null,
    debug: false,

    init() {
        console.log(`Init module helper: ${this.name}`);
    },
    start() {
        console.log(`Starting module helper: ${this.name}`);
    },
    stop() {
        console.log(`Stopping module helper: ${this.name}`);
    },

    // Handle messages form our module// each notification indicates a different message
    // payload is a data structure that is differente per message.. up to you to design this
    socketNotificationReceived(notification, payload) {
        if (this.debug){
            console.log(this.name + " received a socket notification: " + notification + " - Payload " + payload);
        }
        // if config message from module
        if (notification == "zkteco-config") {
            // save payload config info
            this.config = payload;
        } 
        else if (notification=="zkteco-attendance") {
            this.getattendance();
        }
    },
    
    // get the data from the python script
    getattendance() {
        pyshell = new PythonShell('modules/Zkteco-Webapp/MMM-Zkteco.py');
        pyshell.on('message', function(message) {
            if (this.debug) {
                console.log(message);
            }
            this.sendSocketNotification("zkteco-data", payload);            
        });

        pyshell.end(function(err) {
            if (err) throw err;
            console.log(`${this.name} finished running...`);
            this.sendSocketNotification('zkteco-error', 'pyshell-throw');
        })
    }
});