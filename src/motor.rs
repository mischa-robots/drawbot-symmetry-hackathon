use linux_embedded_hal::I2cdev;
use pwm_pca9685::{Channel, Pca9685};
use std::collections::HashMap;
use std::sync::Mutex;
use once_cell::sync::Lazy;

pub struct DcChannels {
    ref_channel: Channel,
    forward_channel: Channel,
    backward_channel: Channel,
}

#[derive(Eq, Hash, PartialEq)]
pub enum Motor {
    Motor1,
    Motor2,
    Motor3,
    Motor4,
}

pub static DC_CHANNEL_MAP: Lazy<HashMap<Motor, DcChannels>> = Lazy::new(|| {
    let mut map = HashMap::new();
    map.insert(
        Motor::Motor1,
        DcChannels {
            ref_channel: Channel::C8,
            forward_channel: Channel::C9,
            backward_channel: Channel::C10,
        },
    );
    map.insert(
        Motor::Motor2,
        DcChannels {
            ref_channel: Channel::C13,
            forward_channel: Channel::C11,
            backward_channel: Channel::C12,
        },
    );
    map.insert(
        Motor::Motor3,
        DcChannels {
            ref_channel: Channel::C2,
            forward_channel: Channel::C3,
            backward_channel: Channel::C4,
        },
    );
    map.insert(
        Motor::Motor4,
        DcChannels {
            ref_channel: Channel::C7,
            forward_channel: Channel::C5,
            backward_channel: Channel::C6,
        },
    );
    map
});

pub struct MotorBoard {
    pwm: Mutex<Pca9685<I2cdev>>,
}

impl MotorBoard {
    pub fn new(i2c_bus: &str, address: u8) -> Self { // Note: Changed from u16 to u8
        let dev = I2cdev::new(i2c_bus).unwrap();
        let mut pwm = Pca9685::new(dev, address).unwrap();
        pwm.set_prescale(100).unwrap();
        pwm.enable().unwrap();

        MotorBoard {
            pwm: Mutex::new(pwm),
        }
    }

    pub fn set_motor_speed(&self, motor: Motor, speed: u16, forward: bool) {
        let channels = DC_CHANNEL_MAP.get(&motor).unwrap();
        let mut pwm = self.pwm.lock().unwrap();

        // Set the reference channel to high
        pwm.set_channel_on(channels.ref_channel, 0).unwrap();
        pwm.set_channel_off(channels.ref_channel, 4095).unwrap();

        if forward {
            // Set the forward channel to speed
            pwm.set_channel_on(channels.forward_channel, 0).unwrap();
            pwm.set_channel_off(channels.forward_channel, speed).unwrap();

            // Set the backward channel to low
            pwm.set_channel_on(channels.backward_channel, 0).unwrap();
            pwm.set_channel_off(channels.backward_channel, 0).unwrap();
        } else {
            // Set the forward channel to low
            pwm.set_channel_on(channels.forward_channel, 0).unwrap();
            pwm.set_channel_off(channels.forward_channel, 0).unwrap();

            // Set the backward channel to speed
            pwm.set_channel_on(channels.backward_channel, 0).unwrap();
            pwm.set_channel_off(channels.backward_channel, speed).unwrap();
        }
    }

    pub fn stop_motor(&self, motor: Motor) {
        let channels = DC_CHANNEL_MAP.get(&motor).unwrap();
        let mut pwm = self.pwm.lock().unwrap();

        // Set the reference channel to low
        pwm.set_channel_on(channels.ref_channel, 0).unwrap();
        pwm.set_channel_off(channels.ref_channel, 0).unwrap();

        // Set the forward and backward channels to low
        pwm.set_channel_on(channels.forward_channel, 0).unwrap();
        pwm.set_channel_off(channels.forward_channel, 0).unwrap();
        pwm.set_channel_on(channels.backward_channel, 0).unwrap();
        pwm.set_channel_off(channels.backward_channel, 0).unwrap();
    }
}
