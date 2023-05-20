const { wrap } = require("module");

Module.register("MMM-Zkteco", {
    default : {
        zktecoIp: "zkteco.intranet"
    },

    message: "MMM-Zkteco starting up",
    notificationReceived(notification, payload) {
        Log.log("notification received = " + notification);
        // if all modules are running
        if (notification == 'ALL_MODULES_STARTED') {
            // send our config down to helper to use
            this.sendNotification("zkteco-config", this.config)
            // get the playing content
            this.message = "MMM-Zkteco waiting for content from api request"
            this.sendNotification("zkteco-attendance", null)
        }
    },

    // helper sends back specific attendance data
    socketNotificationReceived: function (notification, payload) {
        if (notification == 'zkteco-data') {
            Log.log("received content back from helper");
            // save it
            this.content = payload;
            Log.log("there are " + this.content.length + "elements to display");
            if (this.content.length == 0) {
                this.message = "MMM-Zkteco No data found " + this.config.zktecoIp;
            }
            // tell MM we have new stuff to display
            // will cause getDom() to be called
            this.updateDom();
        }
    },

    getDom: function () {
        // base wrapper for our content
        wrapper = document.createElement("div");
        if (this.content.length > 0 ) {
            attendance = document.createElement("div");
            attendance.setAttribute('class', 'attendance');
            attendance.innerHTML = this.content;
        }
        else {
            wrapper.innerHTML = this.message;
        }
        // tell MM this is our content to add to the MM dom
        return wrapper;
    },

    getStyles: function () {
        return ["MMM-Zkteco.css"];
    }
});