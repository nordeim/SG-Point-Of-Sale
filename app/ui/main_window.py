# File: app/ui/main_window.py
# ... (imports)
from app.ui.views.product_view import ProductView
from app.ui.views.customer_view import CustomerView

class MainWindow(QMainWindow):
    # ... (__init__)
    
        # Create a QStackedWidget to hold the different views
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create instances of our views
        self.product_view = ProductView(self.core)
        self.customer_view = CustomerView(self.core)

        # Add views to the stack
        self.stacked_widget.addWidget(self.product_view)
        self.stacked_widget.addWidget(self.customer_view)

        # Create menu bar to switch between views
        self._create_menu()
        
        # Show the product view by default
        self.stacked_widget.setCurrentWidget(self.product_view)

    def _create_menu(self):
        menu_bar = self.menuBar()
        data_menu = menu_bar.addMenu("&Data Management")

        product_action = data_menu.addAction("Products")
        product_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.product_view))

        customer_action = data_menu.addAction("Customers")
        customer_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.customer_view))
