def human_gate(agent_name):
    """
    Presents the Human-In-The-Loop gate to the user after an agent runs.
    Returns a tuple (action, correction)
    action can be: 'A', 'E', 'R', 'Q'
    correction is a string or None.
    """
    print("\nHuman Gate Menu:")
    print("[A] Approve and continue")
    print("[E] Edit (provide correction and rerun)")
    print("[R] Regenerate (rerun with no changes)")
    print("[Q] Quit and save progress")
    
    while True:
        choice = input("\nSelect action [A/E/R/Q]: ").strip().upper()

        if choice == 'A':
            return 'A', None
        elif choice == 'E':
            note = input("Enter your correction: ").strip()
            return 'E', note
        elif choice == 'R':
            return 'R', None
        elif choice == 'Q':
            return 'Q', None
        else:
            print("Invalid choice. Please select A, E, R, or Q.")
