# Joblet - Django
## First TPW Project
## Grade Given: 19/20

### What is Joblet?
Joblet refers to the small, on-demand tasks or gigs that users can post or apply for. These joblets are intended to be quick, simple tasks that providers can complete, offering flexibility and convenience to both service providers and customers.

### Team
Here is the team involved in the development of Joblet. Click on the GitHub profiles for more information:

| **Número Mecanográfico** | **Nome**          | **Email**                  | **GitHub Profile**                                                                 |
|---------------------------|-------------------|----------------------------|------------------------------------------------------------------------------------|
| 114614                    | Martim Santos    | santos.martim@ua.pt       | [GitHub Profile](https://github.com/martimsoutooo)                                |
| 113889                    | Hugo Castro      | hugocastro@ua.pt          | [GitHub Profile](https://github.com/hujuc)                                  |
| 113786                    | Gabriel Silva    | gabrielmsilva4@ua.pt      | [GitHub Profile](https://github.com/GabrielMSilva04)                                |


### Tools:
The project is developed using the following technologies:
- **Django**: A high-level Python web framework that encourages rapid development and clean, pragmatic design.
- **Python**: A programming language that lets you work quickly and integrate systems more effectively.
- **HTML/CSS/JS**: The standard web development technologies.
- **tailwindcss/DaisyUI**: A utility-first CSS framework for rapidly building custom designs.

### How to Run:
To run this project, you need to have Python and Django installed. Here are the steps to get it up and running:

#### 1. Clone the Repository
```bash
git clone <repository_url>
```

#### 2. Open a terminal and navigate to the project's root directory
```bash
cd Joblet
```
   
#### 3. Create a virtual environment by running
```bash
python -m venv venv
```

#### 4. Activate the virtual environment by running
- Linux/MacOS
```bash
source venv/bin/activate
```
- Windows
```powershell
venv\Scripts\activate
```

#### 5. Install the required dependencies by running
```bash
pip install -r requirements.txt
```

#### 6. Create and Configure .env File
- In the root directory, create a .env file:
```bash
touch .env
```
- Generate a secure Django SECRET_KEY using the following Python code:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
- Copy the output and use it as your SECRET_KEY.
- Add the following content to the .env file and customize it:
```makefile
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### 7. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 8. Create a Superuser (Admin Account)
```bash
python manage.py createsuperuser
```

#### 9. Populate the Database (Optional)
- If there’s a script to populate the database (e.g., populate_db.py):
```bash
python manage.py runscript populate_db
```

#### 10. Run the server by executing
- Default Port (8000):
```bash
python manage.py runserver
```
- Custom Port:
```bash
python manage.py runserver {yourport}
```

#### 11. Open a browser and navigate to `http://localhost:{yourport}`
#### 12. Enjoy!

### Deployment
The Joblet application is deployed on PythonAnywhere and can be accessed at:

👉 **[Joblet Deployment](https://joblet.pythonanywhere.com/)**

To deploy the application locally or on a cloud provider, ensure you configure the environment variables and database settings accordingly, as mentioned in the setup guide above.

---
