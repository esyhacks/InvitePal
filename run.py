import asyncio
import logging

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

shutdown_event = asyncio.Event()

async def run_script(script_name):
    """Run a Python script asynchronously and restart it on failure."""
    while not shutdown_event.is_set():
        logging.info(f"Starting {script_name}...")

        process = await asyncio.create_subprocess_exec(
            "python", script_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        async def log_output(stream, prefix):
            """Log output from the script's stdout and stderr."""
            while not shutdown_event.is_set():
                line = await stream.readline()
                if not line:
                    break
                logging.info(f"[{prefix}] {line.decode().strip()}")

        try:
            # Log both stdout and stderr
            await asyncio.gather(
                log_output(process.stdout, script_name),
                log_output(process.stderr, script_name),
            )
            return_code = await process.wait()
            if return_code == 0:
                logging.info(f"{script_name} exited successfully.")
                break
            else:
                logging.error(f"{script_name} exited with code {return_code}. Restarting...")
        except asyncio.CancelledError:
            logging.info(f"Terminating {script_name}...")
            process.terminate()
            await process.wait()
            break

async def main():
    """Run all scripts concurrently."""

    tasks = [
        asyncio.create_task(run_script("server.py")),
        asyncio.create_task(run_script("RefBot.py")),
        asyncio.create_task(run_script("keepalive.py")),
    ]

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logging.info("Shutdown requested. Cancelling tasks...")
        shutdown_event.set()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        logging.info("All scripts terminated.")

if __name__ == "__main__":
    try:
        logging.info("Starting the event loop...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program interrupted by user. Shutting down gracefully...")
        shutdown_event.set()
