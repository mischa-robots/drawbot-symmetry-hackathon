use actix::prelude::*;
use actix_web::{web, HttpRequest, HttpResponse, Responder};
use actix_web_actors::ws;
use serde::Deserialize;
use serde_json;
use std::sync::Arc;
use crate::robot::Robot;

pub struct RobotControl {
    robot: Arc<Robot>,
}

impl RobotControl {
    pub fn new(robot: Arc<Robot>) -> Self {
        Self { robot }
    }
}

impl Actor for RobotControl {
    type Context = ws::WebsocketContext<Self>;

    fn stopped(&mut self, _ctx: &mut Self::Context) {
        let robot = self.robot.clone();
        actix_rt::spawn(async move {
            robot.stop().await;
        });
    }
}

#[derive(Deserialize)]
pub struct DriveParams {
    left: f32,
    right: f32,
}

impl StreamHandler<Result<ws::Message, ws::ProtocolError>> for RobotControl {
    fn handle(&mut self, msg: Result<ws::Message, ws::ProtocolError>, ctx: &mut Self::Context) {
        match msg {
            Ok(ws::Message::Text(text)) => {
                if let Ok(control_msg) = serde_json::from_str::<DriveParams>(&text) {
                    let robot = self.robot.clone();
                    actix_rt::spawn(async move {
                        robot.drive(control_msg.left, control_msg.right).await;
                    });
                }
            }
            Ok(ws::Message::Binary(bin)) => ctx.binary(bin),
            Ok(ws::Message::Close(_reason)) => {
                let robot = self.robot.clone();
                actix_rt::spawn(async move {
                    robot.stop().await;
                });
                ctx.stop(); // Close the WebSocket connection
            }
            _ => (),
        }
    }
}

pub async fn robot_ws(
    req: HttpRequest,
    stream: web::Payload,
    robot: web::Data<Arc<Robot>>,
) -> Result<HttpResponse, actix_web::Error> {
    let robot_control = RobotControl::new(robot.get_ref().clone());
    let res = ws::start(robot_control, &req, stream)?;
    Ok(res)
}

pub async fn drive_robot(robot: web::Data<Arc<Robot>>, params: web::Query<DriveParams>) -> impl Responder {
    let left = params.left;
    let right = params.right;
    robot.drive(left, right).await;
    HttpResponse::Ok().body("Driving")
}
