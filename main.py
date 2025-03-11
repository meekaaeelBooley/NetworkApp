import os

# --------------------------
# Main Function
# --------------------------
def main():
    print("Welcome to the P2P File Sharing System!")
    print("Choose a role:")
    print("1. Tracker")
    print("2. Seeder")
    print("3. Leecher")
    choice = input("Enter your choice (1/2/3): ")

    if choice == "1":
        run_tracker() 
    elif choice == "2":
        run_seeder() 
    elif choice == "3":
        run_leecher() 
    else:
        print("Invalid choice. Exiting.")

# --------------------------
# Tracker Logic
# --------------------------
def run_tracker():
    print("Starting tracker...")
    os.system("python3 tracker.py")

# --------------------------
# Seeder Logic
# --------------------------
def run_seeder():
    print("Starting seeder...")
    os.system("python3 seeder.py")

# --------------------------
# Leecher Logic
# --------------------------
def run_leecher():
    print("Starting leecher...")
    os.system("python3 leecher.py")

    # Prompt for re-seeding
    reseed = input("Do you want to support seeding for this file? (y/n): ")
    if reseed.lower() == "y":
        print("Transitioning to seeder mode...")
        run_seeder()  # Start the seeder after download

# --------------------------
# Entry Point
# --------------------------
if __name__ == "__main__":
    main()