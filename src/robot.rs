use std::sync::Arc;
use crate::motor::{Motor, MotorBoard};
use tokio::sync::Mutex;
use tokio::time::{sleep, Duration};

pub struct Robot {
    motor_board: Arc<Mutex<MotorBoard>>,
    target_left_speed: Mutex<f32>,
    target_right_speed: Mutex<f32>,
    left_motor_factor: f32,
    right_motor_factor: f32,
}

impl Robot {
    pub fn new(motor_board: Arc<Mutex<MotorBoard>>, left_motor_factor: f32, right_motor_factor: f32) -> Arc<Self> {
        let robot = Arc::new(Robot {
            motor_board,
            target_left_speed: Mutex::new(0.0),
            target_right_speed: Mutex::new(0.0),
            left_motor_factor,
            right_motor_factor,
        });

        // Spawn a task to smoothly adjust motor speeds
        let robot_clone = Arc::clone(&robot);
        tokio::spawn(async move {
            robot_clone.smooth_motor_adjustment().await;
        });

        robot
    }

    pub async fn drive(&self, left: f32, right: f32) {
        let mut target_left_speed = self.target_left_speed.lock().await;
        let mut target_right_speed = self.target_right_speed.lock().await;

        *target_left_speed = left * self.left_motor_factor;
        *target_right_speed = right * self.right_motor_factor;
    }

    pub async fn stop(&self) {
        let mut target_left_speed = self.target_left_speed.lock().await;
        let mut target_right_speed = self.target_right_speed.lock().await;

        *target_left_speed = 0.0;
        *target_right_speed = 0.0;
    }

    async fn smooth_motor_adjustment(self: Arc<Self>) {
        const ADJUSTMENT_STEP: f32 = 0.1;
        const INTERVAL: Duration = Duration::from_millis(10);

        let mut current_left_speed = 0.0;
        let mut current_right_speed = 0.0;

        loop {
            let target_left_speed = *self.target_left_speed.lock().await;
            let target_right_speed = *self.target_right_speed.lock().await;

            if (current_left_speed - target_left_speed).abs() > ADJUSTMENT_STEP {
                if current_left_speed < target_left_speed {
                    current_left_speed += ADJUSTMENT_STEP;
                } else {
                    current_left_speed -= ADJUSTMENT_STEP;
                }
            } else {
                current_left_speed = target_left_speed;
            }

            if (current_right_speed - target_right_speed).abs() > ADJUSTMENT_STEP {
                if current_right_speed < target_right_speed {
                    current_right_speed += ADJUSTMENT_STEP;
                } else {
                    current_right_speed -= ADJUSTMENT_STEP;
                }
            } else {
                current_right_speed = target_right_speed;
            }

            let left_pwm = (current_left_speed.abs() * 4095.0).round() as u16;
            let right_pwm = (current_right_speed.abs() * 4095.0).round() as u16;

            let motor_board = self.motor_board.lock().await;

            if current_left_speed > 0.0 {
                motor_board.set_motor_speed(Motor::Motor1, left_pwm, true);
            } else if current_left_speed < 0.0 {
                motor_board.set_motor_speed(Motor::Motor1, left_pwm, false);
            } else {
                motor_board.stop_motor(Motor::Motor1);
            }

            if current_right_speed > 0.0 {
                motor_board.set_motor_speed(Motor::Motor2, right_pwm, true);
            } else if current_right_speed < 0.0 {
                motor_board.set_motor_speed(Motor::Motor2, right_pwm, false);
            } else {
                motor_board.stop_motor(Motor::Motor2);
            }

            sleep(INTERVAL).await;
        }
    }
}
