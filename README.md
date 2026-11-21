# ATM Simulation

A desktop ATM simulator built with Python and Tkinter. Accounts are stored in a singly linked list, and a flash drive acts as the ATM card.

Rhon Jacob B. Ramos | BSIS-2B

## Features

- **Register** a new account through a step-by-step form (name, birthday, contact number, initial deposit, PIN)
- **Flash drive as ATM card:** a `pin.code` file is saved to the drive on registration (30-second wait before returning to the menu)
- **Login** with full name, account number, and PIN
- **Transactions:** balance inquiry, withdraw, deposit, fund transfer, change PIN, and mobile top-up (SMART, GLOBE, DITO, GOMO, TNT, TM)

## Rules

- Account numbers start at 10001
- Initial deposit: PHP 5,000 to PHP 500,000
- Cash deposits must be in multiples of PHP 50, up to PHP 500,000
- PIN is 4 to 6 digits (stored encrypted by shifting each digit by 3)
- Contact number is 11 digits and starts with `09`

## Requirements

- Python 3.8+
- Tkinter (included with most Python installs)
- Windows is recommended for automatic flash drive detection. On other systems, use the **Browse folder...** button.

## How to Run

```bash
python atm.py
```

## Notes

- Data is kept in memory only, so all accounts are lost when the program closes.
- Press **Esc** in any dialog to cancel.

## Concepts Used

Python, GUI (Tkinter), Data Structures and Algorithms (linked list)
