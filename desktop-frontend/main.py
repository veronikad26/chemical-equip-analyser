import sys
import os
from PyQt5.QtWidgets import QApplication
from auth_window import AuthWindow

def main():
    app = QApplication(sys.argv)

    # Check for token (similar to localStorage)
    token = None
    if os.path.exists('token.txt'):
        with open('token.txt', 'r') as f:
            token = f.read().strip()

    if token:
        # If token exists, go directly to dashboard
        from dashboard_window import DashboardWindow
        window = DashboardWindow(token)
    else:
        # Show auth window
        window = AuthWindow()

    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()