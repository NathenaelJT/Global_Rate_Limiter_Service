import os
import threading
import time

import requests

# We will read the MS1 URL from environment variables, defaulting to localhost
MS1_URL = os.getenv("MS1_URL", "http://localhost:8001")


def run_client(client_id, num_requests):
    log_file = f"{client_id}_logs.txt"
    print(f"[{client_id}] Starting {num_requests} requests...")

    # Track when the transition happens
    has_exceeded = False

    with open(log_file, "w") as f:
        f.write(f"--- Starting {num_requests} requests for {client_id} ---\n")

        for i in range(1, num_requests + 1):
            payload = {"client_id": client_id, "num1": 10.0, "num2": 5.0}
            try:
                # Alternate between add and subtract
                endpoint = "/add" if i % 2 == 0 else "/subtract"
                response = requests.post(f"{MS1_URL}{endpoint}", json=payload)

                # Check response and log it
                if response.status_code == 200:
                    f.write(f"Request {i}: Allowed - {response.json()}\n")
                elif response.status_code == 403:
                    # HIGHLIGHT THE EXACT TRANSITION MOMENT!
                    if not has_exceeded:
                        f.write("\n" + "=" * 65 + "\n")
                        f.write(
                            " >>> TRANSITION: LIMIT EXCEEDED FOR "
                            f"{client_id.upper()} <<< \n"
                        )
                        f.write("=" * 65 + "\n\n")
                        has_exceeded = True

                    f.write(f"Request {i}: Exceeded - {response.json()}\n")
                else:
                    f.write(
                        f"Req {i}: Err - {response.status_code} - "
                        f"{response.text}\n"
                    )

            except Exception as e:
                f.write(f"Request {i}: Exception - {str(e)}\n")

            # We add a tiny 10-millisecond sleep.
            time.sleep(0.01)

    print(f"[{client_id}] Finished! Logs saved to {log_file}")


if __name__ == "__main__":
    print("Starting all clients...\n")

    # We use threads to run all 3 clients at the exact same time
    t1 = threading.Thread(target=run_client, args=("client_1", 1000))
    t2 = threading.Thread(target=run_client, args=("client_2", 1500))
    t3 = threading.Thread(target=run_client, args=("client_3", 2000))

    t1.start()
    t2.start()
    t3.start()

    # Wait for all of them to finish
    t1.join()
    t2.join()
    t3.join()

    print("\nAll clients finished executing. Check the .txt files!")
