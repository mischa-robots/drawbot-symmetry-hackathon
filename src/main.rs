mod motor;
mod robot;
mod robot_web_control;

use crate::motor::MotorBoard;
use crate::robot::Robot;
use robot_web_control::{robot_ws, drive_robot};

use actix_files::Files;
use actix_files::NamedFile;
use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use std::sync::Arc;
use std::path::PathBuf;
use tokio::sync::Mutex;

async fn health_check() -> impl Responder {
    HttpResponse::Ok().body("Healthy")
}

async fn index() -> actix_web::Result<NamedFile> {
    let path: PathBuf = "./static/index.html".parse().unwrap();
    Ok(NamedFile::open(path)?)
}

#[tokio::main]
async fn main() -> std::io::Result<()> {

    let motor_board = Arc::new(Mutex::new(MotorBoard::new("/dev/i2c-1", 0x60)));
    let robot = Robot::new(motor_board.clone(), -1.0, 1.0);

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(robot.clone()))
            .route("/health", web::get().to(health_check))
            .route("/drive", web::get().to(drive_robot))
            .route("/", web::get().to(index))
            .route("/ws", web::get().to(robot_ws))
            .service(Files::new("/static", "./static").show_files_listing())
    })
    .bind("0.0.0.0:8000")?
    .run()
    .await
}
