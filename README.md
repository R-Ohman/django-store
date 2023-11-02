# Django E-Commerce Project

## Table of contents
- [General info](#general-info)
- [Technologies Used](#technologies-used)
- [Project Functionality](#project-functionality)
- [Acknowledgments](#acknowledgments)

## General info

Welcome to the Django E-Commerce project! This web application is designed for online shopping and includes a wide range of features to provide a seamless user experience.

## Technologies Used

The project leverages various technologies, including:
- Django (v3.2.19)
- Celery (asynchronous tasks)
- Internationalization and Localization (i18n)
- OAuth (social media login)
- PayPal sandbox
- Fetch API (asynchronous data retrieval)
- jQuery AJAX
- Bootstrap

## Project Functionality

#### 1. Main Pages
- Home
- Catalog
- Profile
- Orders
- Contact

#### 2. Authentication
- Login
- Registration
- Password reset via email
- Social media login
- Email confirmation

#### 3. Profile
- Shopping cart
- Wishlist
- Product availability tracking (sends email notifications)

#### 4. Orders
- Email receipts
- Order viewing
- Product returns within 15 days (with email confirmation)

#### 5. Payment
- PayPal integration
- Payment timeout (30 minutes)
- Order cancellation for non-payment (user notified via email)

#### 6. Catalog
- Product categories
- Sorting
- Price filtering
- Search by product name
- Pagination
- Image carousels

#### 7. Product
- Ratings
- Comments
- Discounts
- Add to wishlist, cart, or tracking
- Image carousels

#### 8. Comments
- Image carousels
- Deletion
- Pagination
- Rating (like/dislike)
- Posting limits (5 times, only if the product was purchased)

#### 9. Internationalization
- Language selection (uk, en, pl)
- Content translation (including emails)
- Currency conversion (UAH, USD, PLN) based on the chosen language

#### 10. Asynchronous/scheduled tasks
- Email inactive users (3+ days) with top 3 discounted products
- Email admin a list of recently sold-out products
- Clear expired discounts
- Cancel unpaid orders

#### 11. Responsiveness
The project is designed to be responsive and work seamlessly on different screen sizes.

#### 12. User-Friendly Admin Panel
The Django admin panel provides convenient access for site administration.


## Acknowledgments

Special thanks to the [@stefanfoulis](https://github.com/stefanfoulis/django-phonenumber-field), author of the `phonenumber_field` application, for his contribution to this project.

Feel free to explore the code and contribute to this open-source project!
