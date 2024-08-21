# Use the Nvidia Docker image as the base
FROM dustynv/onnxruntime:r32.7.1

# Install Rust
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    pkg-config \
    libssl-dev \
    && curl https://sh.rustup.rs -sSf | sh -s -- -y \
    && . $HOME/.cargo/env \
    && cargo install cargo-watch \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Rust
ENV PATH=/root/.cargo/bin:$PATH

# Copy the robot control code into the Docker container
WORKDIR /app

# Copy only the Cargo.toml and Cargo.lock to the working directory
COPY Cargo.toml Cargo.lock ./

# This build step will cache dependencies
RUN mkdir src \
    && echo "fn main() { println!(\"Hello, world!\"); }" > src/main.rs \
    && cargo build

# Copy the rest of the application code
COPY . .

# Set the entry point for the container
CMD ["cargo", "watch", "-x", "run"]
