<img width="1449" alt="image" src="https://github.com/user-attachments/assets/2c88f095-63d3-47b4-87e1-b0c4c5958bed" /># Indoor Plant Store

A Django-based e-commerce platform for buying and selling indoor plants. This project is designed to help plant enthusiasts and small businesses easily manage and explore a curated collection of indoor plants—with a clean interface and seamless payment integration via Stripe.

**Live Demo:** [indoorplant.store](https://indoor-plant-wg6fd2fkaa-uc.a.run.app)

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Features

- **User Authentication:** Secure registration and login system.
- **Product Catalog:** Browse, search, and filter indoor plants.
- **Shopping Cart:** Easily add/remove products and proceed to checkout.
- **Stripe Integration:** Secure and smooth payment processing.
- **Admin Panel:** Manage plant listings, orders, and inventory.
- **Responsive Design:** Optimized for both desktop and mobile devices.

---

## Tech Stack

- ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
- ![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)
- ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)
- ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3)
- ![Stripe](https://img.shields.io/badge/Stripe-008CDD?style=flat&logo=stripe)
- ![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)

---

## Prerequisites

- **Python 3.6+**
- **pip** (Python package installer)
- **Django** (Installed via pip)
- A Stripe account for payment integration (for testing and production)

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/nebullii/Indoor-Plant.git
   cd Indoor-Plant
   ```

2. Set up a virtual environment (recommended):

   ```bash
   python -m venv myenv
   ```

3. Activate the virtual environment:

   - On macOS/Linux:

     ```bash
     source myenv/bin/activate
     ```

   - On Windows:

     ```bash
     myenv\Scripts\activate
     ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Apply migrations:

   ```bash
   python manage.py migrate
   ```

6. Run the development server:

   ```bash
   python manage.py runserver
   ```

7. Open your browser and visit:

   [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## Usage

- **User Signup/Login:** Create an account to start shopping.
- **Browse Plants:** View detailed pages for each plant with descriptions and prices.
- **Add to Cart & Checkout:** Add products to your cart and proceed to a secure Stripe-powered checkout.
- **Admin Features:** Use the built-in admin panel (accessible at `/admin`) to manage product listings and view orders.
- **Live Demo:** Check out the hosted version [here](https://nevus.pythonanywhere.com/).

---

## Screenshots

**Homepage Banner:**

![Homepage Banner](https://github.com/user-attachments/assets/4a4f4ac6-b067-4730-982c-401d2063f2c5)

**Product Showcase:**

![Product Showcase](https://github.com/user-attachments/assets/893dad0b-47ea-45a6-b5b3-014eaeb8a13d)

**Product View:**

![Product View](https://github.com/user-attachments/assets/4a426b04-317d-4f90-82f3-3405060fa4c4)

**Seller Dashboard:**

![Seller Dashboard](https://github.com/user-attachments/assets/eba70b59-6dde-4ded-933b-a1f3be68cee8)

**Seller Products:**

![Seller Products](https://github.com/user-attachments/assets/b5740c00-3f16-4f97-a14c-07f036f749f1)


**Cart View:**

![Cart View](https://github.com/user-attachments/assets/94da07a1-ac60-4c4d-924b-345792f18ec7)

**Payment Page:**

![Payment Page](https://github.com/user-attachments/assets/e29c3219-4a64-468a-8c6e-b26660da7621)


---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some feature'`)
5. Push to the branch (`git push origin feature/your-feature`)
6. Open a Pull Request

Feel free to submit issues for any bugs or feature requests.
