import os

# --------------------------
# Main Function
# --------------------------
def main():
    print("Welcome to the P2P mini BitTorrent!")
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
        print("Invalid choice. Exiting...")

# --------------------------
# Tracker
# --------------------------
def run_tracker():
    print("Starting tracker...")
    os.system("python tracker.py")

# --------------------------
# Seeder
# --------------------------
def run_seeder():
    print("Starting seeder...")
    os.system("python seeder.py")

# --------------------------
# Leecher
# --------------------------
def run_leecher():
    print("Starting leecher...")
    os.system("python leecher.py")

    # Prompt for re-seeding
    reseed = input("Do you want to support seeding for this file? (y/n): ")
    if reseed.lower() == "y":
        print("Transitioning to a seeder...")
        run_seeder()  # Re-seed after download

# --------------------------
# Entry Point
# --------------------------
if __name__ == "__main__":
    main()