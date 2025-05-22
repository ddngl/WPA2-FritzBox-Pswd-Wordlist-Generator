import os
import multiprocessing

output_dir = "wlist_parallel"
output_file = os.path.join(output_dir, "fritz_final.txt")
max_length = 20
buffer_size = 10000
digits = "0123456789"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def build_numbers(prefix, last_digit, repeat_count, buffer, counter, lock):
    if len(prefix) == max_length:
        buffer.append(prefix)
        counter[0] += 1
        if len(buffer) >= buffer_size:
            write_buffer(buffer, lock)
            buffer.clear()
        return

    for d in digits:
        if d == last_digit:
            if repeat_count == 2:
                continue
            build_numbers(prefix + d, d, repeat_count + 1, buffer, counter, lock)
        else:
            build_numbers(prefix + d, d, 1, buffer, counter, lock)

def write_buffer(buffer, lock):
    with lock:
        with open(output_file, "a") as f:
            f.write("\n".join(buffer) + "\n")

def worker(start_digit, lock):
    print(f"[PROC {start_digit}] Start generare...")
    buffer = []
    counter = [0]
    build_numbers(start_digit, start_digit, 1, buffer, counter, lock)
    if buffer:
        write_buffer(buffer, lock)
    print(f"[PROC {start_digit}] Finalizat. Total: {counter[0]} numere.")

if __name__ == "__main__":
    cpu_count = multiprocessing.cpu_count()
    print(f"Detectat {cpu_count} core-uri. Lansăm paralelizare...")

    start_digits = digits[1:]  # evităm prefixe care încep cu 0
    manager = multiprocessing.Manager()
    lock = manager.Lock()

    # Șterge fișierul final dacă există
    if os.path.exists(output_file):
        os.remove(output_file)

    with multiprocessing.Pool(len(start_digits)) as pool:
        pool.starmap(worker, [(digit, lock) for digit in start_digits])

    print("✅ Generarea paralelă s-a încheiat. Ieșire salvată în:", output_file)
