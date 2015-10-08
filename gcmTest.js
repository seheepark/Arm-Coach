var gcm = require('node-gcm');

// create a message with default values
var message = new gcm.Message();

// or with object values
var message = new gcm.Message({
    collapseKey: 'demo',
    delayWhileIdle: true,
    timeToLive: 3,
    data: {
        key1: '안녕하세요.',
        key2: 'saltfactory push demo'
    }
});

var server_access_key = 'AIzaSyCAkwJgDPnLbwZwKz7grVxhs7iXtkx6wmo';
var sender = new gcm.Sender(server_access_key);
var registrationIds = [];

var registration_id = 'APA91bHzj7_DNYHEwTZ1D8EOUGR8f8MNqXamjcNGAYfZG4uOEsYWBfRBTAhuNx9QM7nakBQiWSU35T87Fbe6y9bAIXMPFNB2uv0wS0iMmzskcvp6vktpdUqxafksdVxQNiWI0krk1Axq';
// At least one required
registrationIds.push(registration_id);

/**
 * Params: message-literal, registrationIds-array, No. of retries, callback-function
 **/
sender.send(message, registrationIds, 4, function (err, result) {
    console.log(result);
});

