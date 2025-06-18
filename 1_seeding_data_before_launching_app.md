### **Instructions for Use**

To resolve the "Company not found" error, you must now run this seeding script **one time** after setting up the database. The new, complete deployment process is:

1.  Follow the `Deployment Guide.md` up to and including **Step 10 (Running Migrations)**.
2.  **Run the Seeding Script:** Before launching the application for the first time, execute the following command from your activated Poetry shell (`poetry shell`) in the project root:
    ```bash
    python scripts/database/seed_data.py
    ```
3.  **Launch the Application:** Now, run the application as before.
    ```bash
    python app/main.py
    ```

The application will now start without the "Company not found" error, as the required data now exists in the database. The `Settings` view will load and display the default company information.

---
https://drive.google.com/file/d/1KFlIqHBgTgyDFbHrm9QAt-PqyNei9OyH/view?usp=sharing, https://drive.google.com/file/d/1T2k1YO289bI0i4AX1Vxfxr6OaQGpYHAb/view?usp=sharing, https://drive.google.com/file/d/1dnSP22Pzt3sjhTNHJcPpvKoihYG-somP/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221fo0QcoydHcYD6h_b6-9HapceFSj7xnKT%22%5D,%22action%22:%22open%22,%22userId%22:%22108686197475781557359%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1koyl7FAKLkppdi5iIUCwrJtbPLgb6YGM/view?usp=sharing

