const leftJoystick = document.getElementById('leftJoystick');
const rightJoystick = document.getElementById('rightJoystick');

const controlSocket = new WebSocket(`ws://${location.hostname}:8000/ws`);

controlSocket.onopen = () => {
    console.log('Control WebSocket connection established');
};

controlSocket.onerror = (error) => {
    console.error('Control WebSocket error:', error);
};

function sendDriveCommand(left, right) {
    const message = JSON.stringify({ left, right });
    controlSocket.send(message);
}

const leftNipple = nipplejs.create({
    zone: leftJoystick,
    mode: 'static',
    position: { left: '50%', top: '50%' },
    color: 'blue'
});

const rightNipple = nipplejs.create({
    zone: rightJoystick,
    mode: 'static',
    position: { left: '50%', top: '50%' },
    color: 'red'
});

leftNipple.on('move', (evt, data) => {
    const value = Math.max(-1, Math.min(1, data.vector.y));
    sendDriveCommand(value, rightJoystick.value || 0);
    leftJoystick.value = value;
});

rightNipple.on('move', (evt, data) => {
    const value = Math.max(-1, Math.min(1, data.vector.y));
    sendDriveCommand(leftJoystick.value || 0, value);
    rightJoystick.value = value;
});

leftNipple.on('end', () => {
    leftJoystick.value = 0;
    sendDriveCommand(0, rightJoystick.value || 0);
});

rightNipple.on('end', () => {
    rightJoystick.value = 0;
    sendDriveCommand(leftJoystick.value || 0, 0);
});
